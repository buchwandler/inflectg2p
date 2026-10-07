import json
from pathlib import Path

from inflectg2p import InflectG2P


class GoldenBackend:
    def __init__(self, phonemes_by_text):
        self.phonemes_by_text = phonemes_by_text

    def phonemize(self, text, *, voice):
        assert voice == "en-us"
        return self.phonemes_by_text[text]

    def phonemize_many(self, texts, *, voice):
        assert voice == "en-us"
        return [self.phonemes_by_text[text] for text in texts]

    def close(self):
        raise AssertionError("Injected backend is caller-owned.")


def test_en_us_golden_phonemes_and_token_ids():
    path = Path(__file__).parent / "goldens" / "inflect_v2_en_us.json"
    cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    phonemes_by_text = {case["text"]: case["phonemes"] for case in cases}
    with InflectG2P(backend=GoldenBackend(phonemes_by_text)) as g2p:
        results = g2p.phonemize_prepared_batch([case["text"] for case in cases])

    assert len(results) == len(cases)
    for result, case in zip(results, cases, strict=True):
        assert result.text == case["text"]
        assert result.phonemes == case["phonemes"]
        assert list(result.token_ids) == case["token_ids"]
