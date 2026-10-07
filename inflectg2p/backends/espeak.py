from __future__ import annotations

from collections.abc import Callable, Sequence

from espeakng_runtime import EspeakRuntime
from espeakng_runtime.errors import EspeakError

from ..config import InflectG2PConfig
from ..errors import BackendUnavailableError, PhonemizationError
from ..symbols import SYMBOLS

_PUNCTUATION = frozenset(SYMBOLS[1:16])


def _split_prepared_text(text: str) -> list[tuple[str, bool]]:
    """Split speakable spans from Inflect punctuation and literal spaces."""
    spans: list[tuple[str, bool]] = []
    start = 0
    is_speakable: bool | None = None
    for index, character in enumerate(text):
        current_is_speakable = character != " " and character not in _PUNCTUATION
        if is_speakable is None:
            is_speakable = current_is_speakable
        elif current_is_speakable != is_speakable:
            spans.append((text[start:index], is_speakable))
            start = index
            is_speakable = current_is_speakable
    if start < len(text):
        spans.append((text[start:], bool(is_speakable)))
    return spans


def _render_many(
    texts: Sequence[str],
    phonemize_many: Callable[..., list[str]],
    *,
    voice: str,
) -> list[str]:
    spans_by_text = [_split_prepared_text(text) for text in texts]
    spoken = [span for spans in spans_by_text for span, speakable in spans if speakable]
    phonemes = iter(phonemize_many(spoken, voice=voice) if spoken else ())
    rendered: list[str] = []
    for spans in spans_by_text:
        rendered.append("".join(next(phonemes) if speakable else span for span, speakable in spans))
    return rendered


class EspeakBackend:
    """Punctuation-preserving Inflect adapter for ``espeakng-runtime``."""

    def __init__(self, config: InflectG2PConfig | None = None) -> None:
        config = config or InflectG2PConfig()
        try:
            self._runtime = EspeakRuntime(
                mode=config.espeak_mode,
                executable=config.executable,
                library=config.library,
                data=config.data,
                timeout=config.timeout,
            )
        except EspeakError as exc:
            raise BackendUnavailableError(f"Could not initialize eSpeak: {exc}") from exc

    @property
    def diagnostics(self) -> object:
        return self._runtime.info

    def phonemize(self, text: str, *, voice: str) -> str:
        return self.phonemize_many([text], voice=voice)[0]

    def phonemize_many(self, texts: Sequence[str], *, voice: str) -> list[str]:
        try:
            return _render_many(texts, self._runtime.phonemize_many, voice=voice)
        except EspeakError as exc:
            raise PhonemizationError(f"eSpeak could not phonemize prepared text: {exc}") from exc

    def close(self) -> None:
        self._runtime.close()
