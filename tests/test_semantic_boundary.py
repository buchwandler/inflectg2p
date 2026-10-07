from pathlib import Path


def test_core_contains_no_semantic_preparation_or_runtime_setup():
    package_root = Path(__file__).parents[1] / "inflectg2p"
    forbidden = (
        "num2words",
        "phonemizer",
        "espeakng_loader",
        "_configure_espeak",
        "ABBREVIATIONS",
        "WORD_OVERRIDES",
        "PHONEME_OVERRIDES",
        "PUNCT_TRANSLATION",
        "normalize_text",
        "_expand_",
        "numeralform",
        "spokenform",
        "abbr2words",
    )
    source = "\n".join(path.read_text() for path in package_root.rglob("*.py"))
    assert not [name for name in forbidden if name in source]
