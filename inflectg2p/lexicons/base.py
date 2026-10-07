from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..types import LexiconPronunciation, LexiconProvenance

SUPPORTED_PHONEME_ENCODINGS = frozenset({"ipa"})


def normalize_phoneme_encoding(value: object | None) -> str:
    if value is None:
        return "ipa"
    normalized = str(value).strip().casefold().replace("_", "-")
    if normalized in {"ipa", "unicode-ipa", "ipa-unicode", "generic-ipa"}:
        return "ipa"
    raise ValueError(f"unsupported Inflect lexicon pronunciation encoding {value!r}")


class PronunciationLookup(Protocol):
    def lookup(
        self,
        word: str,
        *,
        tag: str | None = None,
    ) -> LexiconPronunciation | None: ...

    def lookup_many(
        self,
        words: Sequence[str],
        *,
        tag: str | None = None,
    ) -> tuple[LexiconPronunciation | None, ...]: ...

    def close(self) -> None: ...


__all__ = [
    "SUPPORTED_PHONEME_ENCODINGS",
    "LexiconPronunciation",
    "LexiconProvenance",
    "PronunciationLookup",
    "normalize_phoneme_encoding",
]
