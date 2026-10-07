from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LexiconProvenance:
    lexicon_id: str | None = None
    language: str | None = None
    source_encoding: str = "ipa"
    data_version: str | None = None
    asset_path: str | None = None


@dataclass(frozen=True, slots=True)
class LexiconPronunciation:
    pronunciation: str
    source: str
    lexicon_id: str | None = None
    matched_key: str | None = None
    source_encoding: str = "ipa"
    provenance: LexiconProvenance | None = None


@dataclass(frozen=True, slots=True)
class LexiconHit:
    word: str
    pronunciation: str
    source: str
    lexicon_id: str | None = None
    matched_key: str | None = None
    source_encoding: str = "ipa"
    provenance: LexiconProvenance | None = None


@dataclass(frozen=True, slots=True)
class PhonemizeResult:
    text: str
    phonemes: str
    token_ids: tuple[int, ...]
    lexicon_hits: tuple[LexiconHit, ...] = ()

    @property
    def token_count(self) -> int:
        return len(self.token_ids)
