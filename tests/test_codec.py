import hashlib

import pytest

from inflectg2p.codec import encode_phonemes, intersperse_blanks, phoneme_ids
from inflectg2p.errors import MissingSymbolError
from inflectg2p.symbols import BLANK_ID, SPACE_ID, SYMBOL_TO_ID, SYMBOLS


def test_symbol_inventory_snapshot_and_duplicate_mapping():
    assert len(SYMBOLS) == 178
    assert hashlib.sha256("".join(SYMBOLS).encode()).hexdigest() == (
        "3e81afeec2d0906de3d7acf2214d32fbc066be8218d2edafe355255391ea92f7"
    )
    apostrophe_ids = [index for index, symbol in enumerate(SYMBOLS) if symbol == "'"]
    assert apostrophe_ids == [174, 176]
    assert SYMBOL_TO_ID["'"] == apostrophe_ids[-1]


def test_blank_and_space_ids_are_fixed():
    assert BLANK_ID == 0
    assert SPACE_ID == 16
    assert SYMBOL_TO_ID[" "] == SPACE_ID


def test_encode_known_symbols_and_blank_framing():
    ids = encode_phonemes("ab")
    assert ids == (SYMBOL_TO_ID["a"], SYMBOL_TO_ID["b"])
    assert intersperse_blanks(ids) == (BLANK_ID, ids[0], BLANK_ID, ids[1], BLANK_ID)
    assert len(intersperse_blanks(ids)) == 2 * len(ids) + 1


def test_space_is_encoded_as_an_inflect_symbol():
    assert encode_phonemes("a b") == (
        SYMBOL_TO_ID["a"],
        SPACE_ID,
        SYMBOL_TO_ID["b"],
    )


def test_unsupported_symbol_has_positioned_package_error():
    with pytest.raises(MissingSymbolError) as error:
        encode_phonemes("a🙂")
    assert error.value.symbol == "🙂"
    assert error.value.position == 1


def test_empty_phoneme_stream_policy():
    assert encode_phonemes("") == ()
    with pytest.raises(ValueError, match="no speakable tokens"):
        phoneme_ids("")
