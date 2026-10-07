# Quick start

```python
from inflectg2p import InflectG2P

with InflectG2P() as g2p:
    result = g2p.phonemize_prepared("Hello, world.")

print(result.phonemes)
print(result.token_ids)
print(result.token_count)
```

The input string is prepared text. `result.text` preserves it exactly. The frontend performs phonemization, symbol encoding, and blank interspersion only.

The equivalent command-line call is:

```console
inflectg2p 'Hello, world.'
```

See [prepared text](prepared-text.md) for the input contract. Reusable scripts are in the repository's `examples/` directory.
