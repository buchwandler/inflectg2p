# eSpeak backends

The default backend is `EspeakBackend`, a thin adapter over `espeakng-runtime`. Runtime discovery, native loading, CLI invocation, and runtime-specific diagnostics are delegated to that dependency. `inflectg2p` does not configure `phonemizer` or mutate eSpeak-related environment variables.

## Modes and paths

```python
from inflectg2p import InflectG2P, InflectG2PConfig

config = InflectG2PConfig(
    voice="en-us",
    espeak_mode="auto",  # auto, native, or cli
    executable=None,
    library=None,
    data=None,
    timeout=None,
)
with InflectG2P(config) as g2p:
    result = g2p.phonemize_prepared("Hello, world.")
```

Use `native` or `cli` to select a specific runtime path. `executable`, `library`, and `data` are explicit overrides. `timeout` is forwarded to the runtime. The default voice is `en-us`.

## Punctuation transport

The adapter separates supported Inflect punctuation and literal spaces from speakable spans, sends only the spans through eSpeak, then rejoins them in their original positions. It does not translate one punctuation character into another. Supported punctuation comes from the Inflect symbol inventory; unsupported output symbols fail during codec validation.

## Diagnostics and injection

`EspeakBackend.diagnostics` exposes the runtime info object when using the adapter directly:

```python
from inflectg2p import InflectG2PConfig
from inflectg2p.backends import EspeakBackend

config = InflectG2PConfig()

backend = EspeakBackend(config)
try:
    print(backend.diagnostics)
finally:
    backend.close()
```

Applications and tests can inject a backend implementing `phonemize(text, *, voice)`, `phonemize_many(texts, *, voice)`, and `close()`. An injected backend remains caller-owned. `InflectG2P` closes only a backend that it created.

With fallback disabled and a configured lexicon lookup, no eSpeak runtime is constructed. A lexicon miss then raises `LexiconMissError`.
