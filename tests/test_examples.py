import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize(
    ("example", "arguments"),
    [
        ("basic_usage.py", ()),
        ("backend_modes.py", ("--mode", "auto")),
        ("result_inspection.py", ()),
        ("custom_backend.py", ()),
    ],
)
def test_examples_without_lexicon_assets_run(example, arguments):
    subprocess.run(
        [sys.executable, str(ROOT / "examples" / example), *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
