from inflectg2p import available_lexicons, lexicon_info

for name in available_lexicons("en-US"):
    print(name, lexicon_info("en-US", name))
