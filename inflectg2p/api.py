from __future__ import annotations

from .frontend import run_frontend, run_frontend_batch
from .types import FrontendResult


class InflectG2P:
    """Reusable Inflect v2 text frontend.

    The upstream public frontend has no per-request speaker or language selector;
    Inflect v2 is English-only and uses the ``en-us`` eSpeak voice.
    """

    def phonemize(self, text: str) -> FrontendResult:
        return run_frontend(text)

    def phonemize_batch(self, texts: list[str], *, jobs: int = 1) -> list[FrontendResult]:
        return run_frontend_batch(texts, jobs=jobs)

    def __enter__(self) -> InflectG2P:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def phonemize(text: str) -> str:
    return run_frontend(text).phoneme_text


def token_ids(text: str) -> tuple[int, ...]:
    return run_frontend(text).token_ids
