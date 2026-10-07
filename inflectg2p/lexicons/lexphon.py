from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..errors import LexiconDependencyError, LexiconResourceError
from ..types import LexiconPronunciation, LexiconProvenance
from .base import normalize_phoneme_encoding
from .g2lex import G2LexLookup


class LexphonLookup:
    """Lookup explicitly provisioned Lexphon assets without installing data."""

    def __init__(
        self,
        language: str,
        identifiers: Sequence[str],
        *,
        store: Any = None,
    ) -> None:
        self.language = language
        self.identifiers = tuple(identifiers)
        self.store = store
        self._lookup: G2LexLookup | None = None
        self._paths: tuple[Path, ...] = ()
        self._provenance: tuple[LexiconProvenance, ...] = ()
        self._closed = False
        if not self.identifiers:
            raise LexiconResourceError("At least one Lexphon identifier is required.")

    @staticmethod
    def _validate_metadata(
        identifier: str,
        language: str,
        metadata: dict[str, Any],
        asset_path: Path,
    ) -> LexiconProvenance:
        kind = metadata.get("kind")
        if str(kind).casefold() != "pronunciation":
            raise LexiconResourceError(
                f"Lexphon asset {identifier!r} has unsupported kind {kind!r}."
            )
        declared_language = metadata.get("language") or metadata.get("locale")
        if not declared_language:
            raise LexiconResourceError(f"Lexphon asset {identifier!r} has no language metadata.")
        expected = language.casefold().replace("_", "-")
        declared = str(declared_language).casefold().replace("_", "-")
        if not declared.startswith(expected):
            raise LexiconResourceError(
                f"Lexphon asset {identifier!r} declares language {declared_language!r}, "
                f"not requested {language!r}"
            )
        raw_encoding = metadata.get("phoneme_encoding") or metadata.get("pronunciation_alphabet")
        try:
            source_encoding = normalize_phoneme_encoding(raw_encoding)
        except ValueError as exc:
            raise LexiconResourceError(
                f"Lexphon asset {identifier!r} uses unsupported pronunciation encoding "
                f"{raw_encoding!r}."
            ) from exc
        data_version = metadata.get("data_version") or metadata.get("version")
        return LexiconProvenance(
            lexicon_id=identifier,
            language=str(declared_language),
            source_encoding=source_encoding,
            data_version=str(data_version) if data_version is not None else None,
            asset_path=str(asset_path),
        )

    def _ensure_lookup(self) -> G2LexLookup:
        if self._closed:
            raise LexiconResourceError("Lexphon lookup adapter is closed.")
        if self._lookup is not None:
            return self._lookup
        try:
            import lexphon
        except ImportError as exc:
            raise LexiconDependencyError(
                'Lexphon support requires the optional extra. Install "inflectg2p[lexphon]".'
            ) from exc

        try:
            store = self.store if self.store is not None else lexphon.DataStore()
            paths: list[Path] = []
            provenance: list[LexiconProvenance] = []
            for identifier in self.identifiers:
                metadata = store.metadata(identifier)
                if not isinstance(metadata, dict):
                    raise LexiconResourceError(
                        f"Lexphon metadata for {identifier!r} is not an object."
                    )
                asset_path = Path(store.path(identifier))
                if not asset_path.is_file():
                    raise LexiconResourceError(f"Lexphon asset file does not exist: {asset_path}")
                paths.append(asset_path)
                provenance.append(
                    self._validate_metadata(identifier, self.language, metadata, asset_path)
                )
            lookup = G2LexLookup(paths, language=self.language)
        except LexiconResourceError:
            raise
        except Exception as exc:
            identifiers = ", ".join(self.identifiers)
            raise LexiconResourceError(
                f"Could not resolve installed Lexphon lexicon(s): {identifiers}."
            ) from exc
        self._paths = tuple(paths)
        self._provenance = tuple(provenance)
        self._lookup = lookup
        return lookup

    def lookup(self, word: str, *, tag: str | None = None) -> LexiconPronunciation | None:
        lookup = self._ensure_lookup()
        try:
            result = lookup.lookup(word, tag=tag)
        except LexiconResourceError:
            raise
        except Exception as exc:
            raise LexiconResourceError(f"Lexphon lookup failed for {word!r}.") from exc
        if result is None:
            return None
        index = next(
            (i for i, path in enumerate(self._paths) if result.source == f"g2lex:{path}"),
            None,
        )
        if index is None:
            raise LexiconResourceError("Lexphon lookup returned unknown asset provenance.")
        provenance = self._provenance[index]
        return LexiconPronunciation(
            pronunciation=result.pronunciation,
            source=f"lexphon:{self.identifiers[index]}",
            lexicon_id=self.identifiers[index],
            matched_key=result.matched_key or word,
            source_encoding=provenance.source_encoding,
            provenance=provenance,
        )

    def lookup_many(
        self,
        words: Sequence[str],
        *,
        tag: str | None = None,
    ) -> tuple[LexiconPronunciation | None, ...]:
        return tuple(self.lookup(word, tag=tag) for word in words)

    def close(self) -> None:
        if not self._closed and self._lookup is not None:
            self._lookup.close()
        self._closed = True

    def __enter__(self) -> LexphonLookup:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
