import builtins
import sys
from types import ModuleType

import pytest

from inflectg2p import LexiconDependencyError, LexiconResourceError
from inflectg2p.lexicons import G2LexLookup, LexiconPronunciation, LexphonLookup
from inflectg2p.lexicons.registry import available_lexicons, lexicon_info


def metadata(**overrides):
    return {
        "id": "en-us:fixture",
        "language": "en-US",
        "kind": "pronunciation",
        "phoneme_encoding": "ipa",
        "data_version": "1",
        **overrides,
    }


def install_mock_module(monkeypatch, name, **attributes):
    module = ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    monkeypatch.setitem(sys.modules, name, module)
    return module


class FakeAsset:
    def __init__(self, values, metadata_value=None):
        self.values = values
        self.metadata = metadata_value or metadata()
        self.calls = []
        self.close_count = 0

    def lookup(self, word, *, tag=None):
        self.calls.append((word, tag))
        return self.values.get(word)

    def close(self):
        self.close_count += 1


def test_g2lex_preserves_order_tag_and_asset_provenance(tmp_path, monkeypatch):
    first_path = tmp_path / "first.g2lex"
    second_path = tmp_path / "second.g2lex"
    first_path.touch()
    second_path.touch()
    first = FakeAsset({"word": "wɜːd"}, metadata(id="first", data_version="v1"))
    second = FakeAsset({"word": "second"}, metadata(id="second", data_version="v2"))
    assets = {first_path: first, second_path: second}
    install_mock_module(monkeypatch, "g2lex", open=lambda path: assets[path])
    lookup = G2LexLookup((first_path, second_path), language="en-US")

    result = lookup.lookup("word", tag="noun")
    lookup.close()
    lookup.close()

    assert result.pronunciation == "wɜːd"
    assert result.lexicon_id == "first"
    assert result.matched_key == "word"
    assert result.source_encoding == "ipa"
    assert result.provenance.data_version == "v1"
    assert first.calls == [("word", "noun")]
    assert second.calls == []
    assert first.close_count == second.close_count == 1


@pytest.mark.parametrize(
    ("metadata_overrides", "message"),
    [
        ({"language": "de-DE"}, "language"),
        ({"kind": "grapheme"}, "kind"),
        ({"phoneme_encoding": "espeak-ipa3"}, "encoding"),
    ],
)
def test_g2lex_rejects_incompatible_asset_metadata(
    tmp_path,
    monkeypatch,
    metadata_overrides,
    message,
):
    path = tmp_path / "invalid.g2lex"
    path.touch()
    asset = FakeAsset({}, metadata(**metadata_overrides))
    install_mock_module(monkeypatch, "g2lex", open=lambda _: asset)
    lookup = G2LexLookup((path,), language="en-US")

    with pytest.raises(LexiconResourceError, match=message):
        lookup.lookup("word")
    assert asset.close_count == 1


def test_g2lex_missing_file_has_a_focused_resource_error(tmp_path):
    lookup = G2LexLookup((tmp_path / "missing.g2lex",), language="en-US")
    with pytest.raises(LexiconResourceError, match="does not exist"):
        lookup.lookup("word")


def test_missing_g2lex_dependency_has_an_actionable_error(tmp_path, monkeypatch):
    path = tmp_path / "asset.g2lex"
    path.touch()
    monkeypatch.delitem(sys.modules, "g2lex", raising=False)
    original_import = builtins.__import__

    def import_without_g2lex(name, *args, **kwargs):
        if name == "g2lex":
            raise ImportError("not installed")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_g2lex)
    with pytest.raises(LexiconDependencyError, match=r"inflectg2p\[g2lex\]"):
        G2LexLookup((path,)).lookup("word")


class FakeStore:
    def __init__(self, records, paths):
        self.records = records
        self.paths = paths
        self.install_calls = 0

    def metadata(self, identifier):
        return self.records[identifier]

    def path(self, identifier):
        return self.paths[identifier]

    def installed(self):
        return tuple(self.records.values())

    def install(self, _artifact):
        self.install_calls += 1
        raise AssertionError("Lookup must never install lexicon assets.")


