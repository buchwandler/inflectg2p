from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FrontendResult:
    raw_text: str
    normalized_text: str
    phoneme_text: str
    token_ids: tuple[int, ...]

    @property
    def token_count(self) -> int:
        return len(self.token_ids)
