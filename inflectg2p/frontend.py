from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

from .symbols import BLANK_ID, SYMBOL_TO_ID
from .types import FrontendResult

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

WORD_OVERRIDES = {
    "Qwen3": "Qwen three",
    "Qwen": "Qwen",
    "PyTorch": "pie torch",
    "SQLite": "ess cue lite",
    "USB-C": "you ess bee see",
    "RTX 3060": "ar tee ex thirty sixty",
    "RTX 3090": "ar tee ex thirty ninety",
    "RTX 4090": "ar tee ex forty ninety",
    "RTX 5080": "ar tee ex fifty eighty",
    "RTX 5090": "ar tee ex fifty ninety",
}

LETTER_NAMES = {
    "A": "ay",
    "B": "bee",
    "C": "see",
    "D": "dee",
    "E": "ee",
    "F": "eff",
    "G": "gee",
    "H": "aitch",
    "I": "eye",
    "J": "jay",
    "K": "kay",
    "L": "ell",
    "M": "em",
    "N": "en",
    "O": "oh",
    "P": "pee",
    "Q": "cue",
    "R": "ar",
    "S": "ess",
    "T": "tee",
    "U": "you",
    "V": "vee",
    "W": "double you",
    "X": "ex",
    "Y": "why",
    "Z": "zee",
}

ABBREVIATIONS = {
    "Dr.": "doctor",
    "Mr.": "mister",
    "Mrs.": "missus",
    "Ms.": "miss",
    "Prof.": "professor",
    "St.": "saint",
    "vs.": "versus",
    "etc.": "et cetera",
    "e.g.": "for example",
    "i.e.": "that is",
}

PUNCT_TRANSLATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": ", ",
        "\u2026": "...",
        "(": ", ",
        ")": ", ",
        "[": ", ",
        "]": ", ",
        "{": ", ",
        "}": ", ",
    }
)

PHONEME_OVERRIDES = {
    "sˈæskɐtʃˌuːən": "sɐskˈætʃəwən",
    "flʊɹɹˈɛsənt": "flʊˈɹɛsənt",
}

_ESPEAK_CONFIGURED = False


def _num2words(value: int | float, *, ordinal: bool = False) -> str:
    from num2words import num2words

    if ordinal:
        text = num2words(value, to="ordinal")
    else:
        text = num2words(value)
    return str(text).replace("-", " ").replace(",", "")


def _digit_words(text: str) -> str:
    return " ".join(_num2words(int(ch)) for ch in text if ch.isdigit())


def _identifier_digits(text: str) -> str:
    words: list[str] = []
    for index, character in enumerate(text):
        if not character.isdigit():
            continue
        words.append("oh" if character == "0" and index > 0 else _num2words(int(character)))
    return " ".join(words)


def _expand_identifier_token(token: str) -> str:
    match = re.fullmatch(r"([A-Za-z]?)(\d+)([A-Za-z]?)", token)
    if match is None:
        return token
    prefix, digits, suffix = match.groups()
    pieces: list[str] = []
    if prefix:
        pieces.append(LETTER_NAMES[prefix.upper()])
    if len(digits) == 3 or digits.startswith("0"):
        pieces.append(_identifier_digits(digits))
    else:
        pieces.append(_num2words(int(digits)))
    if suffix:
        pieces.append(LETTER_NAMES[suffix.upper()])
    return " ".join(pieces)


def _expand_labeled_identifier(match: re.Match[str]) -> str:
    return f"{match.group(1)} {_expand_identifier_token(match.group(2))}"


def _expand_street_number(match: re.Match[str]) -> str:
    return _identifier_digits(match.group(1))


def _expand_money(match: re.Match[str]) -> str:
    raw = match.group(1).replace(",", "")
    dollars, _, cents = raw.partition(".")
    dollar_count = int(dollars)
    parts = [_num2words(dollar_count), "dollar" if dollar_count == 1 else "dollars"]
    if cents:
        cents = cents[:2].ljust(2, "0")
        cent_count = int(cents)
        if cent_count:
            parts.extend(["and", _num2words(cent_count), "cent" if cent_count == 1 else "cents"])
    return " ".join(parts)


