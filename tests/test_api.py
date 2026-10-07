import pytest

from inflectg2p import (
    BackendError,
    InflectG2P,
    PhonemizationError,
    PhonemizeResult,
    phoneme_ids,
    phonemes,
    phonemize_prepared,
)


class CapturingBackend:
    def __init__(self, phonemes: str = "ab") -> None:
        self.phonemes = phonemes
        self.seen: list[str] = []
        self.close_count = 0

    def phonemize(self, text: str, *, voice: str) -> str:
        assert voice == "en-us"
        self.seen.append(text)
        return self.phonemes

    def phonemize_many(self, texts: list[str], *, voice: str) -> list[str]:
        assert voice == "en-us"
        self.seen.extend(texts)
        return [self.phonemes for _ in texts]

    def close(self) -> None:
        self.close_count += 1


def test_prepared_text_reaches_injected_backend_unchanged():
    text = "Pay $12.50 at 9:05 AM."
    backend = CapturingBackend()
    result = InflectG2P(backend=backend).phonemize_prepared(text)

    assert backend.seen == [text]
    assert isinstance(result, PhonemizeResult)
    assert result.text == text
    assert result.phonemes == "ab"
    assert result.token_count == len(result.token_ids)
    assert not hasattr(result, "normalized_text")


def test_prepared_text_batch_preserves_values_and_order():
    texts = ["Room 12", "A+B", "3/4"]
    backend = CapturingBackend()
    results = InflectG2P(backend=backend).phonemize_prepared_batch(texts)

    assert backend.seen == texts
    assert [result.text for result in results] == texts
    assert [result.phonemes for result in results] == ["ab"] * len(texts)


def test_context_manager_does_not_close_injected_backend():
    backend = CapturingBackend()
    with InflectG2P(backend=backend) as g2p:
        g2p.phonemize_prepared("hello")

    assert backend.close_count == 0


def test_closed_frontend_rejects_further_calls_without_closing_injected_backend():
    backend = CapturingBackend()
    g2p = InflectG2P(backend=backend)
    g2p.close()
    g2p.close()

    with pytest.raises(BackendError, match="closed"):
        g2p.phonemize_prepared("hello")
    assert backend.close_count == 0


def test_injected_backend_exceptions_become_package_errors():
    class FailingBackend:
        def phonemize(self, text: str, *, voice: str) -> str:
            raise RuntimeError("backend failed")

        def phonemize_many(self, texts: list[str], *, voice: str) -> list[str]:
            raise RuntimeError("backend failed")

        def close(self) -> None:
            pass

    with pytest.raises(PhonemizationError, match="backend failed"):
        InflectG2P(backend=FailingBackend()).phonemize_prepared("hello")


def test_functional_api_helpers_share_the_prepared_text_contract():
    text = "  Values stay prepared: $12.50, not expanded.  "
    backend = CapturingBackend()

    result = phonemize_prepared(text, backend=backend)
    phoneme_text = phonemes(text, backend=backend)
    token_ids = phoneme_ids(text, backend=backend)

    assert result.text == text
    assert result.phonemes == phoneme_text == "ab"
    assert result.token_ids == token_ids
    assert backend.seen == [text, text, text]
