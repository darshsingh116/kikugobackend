import re
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from sudachipy import Dictionary, Tokenizer
from googletrans import Translator

# Initialize SudachiPy dictionary and Google Translator
tokenizer = Dictionary(dict="core").create()
translator = Translator()

async def get_japanese_subtitles(video_id):
    try:
        # Fetch Japanese subtitles (limit to first 10 entries for testing)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound):
        return {"error": "Japanese subtitles not available for this video."}

async def translate_word(word, cache):
    # Use a cache to avoid redundant translations
    if word not in cache:
        cache[word] = (await translator.translate(word, src='ja', dest='en')).text
    return cache[word]

async def tokenize_and_translate(text, translation_cache):
    # Tokenize Japanese text using SudachiPy
    tokens = tokenizer.tokenize(text)
    words = [token.surface() for token in tokens if len(token.surface()) > 1]  # Filter short words
    
    # Translate words in parallel
    word_translations = await asyncio.gather(*[translate_word(word, translation_cache) for word in words])
    word_translations = dict(zip(words, word_translations))
    
    # Translate the full sentence
    sentence_translation = (await translator.translate(text, src='ja', dest='en')).text
    
    return {
        "original": text,
        "words": word_translations,
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
            "words": translation_data["words"],
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




































############UNOPTIMIZED INITIAL CODE############


# import re
# import asyncio
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# from sudachipy import Dictionary, Tokenizer
# from googletrans import Translator

# # Initialize SudachiPy dictionary and Google Translator
# tokenizer = Dictionary(dict="core").create()
# translator = Translator()

# async def get_japanese_subtitles(video_id):
#     try:
#         # Fetch Japanese subtitles
#         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
#         return transcript[:10]
#     except (TranscriptsDisabled, NoTranscriptFound):
#         return {"error": "Japanese subtitles not available for this video."}

# async def tokenize_and_translate(text):
#     # Tokenize Japanese text using SudachiPy
#     tokens = tokenizer.tokenize(text)
#     words = [token.surface() for token in tokens]
    
#     # Translate individual words asynchronously
#     word_translations = {
#         word: (await translator.translate(word, src='ja', dest='en')).text
#         for word in words
#     }
#     sentence_translation = (await translator.translate(text, src='ja', dest='en')).text
    
#     return {
#         "original": text,
#         "words": word_translations,
#         "sentence_translation": sentence_translation
#     }

# async def process_captions(transcript):
#     processed_data = []
#     for entry in transcript:
#         text = entry['text']
#         start = entry['start']
#         duration = entry['duration']
        
#         # Tokenize and translate each caption asynchronously
#         translation_data = await tokenize_and_translate(text)
        
#         processed_data.append({
#             "start": start,
#             "duration": duration,
#             "original": translation_data["original"],
#             "words": translation_data["words"],
#             "sentence_translation": translation_data["sentence_translation"]
#         })
#     return processed_data

# async def get_processed_subtitles(video_id):
#     # Fetch subtitles
#     transcript = await get_japanese_subtitles(video_id)
    
#     # Check if subtitles are available
#     if "error" in transcript:
#         return transcript
    
#     # Process subtitles
#     processed_data = await process_captions(transcript)
#     return processed_data