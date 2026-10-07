from inflectg2p import InflectG2P

with InflectG2P() as g2p:
    result = g2p.phonemize_prepared("Hello, world.")

print(result.phonemes)
print(result.token_ids)
