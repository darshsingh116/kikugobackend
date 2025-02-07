import re
from sudachipy import Dictionary, Tokenizer

# Initialize tokenizer
tokenizer = Dictionary().create()
mode = Tokenizer.SplitMode.C  # Standard mode

# English mapping for part-of-speech tags
pos_mapping = {
    "代名詞": "Pronoun",
    "助詞": "Particle",
    "名詞": "Noun",
    "動詞": "Verb",
    "助動詞": "Auxiliary Verb",
    "補助記号": "Punctuation"
}

# Regex pattern to check if a word contains only Japanese characters
japanese_pattern = re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF]+')  
# Hiragana (3040–309F), Katakana (30A0–30FF), Kanji (4E00–9FFF)

def extract_vocab(sentence):
    # Process tokens
    tokens = tokenizer.tokenize(sentence, mode)
    cleaned_tokens = []

    for token in tokens:
        word = token.surface()
        normalized = token.normalized_form()
        pos_japanese = token.part_of_speech()[0]  # Main part of speech
        pos_english = pos_mapping.get(pos_japanese, "Other")  # Convert to English
        
        # **Exclude non-Japanese words**
        if japanese_pattern.search(word):  # If the word contains Japanese characters
            cleaned_tokens.append((word, normalized, pos_english))

    return cleaned_tokens


def extract_japanese_content(text):
    pattern = re.compile(r'[ぁ-んァ-ン一ー-龥、。,\s]+')
    segments = pattern.findall(text)
    # Remove empty entries and strip extra spaces
    segments = [seg.strip() for seg in segments if seg.strip()]
    return segments