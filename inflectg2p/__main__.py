from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .frontend import run_frontend


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Inflect v2 English text frontend")
    parser.add_argument("text")
    args = parser.parse_args()
    result = run_frontend(args.text)
    print(json.dumps(asdict(result), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
