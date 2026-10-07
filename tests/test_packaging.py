import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_release_artifacts",
    ROOT / "tools" / "check_release_artifacts.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)
check_release_artifacts = CHECKER.check_release_artifacts


def write_wheel(dist_dir: Path, version: str, extra_requirements: tuple[str, ...] = ()) -> None:
    wheel = dist_dir / f"inflectg2p-{version}-py3-none-any.whl"
    dist_info = f"inflectg2p-{version}.dist-info"
    requirements = "\n".join(
        ["Requires-Dist: espeakng-runtime>=0.1.5,<0.2"]
        + [f"Requires-Dist: {requirement}" for requirement in extra_requirements]
    )
    metadata = (
        "Metadata-Version: 2.4\n"
        "Name: inflectg2p\n"
        f"Version: {version}\n"
        "Requires-Python: >=3.10\n"
        f"{requirements}\n\n"
    )
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("inflectg2p/__init__.py", "")
        archive.writestr("inflectg2p/__main__.py", "")
        archive.writestr("inflectg2p/py.typed", "")
        archive.writestr(f"{dist_info}/METADATA", metadata)
        archive.writestr(f"{dist_info}/WHEEL", "Wheel-Version: 1.0\nRoot-Is-Purelib: true\n")
        archive.writestr(
            f"{dist_info}/entry_points.txt",
            "[console_scripts]\ninflectg2p = inflectg2p.__main__:main\n",
        )


def write_sdist(dist_dir: Path, version: str, *, include_tool: bool = True) -> None:
    sdist = dist_dir / f"inflectg2p-{version}.tar.gz"
    root = f"inflectg2p-{version}"
    files = {
        "README.md": "# inflectg2p\n",
        "LICENSE": "license\n",
        "NOTICE": "notice\n",
        "pyproject.toml": "[project]\n",
        "docs/index.md": "# docs\n",
        "examples/basic_usage.py": "pass\n",
        "inflectg2p/__init__.py": "",
        "inflectg2p/py.typed": "",
        "PKG-INFO": (
            "Metadata-Version: 2.4\n"
            "Name: inflectg2p\n"
            f"Version: {version}\n"
            "Requires-Python: >=3.10\n\n"
        ),
    }
    if include_tool:
        files["tools/check_release_artifacts.py"] = "pass\n"
    with tarfile.open(sdist, "w:gz") as archive:
        for relative_path, content in files.items():
            data = content.encode("utf-8")
            member = tarfile.TarInfo(f"{root}/{relative_path}")
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))


def create_dist(
    dist_dir: Path,
    version: str = "0.1.0",
    extra_requirements: tuple[str, ...] = (),
    *,
    include_tool: bool = True,
) -> None:
    dist_dir.mkdir(parents=True, exist_ok=True)
    write_wheel(dist_dir, version, extra_requirements)
    write_sdist(dist_dir, version, include_tool=include_tool)


def test_release_artifact_checker_accepts_a_complete_matching_pair(tmp_path):
    create_dist(tmp_path)

    check_release_artifacts(tmp_path, expected_version="0.1.0")


@pytest.mark.parametrize(
    "dependency",
    (
        "phonemizer>=3",
        "abbr2words>=1; extra == 'dev'",
    ),
)
def test_release_artifact_checker_rejects_removed_dependencies(tmp_path, dependency):
    create_dist(tmp_path, extra_requirements=(dependency,))

    with pytest.raises(ValueError, match="removed dependencies"):
        check_release_artifacts(tmp_path)


def test_release_artifact_checker_rejects_wrong_tag_version(tmp_path):
    create_dist(tmp_path, version="0.1.1")

    with pytest.raises(ValueError, match="expected 0.1.0"):
        check_release_artifacts(tmp_path, expected_version="0.1.0")


def test_release_artifact_checker_rejects_incomplete_sdist(tmp_path):
    create_dist(tmp_path, include_tool=False)

    with pytest.raises(ValueError, match="missing required files"):
        check_release_artifacts(tmp_path)
