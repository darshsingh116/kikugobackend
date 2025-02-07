from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import gemini
import vocab_selection
from nlp import extract_japanese_content
import ytCaptions

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# In-memory storage for chat sessions.
# Each session stores its own conversation history and vocab data.
chat_sessions = {}


@app.route('/start', methods=['POST'])
def start_conversation():
    """
    Starts a new conversation for a client.
    Expected JSON payload must include:
      - session_id (str)
      - data_json (list): vocab data sent by the client in JSON format.
      - user_api (dict): configuration for the user's Gemini API instance.
    """
    payload = request.json
    session_id = payload.get('session_id')
    data_json = payload.get('data_json')
    user_api_key = payload.get('user_api')

    print(user_api_key)
    
    if user_api_key is None or data_json is None or session_id is None:
        return jsonify({"error": "session_id, data_json and user_api are required"}), 400

   
    
    # Initiate a new conversation using provided vocab data and an empty history.
    response_text, updated_history, updated_data_json, randomBackendSelectedVocabList, totalScoreIncremented = gemini.initiate_conversation(user_api_key, data_json)
    
    # Save the updated history and vocab data for the session.
    chat_sessions[session_id] = {
        "history": updated_history,
        "data_json": updated_data_json,
    }
    
    extractedJapaneseContents = extract_japanese_content(response_text)
    
    return jsonify({
        "session_id": session_id,
        "response": response_text,
        "extractedJapaneseContents": extractedJapaneseContents,
        "data_json": updated_data_json,
        "history": updated_history,
        "randomBackendSelectedVocabList": randomBackendSelectedVocabList,
        "totalScoreIncremented": totalScoreIncremented
    })

@app.route('/respond', methods=['POST'])
def respond():
    """
    Processes a client input message using their conversation history, vocab data,
    and user's Gemini API settings.
    Expected JSON payload must include:
      - session_id (str)
      - input (str): the client's message.
    """
    payload = request.json
    session_id = payload.get('session_id')
    user_input = payload.get('input')
    user_api_key = payload.get('user_api')
    data_json = payload.get('data_json')
    history = payload.get('history')
    randomBackendSelectedVocabList = payload.get('randomBackendSelectedVocabList')
    print(f"session_id: {session_id}")
    
    if not session_id or not user_input:
        return jsonify({"error": "session_id and input are required"}), 400
    
    if session_id not in chat_sessions:
        print(f"Invalid session_id {session_id}")
        return jsonify({"error": "Invalid session_id"}), 404
    
    

    # Get response from Gemini AI using the provided history and vocab data.
    response_text, updated_history, updated_data_json, totalScoreIncremented = gemini.get_response(user_api_key, data_json, history, user_input, randomBackendSelectedVocabList)
    
    # Update session with new history and vocab data.
    chat_sessions[session_id]["history"] = updated_history
    chat_sessions[session_id]["data_json"] = updated_data_json
    
    extractedJapaneseContents = extract_japanese_content(response_text)
    
    return jsonify({
        "session_id": session_id,
        "response": response_text,
        "extractedJapaneseContents": extractedJapaneseContents,
        "data_json": updated_data_json,
        "history": updated_history,
        "totalScoreIncremented": totalScoreIncremented
    })

@app.route('/vocab/all', methods=['GET'])
def get_all_user_vocab():
    """
    API endpoint to return all vocabulary data.
    """
    try:
        vocab_data = vocab_selection.get_all_vocab_data()
        return jsonify(vocab_data), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-subtitles', methods=['GET'])
async def get_subtitles():
    print("Request received")
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"error": "Please provide a video_id parameter."}), 400
    try:
        # Get processed subtitles asynchronously
        subtitles_data = await ytCaptions.get_processed_subtitles(video_id)
        
        # Return data as JSON
        if "error" in subtitles_data:
            return jsonify(subtitles_data), 404
        return jsonify(subtitles_data)
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)