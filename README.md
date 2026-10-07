# inflectg2p

Independent Python packaging of the public **Inflect v2** English text frontend.
It performs the same written-text normalization, eSpeak-ng phonemization, verified
phoneme overrides, symbol lookup, and VITS blank interspersion used by the public
Inflect-Nano-v2 / Inflect-Micro-v2 runners.

The package has a flat layout (no `src/`) and uses Git-tag-driven `setuptools-scm`
dynamic versioning.

## Install

```bash
python -m pip install inflectg2p
```

## Python

```python
from inflectg2p import run_frontend

result = run_frontend("The invoice is $12.50 at 9:05 AM.")
print(result.normalized_text)
print(result.phoneme_text)
print(result.token_ids)
```

`token_ids` are model-ready Inflect v2 IDs: every phoneme-symbol ID is interspersed
with blank/pad ID `0`, producing the same `(2*n)+1` framing used by the official ONNX
runner.

## Compatibility target

This MVP follows the public v2 frontend contract published in both official releases:

- English `en-us` eSpeak phonemization with stress and punctuation preserved;
- public normalization rules for numbers, money, dates, times, abbreviations, acronyms,
  identifiers, and punctuation;
- the two published phoneme overrides;
- the published Inflect/Tacotron symbol inventory;
- strict symbol lookup, matching upstream failure semantics for unsupported output symbols.

## Dynamic versioning

Versions come from Git tags through `setuptools-scm`. A source archive without Git metadata
uses `0.1.dev0`; `inflectg2p.__version__` reads installed distribution metadata.

## License

Apache-2.0. The Inflect frontend code this package derives from is published by Owen Song
under Apache-2.0. Third-party dependencies retain their own licenses.
