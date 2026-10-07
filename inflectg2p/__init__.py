"""Independent Inflect v2 English G2P and token-ID frontend."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

from .api import InflectG2P, phonemize, token_ids
from .frontend import (
    ABBREVIATIONS,
    LETTER_NAMES,
    MONTHS,
    PHONEME_OVERRIDES,
    WORD_OVERRIDES,
    encode_phonemes,
    intersperse_blanks,
    normalize_text,
    phoneme_ids,
    phonemize_normalized,
    phonemize_normalized_batch,
    run_frontend,
    run_frontend_batch,
)
from .symbols import BLANK_ID, SPACE_ID, SYMBOLS, SYMBOL_TO_ID
from .types import FrontendResult

try:
    __version__ = _distribution_version("inflectg2p")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "__version__",
    "ABBREVIATIONS",
    "BLANK_ID",
    "FrontendResult",
    "InflectG2P",
    "LETTER_NAMES",
    "MONTHS",
    "PHONEME_OVERRIDES",
    "SPACE_ID",
    "SYMBOLS",
    "SYMBOL_TO_ID",
    "WORD_OVERRIDES",
    "encode_phonemes",
    "intersperse_blanks",
    "normalize_text",
    "phoneme_ids",
    "phonemize",
    "phonemize_normalized",
    "phonemize_normalized_batch",
    "run_frontend",
    "run_frontend_batch",
    "token_ids",
]
