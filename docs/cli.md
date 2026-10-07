# Command-line interface

The CLI consumes prepared text as one positional argument and prints one JSON object to standard output:

```console
inflectg2p 'Hello, world.'
inflectg2p --espeak-mode cli 'Hello, world.'
inflectg2p --lexicon en-us:lexhint 'Saskatchewan is fluorescent.'
```

The output shape is:

```json
{
  "text": "Hello, world.",
  "phonemes": "...",
  "token_ids": [0, 1, 0],
  "token_count": 3
}
```

Available runtime options are `--espeak-mode auto|native|cli`, `--executable`, `--library`, `--data`, and `--timeout`. Repeat `--lexicon` to set an ordered list. `--no-espeak-fallback` requires at least one configured lexicon and makes unresolved words an error.

Errors are written to standard error without a traceback and return status `2`. Successful calls return status `0`. There is no `--normalize` flag. Prepare semantic written forms before passing text to the CLI.
