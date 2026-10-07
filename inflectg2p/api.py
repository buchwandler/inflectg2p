from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .backends import EspeakBackend, PhonemeBackend
from .config import InflectG2PConfig
from .errors import BackendError, InflectG2PError, PhonemizationError
from .frontend import result_from_phonemes
from .lexicons import PronunciationLookup, apply_lexicon_overlay, create_lookup
from .types import LexiconHit, PhonemizeResult


class InflectG2P:
    """Convert caller-prepared English text to Inflect phonemes and token IDs."""

    def __init__(
        self,
        config: InflectG2PConfig | None = None,
        *,
        backend: PhonemeBackend | None = None,
        lexicons: str | Sequence[str] | None = None,
        lexicon_backend: PronunciationLookup | None = None,
        lexicon_store: Any = None,
        use_espeak_fallback: bool = True,
    ) -> None:
        if lexicon_backend is not None and lexicons is not None:
            raise ValueError("Pass lexicons or lexicon_backend, not both.")
        if not use_espeak_fallback and lexicon_backend is None and not lexicons:
            raise ValueError("Disabling eSpeak fallback requires a lexicon.")
        self.config = config or InflectG2PConfig()
        self._owns_backend = backend is None and use_espeak_fallback
        self._backend: PhonemeBackend | None = (
            EspeakBackend(self.config) if backend is None and use_espeak_fallback else backend
        )
        self._lexicon_backend = (
            create_lookup(lexicons, language=self.config.voice, store=lexicon_store)
            if lexicon_backend is None
            else lexicon_backend
        )
        self._owns_lexicon_backend = lexicon_backend is None and self._lexicon_backend is not None
        self._use_espeak_fallback = use_espeak_fallback
        self._closed = False

    def phonemize_prepared(self, text: str) -> PhonemizeResult:
        self._ensure_open()
        try:
            if self._lexicon_backend is None:
                phonemes = self._phonemize_text(text)
                hits: tuple[LexiconHit, ...] = ()
            else:
                phonemes, hits = apply_lexicon_overlay(
                    text,
                    self._lexicon_backend,
                    self._phonemize_text,
                    fallback=self._use_espeak_fallback,
                )
        except InflectG2PError:
            raise
        except Exception as exc:
            raise PhonemizationError(f"Could not phonemize prepared text: {exc}") from exc
        return result_from_phonemes(text, phonemes, hits)

    def phonemize_prepared_batch(self, texts: Sequence[str]) -> list[PhonemizeResult]:
        self._ensure_open()
        text_list = list(texts)
        if self._lexicon_backend is not None:
            return [self.phonemize_prepared(text) for text in text_list]
        backend = self._backend
        if backend is None:
            raise BackendError("eSpeak fallback is disabled.")
        try:
            phoneme_list = backend.phonemize_many(text_list, voice=self.config.voice)
        except InflectG2PError:
            raise
        except Exception as exc:
            raise PhonemizationError(f"Could not phonemize prepared text batch: {exc}") from exc
        return [
            result_from_phonemes(text, phonemes)
            for text, phonemes in zip(text_list, phoneme_list, strict=True)
        ]

    def _phonemize_text(self, text: str) -> str:
        if self._backend is None:
            raise BackendError("eSpeak fallback is disabled.")
        return self._backend.phonemize(text, voice=self.config.voice)

    def _ensure_open(self) -> None:
        if self._closed:
            raise BackendError("InflectG2P is closed.")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owns_backend and self._backend is not None:
            self._backend.close()
        if self._owns_lexicon_backend and self._lexicon_backend is not None:
            self._lexicon_backend.close()

    def __enter__(self) -> InflectG2P:
        self._ensure_open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def phonemize_prepared(
    text: str,
    config: InflectG2PConfig | None = None,
    *,
    backend: PhonemeBackend | None = None,
    lexicons: str | Sequence[str] | None = None,
    lexicon_backend: PronunciationLookup | None = None,
    lexicon_store: Any = None,
    use_espeak_fallback: bool = True,
) -> PhonemizeResult:
    with InflectG2P(
        config,
        backend=backend,
        lexicons=lexicons,
        lexicon_backend=lexicon_backend,
        lexicon_store=lexicon_store,
        use_espeak_fallback=use_espeak_fallback,
    ) as g2p:
        return g2p.phonemize_prepared(text)


def phonemes(
    text: str,
    config: InflectG2PConfig | None = None,
    *,
    backend: PhonemeBackend | None = None,
    lexicons: str | Sequence[str] | None = None,
    lexicon_backend: PronunciationLookup | None = None,
    lexicon_store: Any = None,
    use_espeak_fallback: bool = True,
) -> str:
    return phonemize_prepared(
        text,
        config,
        backend=backend,
        lexicons=lexicons,
        lexicon_backend=lexicon_backend,
        lexicon_store=lexicon_store,
        use_espeak_fallback=use_espeak_fallback,
    ).phonemes


def phoneme_ids(
    text: str,
    config: InflectG2PConfig | None = None,
    *,
    backend: PhonemeBackend | None = None,
    lexicons: str | Sequence[str] | None = None,
    lexicon_backend: PronunciationLookup | None = None,
    lexicon_store: Any = None,
    use_espeak_fallback: bool = True,
) -> tuple[int, ...]:
    return phonemize_prepared(
        text,
        config,
        backend=backend,
        lexicons=lexicons,
        lexicon_backend=lexicon_backend,
        lexicon_store=lexicon_store,
        use_espeak_fallback=use_espeak_fallback,
    ).token_ids
