from __future__ import annotations

from .codec import phoneme_ids
from .types import LexiconHit, PhonemizeResult


def result_from_phonemes(
    text: str,
    phonemes: str,
    lexicon_hits: tuple[LexiconHit, ...] = (),
) -> PhonemizeResult:
    """Build a model-ready result from unchanged prepared text and phonemes."""
    return PhonemizeResult(
        text=text,
        phonemes=phonemes,
        token_ids=phoneme_ids(phonemes),
        lexicon_hits=lexicon_hits,
    )
