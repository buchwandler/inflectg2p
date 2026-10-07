import argparse

from inflectg2p import InflectG2P, InflectG2PConfig

parser = argparse.ArgumentParser()
parser.add_argument("text", nargs="?", default="Hello, world.")
parser.add_argument("--mode", choices=("auto", "native", "cli"), default="auto")
args = parser.parse_args()

config = InflectG2PConfig(espeak_mode=args.mode)
with InflectG2P(config) as g2p:
    result = g2p.phonemize_prepared(args.text)

print(result.phonemes)
print(result.token_ids)
