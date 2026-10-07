import pytest

from inflectg2p import BackendUnavailableError, InflectG2P, InflectG2PConfig

pytestmark = [pytest.mark.espeak, pytest.mark.integration]


def frontend_for_mode(mode):
    try:
        return InflectG2P(InflectG2PConfig(voice="en-us", espeak_mode=mode))
    except BackendUnavailableError as exc:
        pytest.skip(f"eSpeak mode {mode!r} is unavailable: {exc}")


@pytest.mark.parametrize("mode", ("auto", "cli", "native"))
def test_runtime_modes_preserve_inflect_punctuation_and_stress(mode):
    text = "“Hello,” she said—really…"
    with frontend_for_mode(mode) as g2p:
        result = g2p.phonemize_prepared(text)

    assert result.text == text
    assert result.phonemes.startswith("“")
    assert ",” " in result.phonemes
    assert "—" in result.phonemes
    assert result.phonemes.endswith("…")
    assert "ˈ" in result.phonemes or "ˌ" in result.phonemes
    assert result.token_ids


@pytest.mark.parametrize("mode", ("auto", "cli", "native"))
def test_runtime_scalar_and_batch_rendering_agree(mode):
    texts = ["Hello, world.", "Café, please.", "One; two?"]
    with frontend_for_mode(mode) as g2p:
        scalar = [g2p.phonemize_prepared(text).phonemes for text in texts]
        batch = [result.phonemes for result in g2p.phonemize_prepared_batch(texts)]

    assert scalar == batch
