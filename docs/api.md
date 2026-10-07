# Python API

## Frontend class

`InflectG2P` provides reusable scalar and batch operations:

```python
from inflectg2p import InflectG2P, InflectG2PConfig

config = InflectG2PConfig(voice="en-us", espeak_mode="auto")
with InflectG2P(config) as g2p:
    one = g2p.phonemize_prepared("Hello.")
    many = g2p.phonemize_prepared_batch(["Hello.", "Good morning."])
```

The class closes a runtime it created. A backend or lexicon lookup passed by the caller remains caller-owned and must be closed by that caller when appropriate. See [backends](backends.md) and [lexicons](lexicons.md).

## Functional helpers

The package root exports:

- `phonemize_prepared(text, ...)`, returning the complete result;
- `phonemes(text, ...)`, returning the phoneme string;
- `phoneme_ids(text, ...)`, returning the token-ID tuple.

All helpers accept the same prepared text. They accept optional `InflectG2PConfig`, injected backend or lexicon lookup, and lexicon configuration arguments.

## Result

`PhonemizeResult` is an immutable value with:

- `text`: original prepared input;
- `phonemes`: rendered phoneme stream, including preserved supported punctuation and spaces;
- `token_ids`: Inflect symbol IDs with blank ID `0` interspersed;
- `token_count`: length of `token_ids`;
- `lexicon_hits`: provenance records for selected lexicon pronunciations.

`LexiconHit` and `LexiconProvenance` identify the matched word, pronunciation source, lexicon ID, key, encoding, and available asset metadata.

## Configuration

`InflectG2PConfig` defaults to voice `en-us`, eSpeak mode `auto`, and automatic runtime discovery. The `espeak_mode` choices are `auto`, `native`, and `cli`. Optional `executable`, `library`, `data`, and `timeout` values are forwarded to `espeakng-runtime`.

## Errors

All package errors derive from `InflectG2PError`. Backend failures use `BackendError`, `BackendUnavailableError`, and `PhonemizationError`. Lexicon errors use `LexiconError`, `LexiconDependencyError`, `LexiconResourceError`, and `LexiconMissError`. Unsupported Inflect symbols raise `MissingSymbolError` with the offending symbol and position.
