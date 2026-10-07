from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Any

from ..errors import LexiconDependencyError, LexiconResourceError
from ..types import LexiconPronunciation
from .base import PronunciationLookup, normalize_phoneme_encoding
from .g2lex import G2LexLookup
from .lexphon import LexphonLookup


def _store(store: Any = None) -> Any:
    if store is not None:
        return store
    try:
        import lexphon
    except ImportError as exc:
        raise LexiconDependencyError(
            'Lexicon discovery requires the optional extra. Install "inflectg2p[lexphon]".'
        ) from exc
    return lexphon.DataStore()


def _metadata_items(store: Any) -> list[dict[str, Any]]:
    try:
        values = store.installed()
    except Exception as exc:
        raise LexiconResourceError("Could not inspect installed Lexphon assets.") from exc
    if not isinstance(values, Sequence):
        raise LexiconResourceError("Lexphon installed-asset metadata is invalid.")
    return [dict(value) for value in values if isinstance(value, dict)]


def _matches_language(metadata: dict[str, Any], language: str) -> bool:
    declared = metadata.get("language") or metadata.get("locale")
    if declared is None:
        return False
    return (
        str(declared).casefold().replace("_", "-").startswith(language.casefold().replace("_", "-"))
    )


def _is_pronunciation(metadata: dict[str, Any]) -> bool:
    return str(metadata.get("kind", "")).casefold() == "pronunciation"


def _short_name(metadata: dict[str, Any]) -> str:
    identifier = str(metadata.get("id", metadata.get("lexicon_id", "")))
    return identifier.rsplit(":", 1)[-1]


def available_lexicons(language: str, *, store: Any = None) -> tuple[str, ...]:
    """Return installed pronunciation asset names for a language."""
    values = {
        _short_name(metadata)
        for metadata in _metadata_items(_store(store))
        if _is_pronunciation(metadata) and _matches_language(metadata, language)
    }
    return tuple(sorted(values))


def lexicon_info(language: str, name: str, *, store: Any = None) -> Any:
    """Return read-only metadata for an installed pronunciation asset."""
    data_store = _store(store)
    candidates = [
        metadata
        for metadata in _metadata_items(data_store)
        if _is_pronunciation(metadata)
        and _matches_language(metadata, language)
        and (
            str(metadata.get("id", metadata.get("lexicon_id", ""))) == name
            or _short_name(metadata) == name
        )
    ]
    if not candidates:
        raise LexiconResourceError(f"Lexicon {name!r} is not installed for {language!r}.")
    metadata = candidates[0]
    identifier = str(metadata.get("id", metadata.get("lexicon_id", name)))
    try:
        asset_path = str(data_store.path(identifier))
    except Exception as exc:
        raise LexiconResourceError(f"Could not resolve installed lexicon {identifier!r}.") from exc
    try:
        encoding = normalize_phoneme_encoding(
            metadata.get("phoneme_encoding") or metadata.get("pronunciation_alphabet")
        )
    except ValueError as exc:
        raise LexiconResourceError(
            f"Lexicon {identifier!r} has an unsupported pronunciation encoding."
        ) from exc
    info = {
        "id": identifier,
        "language": metadata.get("language", metadata.get("locale", language)),
        "kind": metadata["kind"],
        "phoneme_encoding": encoding,
        "data_version": metadata.get("data_version", metadata.get("version")),
        "asset_path": asset_path,
    }
    return MappingProxyType(info)


class OrderedLexiconLookup:
    """Search configured lookups in order and retain the first hit."""

    def __init__(self, lookups: Sequence[PronunciationLookup]) -> None:
        self._lookups = tuple(lookups)
        self._closed = False

    def lookup(self, word: str, *, tag: str | None = None) -> LexiconPronunciation | None:
        return self.lookup_many((word,), tag=tag)[0]

    def lookup_many(
        self,
        words: Sequence[str],
        *,
        tag: str | None = None,
    ) -> tuple[LexiconPronunciation | None, ...]:
        if self._closed:
            raise LexiconResourceError("Configured lexicon lookup is closed.")
        results: list[LexiconPronunciation | None] = [None] * len(words)
        unresolved = list(range(len(words)))
        for lookup in self._lookups:
            if not unresolved:
                break
            batch = lookup.lookup_many(tuple(words[index] for index in unresolved), tag=tag)
            if len(batch) != len(unresolved):
                raise LexiconResourceError("Configured lexicon returned an invalid batch length.")
            remaining: list[int] = []
            for index, pronunciation in zip(unresolved, batch, strict=True):
                if pronunciation is None:
                    remaining.append(index)
                else:
                    results[index] = pronunciation
            unresolved = remaining
        return tuple(results)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for lookup in self._lookups:
            lookup.close()


def create_lookup(
    lexicons: str | Sequence[str] | None,
    *,
    language: str,
    store: Any = None,
) -> PronunciationLookup | None:
    if lexicons is None:
        return None
    names = (lexicons,) if isinstance(lexicons, str) else tuple(lexicons)
    if not names:
        return None
    lookups: list[PronunciationLookup] = []
    for name in names:
        path = Path(name)
        if path.suffix.casefold() == ".g2lex":
            lookups.append(G2LexLookup((path,), language=language))
        else:
            lookups.append(LexphonLookup(language, (name,), store=store))
    return OrderedLexiconLookup(lookups)
