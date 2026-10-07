import json

import pytest

import inflectg2p.__main__ as cli
from inflectg2p import PhonemizationError, PhonemizeResult


class FakeG2P:
    instances = []

    def __init__(self, config, **kwargs):
        self.config = config
        self.kwargs = kwargs
        self.text = None
        self.__class__.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def phonemize_prepared(self, text):
        self.text = text
        return PhonemizeResult(text, "ab", (0, 50, 0))


def test_cli_emits_json_and_forwards_runtime_and_lexicon_options(monkeypatch, capsys):
    FakeG2P.instances.clear()
    monkeypatch.setattr(cli, "InflectG2P", FakeG2P)
    text = "Pay $12.50 at 9:05 AM."

    status = cli.main(
        [
            "--espeak-mode",
            "cli",
            "--executable",
            "/opt/bin/espeak-ng",
            "--data",
            "/opt/share/espeak-ng-data",
            "--timeout",
            "2.5",
            "--lexicon",
            "en-us:company",
            "--lexicon",
            "./local.g2lex",
            "--no-espeak-fallback",
            text,
        ]
    )

    instance = FakeG2P.instances[0]
    payload = json.loads(capsys.readouterr().out)
    assert status == 0
    assert payload == {
        "text": text,
        "phonemes": "ab",
        "token_ids": [0, 50, 0],
        "token_count": 3,
    }
    assert instance.text == text
    assert instance.config.espeak_mode == "cli"
    assert instance.config.executable == "/opt/bin/espeak-ng"
    assert instance.config.data == "/opt/share/espeak-ng-data"
    assert instance.config.timeout == 2.5
    assert instance.kwargs["lexicons"] == ["en-us:company", "./local.g2lex"]
    assert instance.kwargs["use_espeak_fallback"] is False


def test_cli_reports_package_errors_without_a_traceback(monkeypatch, capsys):
    class FailingG2P(FakeG2P):
        def phonemize_prepared(self, _text):
            raise PhonemizationError("backend unavailable")

    monkeypatch.setattr(cli, "InflectG2P", FailingG2P)

    status = cli.main(["Hello."])

    captured = capsys.readouterr()
    assert status == 2
    assert captured.out == ""
    assert captured.err == "inflectg2p: backend unavailable\n"


def test_cli_rejects_removed_normalization_option(capsys):
    with pytest.raises(SystemExit) as error:
        cli.main(["--normalize", "Hello"])

    assert error.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
