# inflectg2p

An Inflect v2 phoneme and token-ID frontend for **prepared, speakable English text**.

`inflectg2p` sends text through `espeakng-runtime`, applies the Inflect symbol inventory, and intersperses VITS-style blank IDs. It does not expand numbers, dates, times, currency, abbreviations, identifiers, or other semantic written forms. Prepare those in your application before calling this package. It does not load a TTS model or synthesize audio.

## Install

```console
python -m pip install inflectg2p
```

Optional runtime and lexicon extras:

```console
python -m pip install 'inflectg2p[bundled]'
python -m pip install 'inflectg2p[lexphon]'
python -m pip install 'inflectg2p[g2lex]'
```

Lexicon packages and pronunciation assets are optional. `inflectg2p` never downloads lexicons implicitly. See [installation](docs/installation.md) and [lexicons](docs/lexicons.md).

## Python

```python
from inflectg2p import InflectG2P

with InflectG2P() as g2p:
    result = g2p.phonemize_prepared("Hello, world.")

print(result.phonemes)
print(result.token_ids)
print(result.token_count)
```

`result.text` is the unchanged input. `result.lexicon_hits` reports explicit lexicon matches when configured. The functional helpers `phonemize_prepared`, `phonemes`, and `phoneme_ids` are also available.

## CLI

```console
inflectg2p 'Hello, world.'
inflectg2p --espeak-mode cli 'Hello, world.'
inflectg2p --lexicon en-us:lexhint 'Saskatchewan is fluorescent.'
```

The CLI prints JSON containing the prepared text, phonemes, token IDs, and token count. There is no `--normalize` option because semantic preparation belongs to the caller.

## Documentation and examples

Start with the [documentation index](docs/index.md). Runnable examples are in [`examples/`](examples/).

## Compatibility

The exact contract covers the Inflect v2 symbol inventory, strict symbol validation, and blank framing. eSpeak pronunciation depends on the installed runtime and voice data. See [compatibility](docs/compatibility.md) for the boundaries and golden snapshots.

## Version and license

Versions are derived from Git tags with `setuptools-scm`. The project is licensed under Apache-2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
