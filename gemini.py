import json
import requests
from base_prompts import basePromptWithVocab
from vocab_selection import select_random_words, update_word_scores

# Generation settings (used as fallback, if needed)
generation_config = {
    "temperature": 1,
    "topP": 0.95,
    "topK": 40,
    "maxOutputTokens": 8192,
    "responseMimeType": "text/plain",
}

def initiate_conversation(user_api_key, data_json):
    """
    Initializes a new conversation for a client using the user's provided Gemini API instance,
    vocab data (JSON), and conversation history.

    Parameters:
        user_api_key (str): The user's API key.
        data_json (list): List of dictionaries containing the vocab data.
        history (list): Client-provided conversation history.

    Returns:
        tuple: (response_text, updated_history, updated_data_json)
    """
    # Generate vocab list from data_json.
    randomBackendSelectedVocabList = select_random_words(data_json)

    # Prepare the system instruction with the vocab list.
    system_instruction = basePromptWithVocab.format(items=randomBackendSelectedVocabList)

    # API endpoint
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent"

    # Request payload
    payload = {
        "systemInstruction": {
            "role": "system",
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": generation_config,
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": "start"}
                ]
            }
        ]
    }

    # Add API key to the URL
    url_with_key = f"{url}?key={user_api_key}"

    # Send the request
    response = requests.post(url_with_key, headers={"Content-Type": "application/json"}, json=payload)
    history = []
    # Process the response
    if response.status_code == 200:
        response_data = response.json()
        response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]

        # Update vocab data using response text.
        updated_data_json, totalScoreIncremented = update_word_scores(data_json, response_text)
        updated_history = history + [response_text]

        return response_text, updated_history, updated_data_json, randomBackendSelectedVocabList, totalScoreIncremented
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


def get_response(user_api_key, data_json, history, user_input, randomBackendSelectedVocabList):
    """
    Processes a client input using the user's Gemini API instance,
    the current vocab data, and conversation history.

    Parameters:
        user_api_key (str): The user's API key.
        data_json (list): List of dictionaries containing the vocab data.
        history (list): Current conversation history.
        user_input (str): The client's input message.

    Returns:
        tuple: (response_text, updated_history, updated_data_json)
    """

    # Prepare the system instruction with the vocab list.
    system_instruction = basePromptWithVocab.format(items=randomBackendSelectedVocabList)

    # API endpoint
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent"

    # Build the conversation history
    contents = []
    for i, message in enumerate(history):
        message_str = str(message)
        role = "user" if i % 2 == 0 else "model"
        contents.append({
            "role": role,
            "parts": [{"text": message_str}]
        })

    # Add the latest user input
    contents.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })

    # Request payload
    payload = {
        "systemInstruction": {
            "role": "system",
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": generation_config,
        "contents": contents
    }

    # Add API key to the URL
    url_with_key = f"{url}?key={user_api_key}"

    # Send the request
    response = requests.post(url_with_key, headers={"Content-Type": "application/json"}, json=payload)

    # Process the response
    if response.status_code == 200:
        response_data = response.json()
        response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        try:
            further_response_text = json.loads(response_text)
            further_response_text = further_response_text["text"]
            response_text = further_response_text
            print("assistant format found and parsed")
        except:
            pass

        print(response_data)
        print(response_text)

        # Update vocab data based on response text.
        updated_data_json, totalScoreIncremented = update_word_scores(data_json, response_text)
        updated_history = history + [response_text]

        return response_text, updated_history, updated_data_json, totalScoreIncremented
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")