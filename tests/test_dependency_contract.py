import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def test_public_import_does_not_require_optional_lexicon_packages():
    script = """
import builtins

original_import = builtins.__import__
def reject_optional(name, *args, **kwargs):
    level = kwargs.get('level', args[3] if len(args) > 3 else 0)
    if level == 0 and name.split('.', 1)[0] in {'g2lex', 'lexphon'}:
        raise AssertionError(f'optional package imported during startup: {name}')
    return original_import(name, *args, **kwargs)

builtins.__import__ = reject_optional
import inflectg2p
assert inflectg2p.InflectG2P
"""
    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )


def test_core_dependency_metadata_and_optional_lexicon_extras():
    pyproject_path = Path(__file__).parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())
    project = pyproject["project"]
    dependencies = project["dependencies"]
    names = {
        re.match(r"[A-Za-z0-9_.-]+", dependency).group().casefold() for dependency in dependencies
    }

    assert names == {"espeakng-runtime"}
    extras = project["optional-dependencies"]
    assert extras["lexicons"] == extras["lexphon"]
    assert any(dependency.startswith("g2lex") for dependency in extras["g2lex"])
    assert any(dependency.startswith("lexphon") for dependency in extras["lexphon"])
