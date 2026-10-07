from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BUILD = ROOT / "build" / "docs"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build inflectg2p documentation.")
    parser.add_argument("target", choices=("html", "clean"), nargs="?", default="html")
    target = parser.parse_args().target
    if target == "clean":
        shutil.rmtree(BUILD, ignore_errors=True)
        return 0
    output = BUILD / target
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", target, str(DOCS), str(output)],
        cwd=ROOT,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
