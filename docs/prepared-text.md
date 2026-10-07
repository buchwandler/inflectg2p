# Prepared-text boundary

`inflectg2p` starts at prepared, speakable English text. It does not decide how written semantic forms should be spoken. Numbers, currency, units, dates, times, abbreviations, URLs, versions, identifiers, and application-specific names must be prepared before G2P.

```text
application text
       |
       | caller-owned semantic preparation
       v
prepared, speakable English text
       |
       | inflectg2p
       v
phonemes and Inflect token IDs
```

For example, call an application-owned preparation function before phonemization:

```python
prepared_text = application_prepare(source_text)
result = g2p.phonemize_prepared(prepared_text)
```

`application_prepare` is a placeholder for your application's own policy, not an `inflectg2p` API. This project does not depend on or prescribe a particular number, abbreviation, or semantic-normalization package.

The frontend preserves the prepared input in `result.text`. It does not rewrite punctuation into different punctuation or return a normalized-text field. eSpeak rendering transports supported punctuation and spaces through phonemization.
