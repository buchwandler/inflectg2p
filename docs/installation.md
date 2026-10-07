# Installation

Install the core package with pip:

```console
python -m pip install inflectg2p
```

The core dependency is `espeakng-runtime`. It discovers an available eSpeak runtime according to its configured mode. A system eSpeak NG installation may be used where available. To install the runtime's bundled assets, use:

```console
python -m pip install 'inflectg2p[bundled]'
```

Optional pronunciation adapters are installed separately:

```console
python -m pip install 'inflectg2p[lexphon]'
python -m pip install 'inflectg2p[g2lex]'
```

The `lexicons` extra is an alias for the Lexphon adapter. Installing an adapter does not install or download pronunciation assets. Provision assets with the relevant lexicon tooling before using them.

For documentation builds and development:

```console
python -m pip install 'inflectg2p[docs]'
python -m pip install 'inflectg2p[dev]'
```

`inflectg2p` does not configure `phonemizer`, mutate eSpeak environment variables, or install semantic-preparation packages. Applications that verbalize numbers, dates, times, currencies, abbreviations, or other written forms should install and call their own preparation layer before passing text here.
