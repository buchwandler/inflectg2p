# Architecture

```text
caller-owned semantic preparation
              |
              v
prepared text
              |
              +---- optional ordered lexicon overlay
              |                  |
              |          unresolved spans, if enabled
              |                  v
              +---------- espeakng-runtime
                                 |
                                 v
                punctuation-preserving renderer
                                 |
                                 v
                  Inflect symbol encoding
                                 |
                                 v
                   blank interspersion
                                 |
                                 v
                       token IDs
```

## Responsibilities

| Area                      | Responsibility                                                         |
| ------------------------- | ---------------------------------------------------------------------- |
| Caller                    | Written-to-spoken semantic preparation and lexicon asset provisioning. |
| `inflectg2p` API          | Prepared-text operations and immutable result values.                  |
| `espeakng-runtime`        | Runtime discovery and eSpeak invocation.                               |
| Inflect codec             | Exact symbol IDs, strict output validation, and blank framing.         |
| Optional lexicon adapters | Explicit lookup, metadata validation, and provenance.                  |

## Resource ownership

| Resource                                | Owner                                     |
| --------------------------------------- | ----------------------------------------- |
| Injected phoneme backend                | Caller                                    |
| Internally created eSpeak runtime       | `InflectG2P`                              |
| Injected lexicon lookup                 | Caller                                    |
| Internally created Lexphon/G2Lex lookup | `InflectG2P`                              |
| Lexicon installation or provisioning    | Caller or a separate provisioning process |

The core path has no model loading, audio synthesis, semantic expansion, or implicit network access. See [prepared text](prepared-text.md), [backends](backends.md), and [lexicons](lexicons.md) for details.
