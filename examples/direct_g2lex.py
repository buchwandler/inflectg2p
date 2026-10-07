import argparse

from inflectg2p import InflectG2P
from inflectg2p.lexicons import G2LexLookup

parser = argparse.ArgumentParser()
parser.add_argument("asset", help="path to an explicitly provisioned .g2lex file")
parser.add_argument("text", help="prepared, speakable text")
args = parser.parse_args()

lookup = G2LexLookup([args.asset], language="en-US")
try:
    with InflectG2P(lexicon_backend=lookup) as g2p:
        result = g2p.phonemize_prepared(args.text)
finally:
    lookup.close()

print(result.phonemes)
print(result.lexicon_hits)
