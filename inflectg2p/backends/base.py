from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class PhonemeBackend(Protocol):
    def phonemize(self, text: str, *, voice: str) -> str: ...

    def phonemize_many(self, texts: Sequence[str], *, voice: str) -> list[str]: ...

    def close(self) -> None: ...
