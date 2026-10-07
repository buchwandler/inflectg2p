from inflectg2p.frontend import encode_phonemes, intersperse_blanks
from inflectg2p.symbols import BLANK_ID, SYMBOL_TO_ID


def test_inflect_blank_interspersion_matches_upstream_contract():
    ids = encode_phonemes("ab")
    assert ids == (SYMBOL_TO_ID["a"], SYMBOL_TO_ID["b"])
    assert intersperse_blanks(ids) == (BLANK_ID, ids[0], BLANK_ID, ids[1], BLANK_ID)
