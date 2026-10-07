from inflectg2p import InflectG2P

text = "Hello, world."
with InflectG2P() as g2p:
    result = g2p.phonemize_prepared(text)

print("prepared text:", result.text)
print("phonemes:", result.phonemes)
print("token IDs:", result.token_ids)
print("token count:", result.token_count)
print("lexicon hits:", result.lexicon_hits)
