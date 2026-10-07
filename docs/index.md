# inflectg2p documentation

`inflectg2p` converts prepared, speakable English text into Inflect-compatible phonemes and token IDs. It does not perform semantic written-to-spoken preparation, load a TTS model, or synthesize audio.

The library uses `espeakng-runtime` directly. Optional pronunciation lexicons are explicitly configured and never installed during lookup. Runnable scripts are maintained in the repository's `examples/` directory.

```{toctree}
:maxdepth: 2
:caption: Guides

installation
quickstart
prepared-text
api
backends
lexicons
codec
compatibility
cli
architecture
changelog
```
