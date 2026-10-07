from __future__ import annotations

_PAD = "_"
_PUNCTUATION = ';:,.!?¡¿—…"«»“” '
_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
_LETTERS_IPA = (
    "ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸ"
    "θœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞"
    "↓↑→↗↘'̩'ᵻ"
)

SYMBOLS: tuple[str, ...] = tuple([_PAD, *list(_PUNCTUATION), *list(_LETTERS), *list(_LETTERS_IPA)])
SYMBOL_TO_ID: dict[str, int] = {symbol: index for index, symbol in enumerate(SYMBOLS)}
SPACE_ID = SYMBOLS.index(" ")
BLANK_ID = 0
