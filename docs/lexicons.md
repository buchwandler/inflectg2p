# Lexicons

Pronunciation lexicons are optional overlays for prepared text. Precedence is:

1. first pronunciation hit from configured lexicons, in the order configured;
2. `espeakng-runtime` for unresolved spans, if fallback is enabled;
3. Inflect symbol validation and token encoding.

`inflectg2p` does not download or install lexicons. A lexicon miss is distinct from an invalid or unavailable resource. Invalid metadata, unsupported pronunciation encoding, lookup failures, and unencodable IPA are errors. The supported lexicon pronunciation encoding for v0.1.0 is generic IPA.

## Managed Lexphon assets

Install the adapter and provision an asset separately. For example:

```console
python -m pip install 'inflectg2p[lexphon]'
lexphon data available en-US
lexphon data install en-us:lexhint
lexphon data verify en-us:lexhint
```

Inspect locally provisioned assets with:

```python
from inflectg2p import available_lexicons, lexicon_info

for name in available_lexicons("en-US"):
    print(name, lexicon_info("en-US", name))
```

Use a provisioned lexicon by name:

```python
from inflectg2p import InflectG2P

with InflectG2P(lexicons=("en-us:lexhint",)) as g2p:
    result = g2p.phonemize_prepared("Saskatchewan is fluorescent.")

print(result.phonemes)
print(result.lexicon_hits)
```

The `en-us:lexhint` asset must already be installed in the Lexphon store. Runtime lookup never performs provisioning.

To disable fallback, provide at least one lexicon and set `use_espeak_fallback=False`. A missing word raises `LexiconMissError` rather than invoking eSpeak.

## Direct local G2Lex files

Install the optional adapter, then load an explicit `.g2lex` resource:

```console
python -m pip install 'inflectg2p[g2lex]'
g2lex inspect ./build/custom.g2lex
```

```python
from inflectg2p import InflectG2P
from inflectg2p.lexicons import G2LexLookup

lookup = G2LexLookup(["./build/custom.g2lex"], language="en-US")
try:
    with InflectG2P(lexicon_backend=lookup) as g2p:
        result = g2p.phonemize_prepared("AcmeWidget")
        print(result.phonemes)
finally:
    lookup.close()
```

An injected lookup remains caller-owned. `G2LexLookup` opens only the given local file and validates language, kind, and pronunciation encoding. Multiple assets are searched in order. Lexicon hits retain their source, matched key, ID, encoding, and available version/path metadata in `result.lexicon_hits`.

## Custom lookup

Applications can inject their own `PronunciationLookup` implementation. It returns `LexiconPronunciation` records in generic IPA and implements `lookup`, `lookup_many`, and `close`. This is also the preferred way to test overlay behavior without requiring optional packages or provisioned data.
