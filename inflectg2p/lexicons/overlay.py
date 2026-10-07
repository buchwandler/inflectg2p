from __future__ import annotations

from collections.abc import Callable

from ..errors import LexiconError, LexiconMissError, LexiconResourceError
from ..types import LexiconHit, LexiconPronunciation
from .base import PronunciationLookup, normalize_phoneme_encoding
from .spans import scan_source_spans


def apply_lexicon_overlay(
    text: str,
    lookup: PronunciationLookup,
    phonemize_text: Callable[[str], str],
    *,
    tag: str | None = None,
    fallback: bool = True,
) -> tuple[str, tuple[LexiconHit, ...]]:
    spans = scan_source_spans(text)
    words = tuple(span.text for span in spans if span.kind == "word")
    if not words:
        return text, ()
    try:
        matches = lookup.lookup_many(words, tag=tag)
    except LexiconError:
        raise
    except Exception as exc:
        raise LexiconResourceError("Pronunciation lookup failed.") from exc
    if len(matches) != len(words):
        raise LexiconResourceError("Pronunciation lookup returned an invalid batch length.")

    output: list[str] = []
    pending: list[str] = []
    pending_has_miss = False
    word_index = 0
    lexicon_hits: list[LexiconHit] = []

    def flush_pending() -> None:
        nonlocal pending_has_miss
        if not pending:
            return
        source_text = "".join(pending)
        output.append(phonemize_text(source_text) if pending_has_miss else source_text)
        pending.clear()
        pending_has_miss = False

    for span in spans:
        if span.kind == "other":
            pending.append(span.text)
            continue

        pronunciation = matches[word_index]
        word_index += 1
        if pronunciation is None:
            if not fallback:
                raise LexiconMissError(
                    f"No pronunciation for {span.text!r} in configured lexicons."
                )
            pending.append(span.text)
            pending_has_miss = True
            continue
        if not isinstance(pronunciation, LexiconPronunciation):
            raise LexiconResourceError("Pronunciation lookup returned an invalid value.")
        if not pronunciation.pronunciation:
            raise LexiconResourceError(f"Lexicon pronunciation for {span.text!r} is empty.")
        try:
            encoding = normalize_phoneme_encoding(pronunciation.source_encoding)
            if pronunciation.provenance is not None:
                provenance_encoding = normalize_phoneme_encoding(
                    pronunciation.provenance.source_encoding
                )
                if encoding != provenance_encoding:
                    raise ValueError("pronunciation and provenance encodings disagree")
        except ValueError as exc:
            raise LexiconResourceError(
                f"Unsupported or inconsistent pronunciation encoding for {span.text!r}."
            ) from exc

        flush_pending()
        output.append(pronunciation.pronunciation)
        lexicon_hits.append(
            LexiconHit(
                word=span.text,
                pronunciation=pronunciation.pronunciation,
                source=pronunciation.source,
                lexicon_id=pronunciation.lexicon_id,
                matched_key=pronunciation.matched_key or span.text,
                source_encoding=encoding,
                provenance=pronunciation.provenance,
            )
        )

    flush_pending()
    return "".join(output), tuple(lexicon_hits)
