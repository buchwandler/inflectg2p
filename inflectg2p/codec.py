from __future__ import annotations

from .errors import MissingSymbolError
from .symbols import BLANK_ID, SYMBOL_TO_ID


def encode_phonemes(phoneme_text: str) -> tuple[int, ...]:
    """Encode IPA and punctuation using the Inflect symbol inventory."""
    ids: list[int] = []
    for position, symbol in enumerate(phoneme_text):
        try:
            ids.append(SYMBOL_TO_ID[symbol])
        except KeyError:
            raise MissingSymbolError(symbol, position) from None
    return tuple(ids)


def intersperse_blanks(token_ids: tuple[int, ...]) -> tuple[int, ...]:
    """Add Inflect's blank/pad ID before, between, and after symbol IDs."""
    output = [BLANK_ID] * (len(token_ids) * 2 + 1)
    output[1::2] = token_ids
    return tuple(output)


def phoneme_ids(phoneme_text: str) -> tuple[int, ...]:
    """Encode phonemes and apply Inflect's blank framing."""
    ids = encode_phonemes(phoneme_text)
    if not ids:
        raise ValueError("The phoneme stream contains no speakable tokens.")
    return intersperse_blanks(ids)
