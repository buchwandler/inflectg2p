from collections.abc import Sequence

from inflectg2p import InflectG2P


class FixedBackend:
    def phonemize(self, text: str, *, voice: str) -> str:
        print(f"Received unchanged text for {voice}: {text!r}")
        return "həlˈoʊ, wˈɜːld."

    def phonemize_many(self, texts: Sequence[str], *, voice: str) -> list[str]:
        return [self.phonemize(text, voice=voice) for text in texts]

    def close(self) -> None:
        print("Caller closes the injected backend.")


backend = FixedBackend()
g2p = InflectG2P(backend=backend)
try:
    result = g2p.phonemize_prepared("Hello, world.")
finally:
    g2p.close()
    backend.close()

print(result.phonemes)
print(result.token_ids)
