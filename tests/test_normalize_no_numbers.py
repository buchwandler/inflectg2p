from inflectg2p import normalize_text


def test_punctuation_and_abbreviation_normalization_without_optional_runtime_calls():
    assert normalize_text("Dr. Smith—hello") == "doctor Smith, hello"
    assert normalize_text("USB-C works") == "you ess bee see works"
