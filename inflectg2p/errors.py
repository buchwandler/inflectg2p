class InflectG2PError(Exception):
    """Base class for package errors."""


class BackendError(InflectG2PError):
    """Base class for phoneme backend errors."""


class BackendUnavailableError(BackendError):
    """No usable phoneme backend is available."""


class PhonemizationError(BackendError):
    """A backend could not phonemize the supplied prepared text."""


class LexiconError(InflectG2PError):
    """Base class for lexicon errors."""


class LexiconDependencyError(LexiconError):
    """An optional lexicon integration is unavailable."""


class LexiconResourceError(LexiconError):
    """A configured lexicon resource is missing or invalid."""


class LexiconMissError(LexiconError):
    """No configured lexicon contains a requested word."""


class MissingSymbolError(InflectG2PError, ValueError):
    """A phoneme stream contains a symbol absent from the Inflect inventory."""

    def __init__(self, symbol: str, position: int) -> None:
        self.symbol = symbol
        self.position = position
        super().__init__(f"Unsupported phoneme symbol {symbol!r} at position {position}.")
