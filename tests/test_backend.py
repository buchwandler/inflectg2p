import pytest
from espeakng_runtime.errors import EspeakError
from espeakng_runtime.errors import PhonemizationError as EspeakPhonemizationError

from inflectg2p import (
    SYMBOLS,
    BackendUnavailableError,
    InflectG2PConfig,
    PhonemizationError,
)
from inflectg2p.backends import EspeakBackend


class FakeRuntime:
    def __init__(self, **kwargs):
        self.arguments = kwargs
        self.info = object()
        self.calls: list[tuple[list[str], str]] = []
        self.close_count = 0
        self.fail: Exception | None = None

    def phonemize_many(self, texts, *, voice):
        self.calls.append((list(texts), voice))
        if self.fail is not None:
            raise self.fail
        return ["ab" for _ in texts]

    def close(self):
        self.close_count += 1


def test_config_defaults_and_validation():
    assert InflectG2PConfig().voice == "en-us"
    assert InflectG2PConfig().espeak_mode == "auto"
    for mode in ("native", "cli", "auto"):
        assert InflectG2PConfig(espeak_mode=mode).espeak_mode == mode
    with pytest.raises(ValueError, match="espeak_mode"):
        InflectG2PConfig(espeak_mode="invalid")
    with pytest.raises(ValueError, match="voice"):
        InflectG2PConfig(voice=" ")
    with pytest.raises(ValueError, match="timeout"):
        InflectG2PConfig(timeout=0)


def test_espeak_backend_forwards_runtime_configuration(monkeypatch):
    runtime = FakeRuntime()
    calls = []

    def runtime_factory(**kwargs):
        calls.append(kwargs)
        return runtime

    monkeypatch.setattr("inflectg2p.backends.espeak.EspeakRuntime", runtime_factory)
    config = InflectG2PConfig(
        espeak_mode="cli",
        executable="/opt/espeak",
        library="/opt/libespeak.so",
        data="/opt/espeak-data",
        timeout=3.5,
    )
    backend = EspeakBackend(config)

    assert calls == [
        {
            "mode": "cli",
            "executable": "/opt/espeak",
            "library": "/opt/libespeak.so",
            "data": "/opt/espeak-data",
            "timeout": 3.5,
        }
    ]
    assert backend.diagnostics is runtime.info


def test_punctuation_and_exact_spaces_survive_rendering(monkeypatch):
    runtime = FakeRuntime()
    monkeypatch.setattr("inflectg2p.backends.espeak.EspeakRuntime", lambda **_: runtime)
    backend = EspeakBackend()
    punctuation = "".join(SYMBOLS[1:16])

    assert backend.phonemize(f"  one,  two! {punctuation}", voice="en-us") == (
        f"  ab,  ab! {punctuation}"
    )
    assert runtime.calls == [(["one", "two"], "en-us")]


def test_punctuation_only_and_empty_text_need_no_runtime_call(monkeypatch):
    runtime = FakeRuntime()
    monkeypatch.setattr("inflectg2p.backends.espeak.EspeakRuntime", lambda **_: runtime)
    backend = EspeakBackend()
    punctuation = "".join(SYMBOLS[1:16])

    assert backend.phonemize(punctuation, voice="en-us") == punctuation
    assert backend.phonemize("", voice="en-us") == ""
    assert runtime.calls == []


def test_scalar_and_batch_rendering_are_equal(monkeypatch):
    runtime = FakeRuntime()
    monkeypatch.setattr("inflectg2p.backends.espeak.EspeakRuntime", lambda **_: runtime)
    backend = EspeakBackend()
    texts = ["hello, world!", "A  B."]

    scalar = [backend.phonemize(text, voice="en-us") for text in texts]
    batch = backend.phonemize_many(texts, voice="en-us")

    assert scalar == batch == ["ab, ab!", "ab  ab."]


def test_runtime_initialization_errors_are_mapped(monkeypatch):
    def fail(**kwargs):
        raise EspeakError("unavailable")

    monkeypatch.setattr("inflectg2p.backends.espeak.EspeakRuntime", fail)
    with pytest.raises(BackendUnavailableError, match="unavailable"):
        EspeakBackend()


def test_runtime_phonemization_errors_are_mapped(monkeypatch):
    runtime = FakeRuntime()
    runtime.fail = EspeakPhonemizationError("runtime failure")
    monkeypatch.setattr("inflectg2p.backends.espeak.EspeakRuntime", lambda **_: runtime)
    backend = EspeakBackend()

    with pytest.raises(PhonemizationError, match="runtime failure"):
        backend.phonemize("hello", voice="en-us")


def test_default_backend_is_closed_idempotently(monkeypatch):
    runtime = FakeRuntime()
    monkeypatch.setattr("inflectg2p.backends.espeak.EspeakRuntime", lambda **_: runtime)
    from inflectg2p.api import InflectG2P

    g2p = InflectG2P()
    g2p.close()
    g2p.close()

    assert runtime.close_count == 1
