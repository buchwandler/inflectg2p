# Examples

Run from the repository root after installing the project:

```console
python examples/basic_usage.py
python examples/backend_modes.py --mode auto
python examples/result_inspection.py
python examples/custom_backend.py
```

These examples need no pronunciation lexicon assets. The first three use an available eSpeak runtime. `custom_backend.py` is deterministic and does not invoke eSpeak.

Lexicon examples are explicit about optional packages and provisioned resources:

- `lexicon_selection.py` requires the `lexphon` extra;
- `lexicon_usage.py` requires the `en-us:lexhint` asset to be installed in the Lexphon store;
- `direct_g2lex.py` requires the `g2lex` extra and a local `.g2lex` file.

None of the examples installs assets automatically.