def _expand_date_slash(match: re.Match[str]) -> str:
    month = int(match.group(1))
    day = int(match.group(2))
    year = int(match.group(3))
    try:
        date(year, month, day)
    except ValueError:
        return match.group(0)
    return f"{MONTHS[month - 1]} {_num2words(day, ordinal=True)} {_num2words(year)}"


def _expand_time(match: re.Match[str]) -> str:
    hour = int(match.group(1))
    minute = int(match.group(2))
    suffix = match.group(3) or ""
    pieces = [_num2words(hour)]
    if minute == 0:
        pieces.append("o clock")
    elif minute < 10:
        pieces.extend(["oh", _num2words(minute)])
    else:
        pieces.append(_num2words(minute))
    if suffix:
        suffix = suffix.lower().replace(".", "")
        pieces.extend(list(suffix))
    return " ".join(pieces)


def _expand_bare_hour_time(match: re.Match[str]) -> str:
    hour = int(match.group(1))
    suffix = re.sub(r"[^A-Za-z]", "", match.group(2)).lower()
    return f"{_num2words(hour)} {' '.join(suffix)}"


def _expand_version(match: re.Match[str]) -> str:
    return " point ".join(_num2words(int(part)) for part in match.group(0).split("."))


def _expand_decimal(match: re.Match[str]) -> str:
    whole, frac = match.group(1), match.group(2)
    return f"{_num2words(int(whole))} point {_digit_words(frac)}"


def _expand_ordinal(match: re.Match[str]) -> str:
    return _num2words(int(match.group(1)), ordinal=True)


def _expand_number(match: re.Match[str]) -> str:
    value = match.group(0).replace(",", "")
    if len(value) >= 5 and not value.startswith("20"):
        return _digit_words(value)
    return _num2words(int(value))


def _expand_phone(match: re.Match[str]) -> str:
    left, right = match.group(1), match.group(2)
    return f"{_digit_words(left)}, {_digit_words(right)}"


def _expand_acronym(match: re.Match[str]) -> str:
    acronym = match.group(0)
    if len(acronym) <= 1:
        return acronym
    return " ".join(LETTER_NAMES.get(ch, ch) for ch in acronym)


