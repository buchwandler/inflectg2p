from inflectg2p import InflectG2P

with InflectG2P(lexicons=("en-us:lexhint",)) as g2p:
    result = g2p.phonemize_prepared("Saskatchewan is fluorescent.")

print(result.phonemes)
print(result.token_ids)
print(result.lexicon_hits)
