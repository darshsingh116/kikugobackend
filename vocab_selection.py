import random
from nlp import extract_vocab  # Import the extract_vocab function from nlp.py

# THIS IS PRIMARY MAIN COURSE ORIENTED VOCAB MANAGER

def select_random_words(data_json):
    """
    Accepts data as a JSON object (Python list of dictionaries) and returns 10 random Japanese words.
    
    Parameters:
        data_json (list): List of dictionaries containing the vocab data.
        
    Returns:
        list: A list of 10 randomly selected Japanese words.
    """
    try:
        if not data_json:
            raise ValueError("Provided JSON data is empty.")
        random_rows = random.sample(data_json, min(10, len(data_json)))
        return [row["japanese"] for row in random_rows]
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def update_word_scores(data_json, sentence):
    """
    Updates the scores of words in the provided JSON data by incrementing them by 1.
    The data is expected to be a list of dictionaries and the word list extracted from the sentence 
    should be in the format:
        [('水', '水', 'Noun'), ('ペットボトル', 'ペットボトル', 'Noun'), ...]
    
    Parameters:
        data_json (list): List of dictionaries containing the vocab data.
        sentence (str): The sentence from which to extract vocab.
        
    Returns:
        list: The updated JSON data.
    """
    try:
        word_list = extract_vocab(sentence)
        # Create a mapping from Japanese word to its row index for faster lookup
        word_index_map = {row["japanese"]: idx for idx, row in enumerate(data_json)}
        totalScoreIncremented = 0
        for word, _, _ in word_list:
            if word in word_index_map:
                idx = word_index_map[word]
                current_score = int(data_json[idx].get("score", "0"))
                data_json[idx]["score"] = str(current_score + 1)
                totalScoreIncremented += 1

        return data_json , totalScoreIncremented
    except Exception as e:
        raise Exception(f"An error occurred: {e}")