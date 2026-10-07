from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class SourceSpan:
    text: str
    start: int
    end: int
    kind: Literal["word", "other"]


_APOSTROPHES = frozenset(("'", "’", "ʼ", "＇"))
_HYPHENS = frozenset(("-", "‐", "‑", "‒", "–", "—", "−"))


def _is_word_character(value: str) -> bool:
    return bool(value) and unicodedata.category(value)[0] in {"L", "N"}


def _is_combining(value: str) -> bool:
    return bool(value) and unicodedata.category(value).startswith("M")


def _word_end(text: str, start: int) -> int:
    position = start
    while position < len(text):
        character = text[position]
        if _is_word_character(character) or _is_combining(character):
            position += 1
        elif character in _APOSTROPHES | _HYPHENS:
            next_position = position + 1
            if next_position < len(text) and _is_word_character(text[next_position]):
                position += 1
            else:
                break
        else:
            break
    return position


def scan_source_spans(text: str) -> tuple[SourceSpan, ...]:
    """Scan words while retaining every punctuation and whitespace span."""
    spans: list[SourceSpan] = []
    position = 0
    while position < len(text):
        if _is_word_character(text[position]):
            end = _word_end(text, position)
            spans.append(SourceSpan(text[position:end], position, end, "word"))
            position = end
            continue
        start = position
        position += 1
        while position < len(text) and not _is_word_character(text[position]):
            position += 1
        spans.append(SourceSpan(text[start:position], start, position, "other"))
    return tuple(spans)


def word_spans(text: str) -> tuple[SourceSpan, ...]:
    return tuple(span for span in scan_source_spans(text) if span.kind == "word")
