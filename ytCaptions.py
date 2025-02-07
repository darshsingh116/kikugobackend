import asyncio
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from sudachipy import Dictionary, Tokenizer
from googletrans import Translator

# Initialize SudachiPy dictionary and Google Translator
tokenizer = Dictionary(dict="core").create()
translator = Translator()

# Define a set of common Japanese grammar particles and functional words
GRAMMAR_PARTICLES = {"は", "の", "が", "に", "を", "と", "で", "へ", "や", "も", "か", "ね", "よ", "さ", "な", "わ", "ぜ", "ぞ"}

async def get_japanese_subtitles(video_id):
    try:
        # Fetch Japanese subtitles
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound):
        return {"error": "Japanese subtitles not available for this video."}

async def translate_word_with_retry(word, cache, max_retries=3):
    """
    Translate a word with retry logic.
    Retries up to `max_retries` times if the translation is empty or fails.
    """
    if word in GRAMMAR_PARTICLES:
        return ""  # Skip translation for grammar particles
    
    if word in cache:
        return cache[word]  # Use cached translation if available

    for attempt in range(max_retries):
        try:
            translation = (await translator.translate(word, src='ja', dest='en')).text
            if translation:  # Only accept non-empty translations
                cache[word] = translation
                return translation
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for word '{word}': {e}")
            pass
        
        await asyncio.sleep(1)  # Wait before retrying to avoid overwhelming the API

    # If all retries fail, log the issue and return an empty string
    # print(f"Failed to translate word after {max_retries} attempts: {word}")
    cache[word] = ""  # Cache the failure to avoid future retries
    return ""

async def tokenize_and_translate(text, translation_cache):
    # Tokenize Japanese text using SudachiPy
    tokens = tokenizer.tokenize(text)
    words = [token.surface() for token in tokens]  # Get all tokens
    
    # Translate words in parallel while preserving order
    translation_tasks = [translate_word_with_retry(word, translation_cache) for word in words]
    word_translations = await asyncio.gather(*translation_tasks)
    
    # Pair each word with its translation (or empty string if missing)
    word_translation_pairs = [
        {"word": word, "translation": translation}
        for word, translation in zip(words, word_translations)
    ]
    
    # Translate the full sentence
    try:
        sentence_translation = (await translator.translate(text, src='ja', dest='en')).text
    except Exception:
        sentence_translation = ""  # Handle sentence translation failure gracefully
    
    return {
        "original": text,
        "words": word_translation_pairs,  # List of word-translation pairs in order
        "sentence_translation": sentence_translation
    }

async def process_captions(transcript):
    processed_data = []
    translation_cache = {}  # Cache for word translations
    
    # Process subtitles in parallel
    tasks = [tokenize_and_translate(entry['text'], translation_cache) for entry in transcript]
    translation_results = await asyncio.gather(*tasks)
    
    for entry, translation_data in zip(transcript, translation_results):
        processed_data.append({
            "start": entry['start'],
            "duration": entry['duration'],
            "original": translation_data["original"],
            "words": translation_data["words"],  # Ordered list of word-translation pairs
            "sentence_translation": translation_data["sentence_translation"]
        })
    return processed_data

async def get_processed_subtitles(video_id):
    # Fetch subtitles
    transcript = await get_japanese_subtitles(video_id)
    
    # Check if subtitles are available
    if "error" in transcript:
        return transcript
    
    # Process subtitles
    processed_data = await process_captions(transcript)
    return processed_data