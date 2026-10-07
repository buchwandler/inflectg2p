# Inflect codec

The codec maps each character in the phoneme stream through the public Inflect v2 symbol inventory in `inflectg2p.symbols`. The inventory and character-to-ID mapping are exact frontend data, independent of the eSpeak implementation.

For symbol IDs `s`, Inflect blank interspersion produces:

```text
[0, s0, 0, s1, 0, ..., sn, 0]
```

The resulting length is `2 * len(s) + 1`. Blank/pad ID is `0`; the space symbol is encoded as a regular inventory symbol.

`encode_phonemes`, `intersperse_blanks`, and `phoneme_ids` are available from the package root. An empty phoneme stream has no model-ready token sequence and raises `ValueError`. A symbol absent from the inventory raises `MissingSymbolError`, which reports the symbol and its position rather than silently dropping it.
