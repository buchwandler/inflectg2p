from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..errors import LexiconDependencyError, LexiconResourceError
from ..types import LexiconPronunciation, LexiconProvenance
from .base import normalize_phoneme_encoding


class G2LexLookup:
    """Lazy exact-key lookup over explicitly supplied local G2Lex assets."""

    def __init__(self, paths: Sequence[str | Path], *, language: str | None = None) -> None:
        self.paths = tuple(Path(path) for path in paths)
        self.language = language
        self._assets: tuple[Any, ...] | None = None
        self._provenance: tuple[LexiconProvenance, ...] = ()
        self._closed = False
        if not self.paths:
            raise LexiconResourceError("At least one local G2Lex path is required.")

    @staticmethod
    def _metadata(asset: Any) -> dict[str, Any]:
        metadata = getattr(asset, "metadata", None)
        if not isinstance(metadata, dict):
            raise LexiconResourceError("G2Lex metadata is not an object.")
        return metadata

    @staticmethod
    def _metadata_value(metadata: dict[str, Any], *keys: str) -> Any:
        source = metadata.get("source")
        sources = (source,) if isinstance(source, dict) else ()
        for key in keys:
            if metadata.get(key) is not None:
                return metadata[key]
            for source_metadata in sources:
                if source_metadata.get(key) is not None:
                    return source_metadata[key]
        return None

    def _validate_asset(self, asset: Any, path: Path) -> LexiconProvenance:
        metadata = self._metadata(asset)
        declared_language = self._metadata_value(metadata, "language", "locale")
        if self.language and declared_language:
            expected = self.language.casefold().replace("_", "-")
            declared = str(declared_language).casefold().replace("_", "-")
            if not declared.startswith(expected):
                raise LexiconResourceError(
                    f"G2Lex asset {str(path)!r} declares language {declared_language!r}, "
                    f"not requested {self.language!r}"
                )
        kind = self._metadata_value(metadata, "kind")
        if kind is not None and str(kind).casefold() != "pronunciation":
            raise LexiconResourceError(f"G2Lex asset {str(path)!r} has unsupported kind {kind!r}.")
        raw_encoding = self._metadata_value(
            metadata,
            "phoneme_encoding",
            "pronunciation_alphabet",
            "alphabet",
        )
        try:
            source_encoding = normalize_phoneme_encoding(raw_encoding)
        except ValueError as exc:
            raise LexiconResourceError(
                f"G2Lex asset {str(path)!r} uses unsupported pronunciation encoding "
                f"{raw_encoding!r}."
            ) from exc
        return LexiconProvenance(
            lexicon_id=str(self._metadata_value(metadata, "id", "lexicon_id") or path),
            language=str(declared_language) if declared_language is not None else None,
            source_encoding=source_encoding,
            data_version=self._optional_string(
                self._metadata_value(metadata, "data_version", "version")
            ),
            asset_path=str(path),
        )

    @staticmethod
    def _optional_string(value: object | None) -> str | None:
        return None if value is None else str(value)

    def _ensure_assets(self) -> tuple[Any, ...]:
        if self._closed:
            raise LexiconResourceError("G2Lex lookup adapter is closed.")
        if self._assets is not None:
            return self._assets
        for path in self.paths:
            if not path.is_file():
                raise LexiconResourceError(f"G2Lex asset does not exist: {path}")
        try:
            import g2lex
        except ImportError as exc:
            raise LexiconDependencyError(
                'Direct G2Lex support requires the optional extra. Install "inflectg2p[g2lex]".'
            ) from exc

        assets: list[Any] = []
        provenance: list[LexiconProvenance] = []
        try:
            for path in self.paths:
                asset = g2lex.open(path)
                assets.append(asset)
                provenance.append(self._validate_asset(asset, path))
        except LexiconResourceError:
            for asset in assets:
                asset.close()
            raise
        except Exception as exc:
            for asset in assets:
                asset.close()
            raise LexiconResourceError("Could not open configured G2Lex asset.") from exc
        self._assets = tuple(assets)
        self._provenance = tuple(provenance)
        return self._assets

    def lookup(self, word: str, *, tag: str | None = None) -> LexiconPronunciation | None:
        assets = self._ensure_assets()
        try:
            for asset, path, provenance in zip(assets, self.paths, self._provenance, strict=True):
                value = asset.lookup(word, tag=tag)
                if value is not None:
                    return LexiconPronunciation(
                        pronunciation=str(value),
                        source=f"g2lex:{path}",
                        lexicon_id=provenance.lexicon_id,
                        matched_key=word,
                        source_encoding=provenance.source_encoding,
                        provenance=provenance,
                    )
        except Exception as exc:
            if isinstance(exc, LexiconResourceError):
                raise
            raise LexiconResourceError(f"G2Lex lookup failed for {word!r}.") from exc
        return None

    def lookup_many(
        self,
        words: Sequence[str],
        *,
        tag: str | None = None,
    ) -> tuple[LexiconPronunciation | None, ...]:
        return tuple(self.lookup(word, tag=tag) for word in words)

    def close(self) -> None:
        if self._assets is not None:
            for asset in self._assets:
                asset.close()
        self._assets = None
        self._closed = True

    def __enter__(self) -> G2LexLookup:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
