"""Prepared-text phoneme and token-ID frontend for Inflect v2."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

from .api import InflectG2P, phoneme_ids, phonemes, phonemize_prepared
from .codec import encode_phonemes, intersperse_blanks
from .config import InflectG2PConfig
from .errors import (
    BackendError,
    BackendUnavailableError,
    InflectG2PError,
    LexiconDependencyError,
    LexiconError,
    LexiconMissError,
    LexiconResourceError,
    MissingSymbolError,
    PhonemizationError,
)
from .lexicons import available_lexicons, lexicon_info
from .symbols import BLANK_ID, SPACE_ID, SYMBOL_TO_ID, SYMBOLS
from .types import LexiconHit, PhonemizeResult

try:
    __version__ = _distribution_version("inflectg2p")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "__version__",
    "BackendError",
    "BackendUnavailableError",
    "BLANK_ID",
    "InflectG2P",
    "InflectG2PConfig",
    "InflectG2PError",
    "LexiconDependencyError",
    "LexiconError",
    "LexiconHit",
    "LexiconMissError",
    "LexiconResourceError",
    "MissingSymbolError",
    "PhonemizeResult",
    "PhonemizationError",
    "SPACE_ID",
    "SYMBOLS",
    "SYMBOL_TO_ID",
    "available_lexicons",
    "encode_phonemes",
    "intersperse_blanks",
    "lexicon_info",
    "phoneme_ids",
    "phonemes",
    "phonemize_prepared",
]
