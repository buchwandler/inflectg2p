import pytest

from inflectg2p import InflectG2P, LexiconMissError, LexiconResourceError, MissingSymbolError
from inflectg2p.lexicons import (
    LexiconPronunciation,
    LexiconProvenance,
    OrderedLexiconLookup,
    apply_lexicon_overlay,
)


class MappingLookup:
    def __init__(self, values):
        self.values = values
        self.calls = []
        self.close_count = 0
        self.error = None

    def lookup(self, word: str, *, tag: str | None = None):
        return self.lookup_many((word,), tag=tag)[0]

    def lookup_many(self, words, *, tag: str | None = None):
        self.calls.append((tuple(words), tag))
        if self.error is not None:
            raise self.error
        return tuple(self.values.get(word) for word in words)

    def close(self):
        self.close_count += 1


def pronunciation(word, value, *, lexicon_id="test", source="mapping", encoding="ipa"):
    provenance = LexiconProvenance(
        lexicon_id=lexicon_id,
        language="en-US",
        source_encoding=encoding,
        data_version="1",
        asset_path="fixture.g2lex",
    )
    return LexiconPronunciation(
        pronunciation=value,
        source=source,
        lexicon_id=lexicon_id,
        matched_key=word,
        source_encoding=encoding,
        provenance=provenance,
    )


def test_lexicon_hits_bypass_fallback_and_report_provenance():
    lookup = MappingLookup(
        {
            "Saskatchewan": pronunciation("Saskatchewan", "sɑsk"),
            "fluorescent": pronunciation("fluorescent", "flʊ"),
        }
    )
    fallback_calls = []

    rendered, hits = apply_lexicon_overlay(
        "Saskatchewan is fluorescent.",
        lookup,
        lambda text: fallback_calls.append(text) or f"[{text}]",
    )

    assert rendered == "sɑsk[ is ]flʊ."
    assert fallback_calls == [" is "]
    assert [hit.word for hit in hits] == ["Saskatchewan", "fluorescent"]
    assert hits[0].lexicon_id == "test"
    assert hits[0].matched_key == "Saskatchewan"
    assert hits[0].provenance == lookup.values["Saskatchewan"].provenance


def test_adjacent_hits_do_not_create_empty_fallback_calls():
    lookup = MappingLookup(
        {
            "one": pronunciation("one", "wʌn"),
            "two": pronunciation("two", "tu"),
        }
    )
    fallback_calls = []

    rendered, hits = apply_lexicon_overlay(
        "one two",
        lookup,
        lambda text: fallback_calls.append(text) or text,
    )

    assert rendered == "wʌn tu"
    assert len(hits) == 2
    assert fallback_calls == []


def test_adjacent_misses_are_coalesced_into_one_fallback_call():
    lookup = MappingLookup({})
    fallback_calls = []

    rendered, hits = apply_lexicon_overlay(
        "alpha, beta?",
        lookup,
        lambda text: fallback_calls.append(text) or f"[{text}]",
    )

    assert rendered == "[alpha, beta?]"
    assert fallback_calls == ["alpha, beta?"]
    assert hits == ()


def test_ordered_lexicons_use_the_first_configured_hit():
    first = MappingLookup({"one": pronunciation("one", "fɜːst", lexicon_id="first")})
    second = MappingLookup(
        {
            "one": pronunciation("one", "sɛkənd", lexicon_id="second"),
            "two": pronunciation("two", "tu", lexicon_id="second"),
        }
    )
    lookup = OrderedLexiconLookup((first, second))

    matches = lookup.lookup_many(("one", "two"), tag="noun")

    assert [match.lexicon_id for match in matches if match is not None] == ["first", "second"]
    assert first.calls == [(("one", "two"), "noun")]
    assert second.calls == [(("two",), "noun")]


def test_fallback_can_be_disabled_with_a_focused_miss_error():
    lookup = MappingLookup({})
    fallback_calls = []

    with pytest.raises(LexiconMissError, match="unknown"):
        apply_lexicon_overlay(
            "unknown",
            lookup,
            lambda text: fallback_calls.append(text) or text,
            fallback=False,
        )
    assert fallback_calls == []


def test_resource_errors_are_not_treated_as_misses():
    lookup = MappingLookup({})
    lookup.error = LexiconResourceError("invalid asset")

    with pytest.raises(LexiconResourceError, match="invalid asset"):
        apply_lexicon_overlay("unknown", lookup, lambda text: text)


def test_invalid_lookup_batch_is_a_resource_error():
    class BadLookup(MappingLookup):
        def lookup_many(self, words, *, tag=None):
            return ()

    with pytest.raises(LexiconResourceError, match="batch length"):
        apply_lexicon_overlay("word", BadLookup({}), lambda text: text)


def test_unsupported_encoding_is_a_resource_error():
    lookup = MappingLookup({"word": pronunciation("word", "wɜːd", encoding="espeak-ipa3")})

    with pytest.raises(LexiconResourceError, match="encoding"):
        apply_lexicon_overlay("word", lookup, lambda text: text)


def test_unencodable_ipa_hit_uses_the_inflect_symbol_error():
    lookup = MappingLookup({"word": pronunciation("word", "@")})

    with InflectG2P(backend=CapturingBackend(), lexicon_backend=lookup) as g2p:
        with pytest.raises(MissingSymbolError) as error:
            g2p.phonemize_prepared("word")
    assert error.value.symbol == "@"


class CapturingBackend:
    def __init__(self):
        self.seen = []

    def phonemize(self, text: str, *, voice: str) -> str:
        self.seen.append(text)
        return "ab"

    def phonemize_many(self, texts, *, voice: str):
        self.seen.extend(texts)
        return ["ab" for _ in texts]

    def close(self):
        raise AssertionError("Injected backend is caller-owned.")


def test_frontend_uses_injected_lexicon_and_keeps_it_caller_owned():
    lexicon = MappingLookup({"word": pronunciation("word", "ab")})
    backend = CapturingBackend()

    with InflectG2P(backend=backend, lexicon_backend=lexicon) as g2p:
        result = g2p.phonemize_prepared("word")

    assert result.phonemes == "ab"
    assert result.lexicon_hits[0].word == "word"
    assert backend.seen == []
    assert lexicon.close_count == 0


def test_frontend_closes_an_internally_created_lookup(monkeypatch):
    lexicon = MappingLookup({})
    monkeypatch.setattr("inflectg2p.api.create_lookup", lambda *_args, **_kwargs: lexicon)
    g2p = InflectG2P(backend=CapturingBackend(), lexicons=("en-us:fixture",))

    g2p.close()
    g2p.close()

    assert lexicon.close_count == 1


def test_fallback_cannot_be_disabled_without_a_lexicon():
    with pytest.raises(ValueError, match="requires a lexicon"):
        InflectG2P(backend=CapturingBackend(), use_espeak_fallback=False)


def test_lexicon_only_frontend_does_not_construct_espeak():
    lookup = MappingLookup({"word": pronunciation("word", "ab")})
    g2p = InflectG2P(lexicon_backend=lookup, use_espeak_fallback=False)

    result = g2p.phonemize_prepared("word")
    g2p.close()

    assert result.phonemes == "ab"
    assert g2p._backend is None