class FakeG2LexLookup:
    def __init__(self, paths, *, language):
        self.paths = tuple(paths)
        self.language = language
        self.calls = []
        self.close_count = 0

    def lookup(self, word, *, tag=None):
        self.calls.append((word, tag))
        if word != "word":
            return None
        return LexiconPronunciation(
            pronunciation="wɜːd",
            source=f"g2lex:{self.paths[0]}",
            matched_key=word,
        )

    def close(self):
        self.close_count += 1


def test_lexphon_uses_only_installed_store_data_and_forwards_tag(tmp_path, monkeypatch):
    identifier = "en-us:fixture"
    path = tmp_path / "fixture.g2lex"
    path.touch()
    store = FakeStore({identifier: metadata()}, {identifier: path})
    inner = FakeG2LexLookup((path,), language="en-US")
    install_mock_module(monkeypatch, "lexphon")
    monkeypatch.setattr("inflectg2p.lexicons.lexphon.G2LexLookup", lambda paths, **kwargs: inner)
    lookup = LexphonLookup("en-US", (identifier,), store=store)

    result = lookup.lookup("word", tag="noun")
    lookup.close()

    assert result.source == f"lexphon:{identifier}"
    assert result.lexicon_id == identifier
    assert result.provenance.asset_path == str(path)
    assert inner.calls == [("word", "noun")]
    assert inner.close_count == 1
    assert store.install_calls == 0


@pytest.mark.parametrize(
    ("metadata_overrides", "message"),
    [
        ({"language": "de-DE"}, "language"),
        ({"kind": "grapheme"}, "kind"),
        ({"phoneme_encoding": "espeak-ipa3"}, "encoding"),
    ],
)
def test_lexphon_rejects_invalid_catalog_metadata(
    tmp_path,
    monkeypatch,
    metadata_overrides,
    message,
):
    identifier = "en-us:fixture"
    path = tmp_path / "fixture.g2lex"
    path.touch()
    store = FakeStore({identifier: metadata(**metadata_overrides)}, {identifier: path})
    install_mock_module(monkeypatch, "lexphon")
    monkeypatch.setattr(
        "inflectg2p.lexicons.lexphon.G2LexLookup",
        lambda *_args, **_kwargs: pytest.fail("Invalid metadata must be rejected first."),
    )
    lookup = LexphonLookup("en-US", (identifier,), store=store)

    with pytest.raises(LexiconResourceError, match=message):
        lookup.lookup("word")
    assert store.install_calls == 0


def test_missing_lexphon_dependency_has_an_actionable_error(monkeypatch):
    monkeypatch.delitem(sys.modules, "lexphon", raising=False)
    original_import = builtins.__import__

    def import_without_lexphon(name, *args, **kwargs):
        if name == "lexphon":
            raise ImportError("not installed")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_lexphon)
    with pytest.raises(LexiconDependencyError, match=r"inflectg2p\[lexphon\]"):
        LexphonLookup("en-US", ("en-us:fixture",)).lookup("word")


def test_registry_lists_and_inspects_provisioned_assets_without_installing(tmp_path):
    identifier = "en-us:lexhint"
    path = tmp_path / "lexhint.g2lex"
    path.touch()
    store = FakeStore(
        {
            identifier: metadata(id=identifier),
            "de-de:fixture": metadata(id="de-de:fixture", language="de-DE"),
            "en-us:graphemes": metadata(id="en-us:graphemes", kind="grapheme"),
        },
        {identifier: path},
    )

    assert available_lexicons("en-US", store=store) == ("lexhint",)
    info = lexicon_info("en-US", "lexhint", store=store)
    assert info["id"] == identifier
    assert info["asset_path"] == str(path)
    assert store.install_calls == 0
