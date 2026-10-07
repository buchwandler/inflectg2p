from importlib.metadata import PackageNotFoundError, version

import inflectg2p


def test_public_version_matches_distribution_metadata():
    try:
        expected = version("inflectg2p")
    except PackageNotFoundError:
        expected = "0+unknown"
    assert inflectg2p.__version__ == expected