def normalize_text(text: str) -> str:
    text = text.translate(PUNCT_TRANSLATION)
    text = re.sub(r"\s+", " ", text).strip()
    for src, dst in WORD_OVERRIDES.items():
        text = re.sub(rf"\b{re.escape(src)}\b", dst, text)
    for src, dst in ABBREVIATIONS.items():
        text = re.sub(rf"\b{re.escape(src)}", dst, text, flags=re.IGNORECASE)
    text = re.sub(
        r"\b([A-Z])(?:\.([A-Z]))+\.",
        lambda match: " ".join(re.findall(r"[A-Z]", match.group(0))),
        text,
    )
    text = re.sub(
        r"\b(apartment|apt\.?|suite|unit|room|flight|extension|order|invoice|locker|aisle|gate)\s+([A-Za-z]?\d{1,4}[A-Za-z]?)\b",
        _expand_labeled_identifier,
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\b(\d{3})(?=\s+(?:North|South|East|West)\b)",
        _expand_street_number,
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\$(\d[\d,]*(?:\.\d{1,2})?)", _expand_money, text)
    text = re.sub(
        r"\b(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/(20\d{2}|19\d{2})\b",
        _expand_date_slash,
        text,
    )
    text = re.sub(r"\b(\d{1,2}):(\d{2})\s*([AaPp]\.?\s*[Mm]\.?)?\b", _expand_time, text)
    text = re.sub(r"\b(\d{1,2})\s*([AaPp]\.?\s*[Mm]\.?)\b", _expand_bare_hour_time, text)
    text = re.sub(r"\b(\d{3})-(\d{4})\b", _expand_phone, text)
    text = re.sub(r"\b\d+(?:\.\d+){2,}\b", _expand_version, text)
    text = re.sub(r"\b(\d+)\.(\d+)\b", _expand_decimal, text)
    text = re.sub(r"\b(\d+)(st|nd|rd|th)\b", _expand_ordinal, text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d[\d,]*\b", _expand_number, text)
    text = re.sub(r"\b[A-Z]{2,}\b", _expand_acronym, text)
    text = re.sub(r",(?:\s*,)+", ",", text)
    text = re.sub(r",\s*([.!?])", r"\1", text)
    text = re.sub(r"\s+([,;:.!?])", r"\1", text)
    text = re.sub(r"([,;:.!?])(?=\S)", r"\1 ", text)
    return re.sub(r"\s+", " ", text).strip()


def _configure_espeak() -> None:
    global _ESPEAK_CONFIGURED
    if _ESPEAK_CONFIGURED:
        return
    system_libraries = (
        Path("/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1"),
        Path("/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1"),
        Path("/usr/lib64/libespeak-ng.so.1"),
    )
    system_library = next((path for path in system_libraries if path.is_file()), None)
    if system_library is not None:
        os.environ.setdefault("PHONEMIZER_ESPEAK_LIBRARY", str(system_library))
    else:
        import espeakng_loader

        os.environ.setdefault("PHONEMIZER_ESPEAK_LIBRARY", espeakng_loader.get_library_path())
        os.environ.setdefault("ESPEAK_DATA_PATH", espeakng_loader.get_data_path())
        espeakng_loader.make_library_available()
        espeakng_loader.load_library()
    _ESPEAK_CONFIGURED = True


def _apply_phoneme_overrides(phoneme_text: str) -> str:
    for source, replacement in PHONEME_OVERRIDES.items():
        phoneme_text = phoneme_text.replace(source, replacement)
    return re.sub(r"\s+", " ", phoneme_text).strip()


def phonemize_normalized_batch(normalized_texts: list[str], *, jobs: int = 1) -> list[str]:
    if not normalized_texts:
        return []
    _configure_espeak()
    from phonemizer import phonemize

    rendered = phonemize(
        normalized_texts,
        language="en-us",
        backend="espeak",
        strip=True,
        preserve_punctuation=True,
        with_stress=True,
        njobs=jobs,
    )
    if isinstance(rendered, str):
        rendered = [rendered]
    return [_apply_phoneme_overrides(text) for text in rendered]


def phonemize_normalized(normalized_text: str) -> str:
    return phonemize_normalized_batch([normalized_text], jobs=1)[0]


def encode_phonemes(phoneme_text: str) -> tuple[int, ...]:
    return tuple(SYMBOL_TO_ID[symbol] for symbol in phoneme_text)


def intersperse_blanks(token_ids: tuple[int, ...]) -> tuple[int, ...]:
    output = [BLANK_ID] * (len(token_ids) * 2 + 1)
    output[1::2] = token_ids
    return tuple(output)


def phoneme_ids(phoneme_text: str) -> tuple[int, ...]:
    ids = encode_phonemes(phoneme_text)
    if not ids:
        raise ValueError("The text frontend produced no speakable tokens.")
    return intersperse_blanks(ids)


def run_frontend(text: str) -> FrontendResult:
    normalized = normalize_text(text)
    phonemes = phonemize_normalized(normalized)
    return FrontendResult(
        raw_text=text,
        normalized_text=normalized,
        phoneme_text=phonemes,
        token_ids=phoneme_ids(phonemes),
    )


def run_frontend_batch(texts: list[str], *, jobs: int = 1) -> list[FrontendResult]:
    normalized = [normalize_text(text) for text in texts]
    phonemes = phonemize_normalized_batch(normalized, jobs=jobs)
    return [
        FrontendResult(
            raw_text=raw,
            normalized_text=norm,
            phoneme_text=phones,
            token_ids=phoneme_ids(phones),
        )
        for raw, norm, phones in zip(texts, normalized, phonemes, strict=True)
    ]
