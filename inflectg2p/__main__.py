from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .api import InflectG2P
from .config import InflectG2PConfig
from .errors import InflectG2PError


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=("Phonemize prepared English text for the Inflect v2 symbol/token-ID frontend.")
    )
    parser.add_argument("text", help="prepared, speakable English text")
    parser.add_argument("--espeak-mode", choices=("auto", "native", "cli"), default="auto")
    parser.add_argument("--executable")
    parser.add_argument("--library")
    parser.add_argument("--data")
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--lexicon", action="append", dest="lexicons")
    parser.add_argument("--no-espeak-fallback", action="store_true")
    arguments = parser.parse_args(argv)

    try:
        config = InflectG2PConfig(
            espeak_mode=arguments.espeak_mode,
            executable=arguments.executable,
            library=arguments.library,
            data=arguments.data,
            timeout=arguments.timeout,
        )
        with InflectG2P(
            config,
            lexicons=arguments.lexicons,
            use_espeak_fallback=not arguments.no_espeak_fallback,
        ) as g2p:
            result = g2p.phonemize_prepared(arguments.text)
    except (InflectG2PError, ValueError) as exc:
        print(f"inflectg2p: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "text": result.text,
                "phonemes": result.phonemes,
                "token_ids": list(result.token_ids),
                "token_count": result.token_count,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
