from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_sdist_filename, parse_wheel_filename
from packaging.version import Version

FORBIDDEN_DEPENDENCIES = {
    "phonemizer",
    "espeakng-loader",
    "num2words",
    "numeralform",
    "spokenform",
    "abbr2words",
}
WHEEL_EXCLUDED_PATHS = {
    ".github",
    ".ledger",
    ".venv",
    "build",
    "dist",
    "docs",
    "examples",
    "tests",
    "tools",
}
SDIST_EXCLUDED_PATHS = {".github", ".ledger", ".venv", "build", "dist"}
SDIST_REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "NOTICE",
    "pyproject.toml",
    "docs/index.md",
    "examples/basic_usage.py",
    "tools/check_release_artifacts.py",
    "inflectg2p/__init__.py",
    "inflectg2p/py.typed",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _check_version(actual: Version, expected: str | None, label: str) -> None:
    if expected is not None:
        _require(actual == Version(expected), f"{label} version is {actual}, expected {expected}.")


def _check_wheel(path: Path, expected_version: str | None) -> Version:
    name, filename_version, _build, _tags = parse_wheel_filename(path.name)
    _require(canonicalize_name(name) == "inflectg2p", f"Unexpected wheel distribution: {name}.")
    _check_version(filename_version, expected_version, "Wheel")

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        _require("inflectg2p/__init__.py" in names, "Wheel is missing inflectg2p/__init__.py.")
        _require("inflectg2p/__main__.py" in names, "Wheel is missing inflectg2p/__main__.py.")
        _require("inflectg2p/py.typed" in names, "Wheel is missing inflectg2p/py.typed.")
        _require(
            any(name.startswith("inflectg2p/") and name.endswith(".py") for name in names),
            "Wheel contains no inflectg2p Python modules.",
        )
        for member in names:
            parts = set(PurePosixPath(member).parts)
            _require(
                not parts.intersection(WHEEL_EXCLUDED_PATHS),
                f"Wheel contains development-only path {member!r}.",
            )

        metadata_files = [
            member
            for member in names
            if PurePosixPath(member).name == "METADATA"
            and PurePosixPath(member).parent.name.endswith(".dist-info")
        ]
        _require(
            len(metadata_files) == 1,
            "Wheel must contain exactly one dist-info/METADATA file.",
        )
        metadata = Parser().parsestr(archive.read(metadata_files[0]).decode("utf-8"))
        _require(
            canonicalize_name(metadata.get("Name", "")) == "inflectg2p",
            "Wheel METADATA has an unexpected distribution name.",
        )
        metadata_version = Version(metadata.get("Version", "0"))
        _require(
            metadata_version == filename_version,
            "Wheel filename and METADATA versions differ.",
        )
        _require(
            metadata.get("Requires-Python") == ">=3.10",
            "Wheel Requires-Python must be >=3.10.",
        )

        requirements = [Requirement(value) for value in metadata.get_all("Requires-Dist", [])]
        forbidden = {
            canonicalize_name(str(requirement.name))
            for requirement in requirements
            if canonicalize_name(str(requirement.name)) in FORBIDDEN_DEPENDENCIES
        }
        _require(
            not forbidden,
            f"Wheel metadata contains removed dependencies: {sorted(forbidden)}.",
        )
        core_dependencies = {
            canonicalize_name(str(requirement.name))
            for requirement in requirements
            if requirement.marker is None or requirement.marker.evaluate({"extra": ""})
        }
        _require(
            core_dependencies == {"espeakng-runtime"},
            f"Unexpected core dependencies: {sorted(core_dependencies)}.",
        )

        entry_point_files = [
            member
            for member in names
            if PurePosixPath(member).name == "entry_points.txt"
            and PurePosixPath(member).parent.name.endswith(".dist-info")
        ]
        _require(len(entry_point_files) == 1, "Wheel must contain one entry_points.txt.")
        entry_points = archive.read(entry_point_files[0]).decode("utf-8")
        _require(
            "inflectg2p = inflectg2p.__main__:main" in entry_points,
            "Wheel is missing the inflectg2p console script.",
        )
    return filename_version


def _check_sdist(path: Path, expected_version: str | None) -> Version:
    name, filename_version = parse_sdist_filename(path.name)
    _require(canonicalize_name(name) == "inflectg2p", f"Unexpected sdist distribution: {name}.")
    _check_version(filename_version, expected_version, "Sdist")

    with tarfile.open(path, "r:*") as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
        roots = {PurePosixPath(member.name).parts[0] for member in members}
        expected_root = f"inflectg2p-{filename_version}"
        _require(roots == {expected_root}, f"Sdist must have one {expected_root!r} root directory.")
        files: set[str] = set()
        for member in members:
            parts = PurePosixPath(member.name).parts
            _require(
                not set(parts).intersection(SDIST_EXCLUDED_PATHS),
                f"Sdist contains a development-only path {member.name!r}.",
            )
            _require(
                "__pycache__" not in parts and ".git" not in parts,
                f"Sdist contains a local cache or Git metadata path {member.name!r}.",
            )
            files.add(PurePosixPath(*parts[1:]).as_posix())
        missing = SDIST_REQUIRED_FILES.difference(files)
        pkg_info_members = [
            member
            for member in members
            if PurePosixPath(member.name).relative_to(expected_root) == PurePosixPath("PKG-INFO")
        ]
        _require(len(pkg_info_members) == 1, "Sdist must contain one PKG-INFO file.")
        pkg_info = archive.extractfile(pkg_info_members[0])
        _require(pkg_info is not None, "Could not read sdist PKG-INFO.")
        source_metadata = Parser().parsestr(pkg_info.read().decode("utf-8"))
        _require(
            canonicalize_name(source_metadata.get("Name", "")) == "inflectg2p",
            "Sdist PKG-INFO has an unexpected distribution name.",
        )
        _require(
            Version(source_metadata.get("Version", "0")) == filename_version,
            "Sdist filename and PKG-INFO versions differ.",
        )
        _require(
            source_metadata.get("Requires-Python") == ">=3.10",
            "Sdist Requires-Python must be >=3.10.",
        )
        _require(not missing, f"Sdist is missing required files: {sorted(missing)}.")
    return filename_version


def check_release_artifacts(dist_dir: Path, expected_version: str | None = None) -> None:
    _require(dist_dir.is_dir(), f"Distribution directory does not exist: {dist_dir}.")
    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    _require(len(wheels) == 1, f"Expected exactly one wheel, found {len(wheels)}.")
    _require(len(sdists) == 1, f"Expected exactly one sdist, found {len(sdists)}.")

    wheel_version = _check_wheel(wheels[0], expected_version)
    sdist_version = _check_sdist(sdists[0], expected_version)
    _require(wheel_version == sdist_version, "Wheel and sdist versions differ.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check built inflectg2p release artifacts.")
    parser.add_argument("dist", type=Path, nargs="?", default=Path("dist"))
    parser.add_argument("--expected-version")
    arguments = parser.parse_args(argv)
    try:
        check_release_artifacts(arguments.dist, arguments.expected_version)
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(f"release artifact check failed: {exc}", file=sys.stderr)
        return 1

    version_note = (
        f" for version {arguments.expected_version}" if arguments.expected_version else ""
    )
    print(f"release artifacts validated{version_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
