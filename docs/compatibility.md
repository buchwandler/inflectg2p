# Compatibility

Compatibility is defined in layers. This package does not claim blanket equivalence with every historical Inflect runner or every eSpeak installation.

## Exact and structural behavior

- The checked-in Inflect v2 symbol inventory and symbol-to-ID mapping.
- Blank/pad ID `0` and blank framing of `(2 * symbol_count) + 1` IDs.
- Strict failure for output symbols outside that inventory.
- Preservation of supported punctuation and literal spaces around eSpeak-rendered spans.
- Prepared input is not semantically rewritten.

The exact frontend snapshots are in [`tests/goldens/inflect_v2_en_us.json`](../tests/goldens/inflect_v2_en_us.json). They record phoneme strings and token IDs for review. Runtime integration tests separately exercise `auto`, CLI, and native modes when available.

## Runtime-dependent behavior

Pronunciation varies with eSpeak version, voice data, and runtime mode. `espeakng-runtime` may choose a different CLI or native installation on different systems. Therefore exact pronunciation parity is not promised across runtime versions. The integration suite checks punctuation transport, stress presence, Unicode IPA encoding, and scalar/batch consistency on the runtime under test.

The old project-specific hard-coded pronunciation overrides are intentionally absent. Use an explicit lexicon when an application needs a pronunciation exception. A lexicon-selected pronunciation is an intentional override, not an unqualified claim of pure eSpeak parity.

## Out of scope

- Semantic expansion of numbers, dates, times, currency, units, identifiers, acronyms, or abbreviations.
- Loading a TTS model or generating audio.
- Automatic pronunciation-data installation.
