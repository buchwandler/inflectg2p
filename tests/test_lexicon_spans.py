from inflectg2p.lexicons.spans import scan_source_spans, word_spans


def test_source_scanner_retains_every_source_character_and_span():
    text = "  O’Neil's well-known cafe\u0301, 42! "
    spans = scan_source_spans(text)

    assert "".join(span.text for span in spans) == text
    assert all(text[span.start : span.end] == span.text for span in spans)
    assert [span.text for span in word_spans(text)] == [
        "O’Neil's",
        "well-known",
        "cafe\u0301",
        "42",
    ]


def test_apostrophes_and_hyphens_only_join_internal_word_characters():
    text = "'start end' end-"
    assert [span.text for span in word_spans(text)] == ["start", "end", "end"]
