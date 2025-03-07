from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

@app.route('/get-subtitles', methods=['POST'])
def ytcaption():
    data = request.get_json()
    video_url = data.get("videourl")
    if not video_url:
        return jsonify({"error": "videourl is required"}), 400
    try:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", video_url)
        if match:
            video_id = match.group(1)
        else:
            return jsonify({"error": "Invalid YouTube URL"}), 400
        # Fetch Japanese subtitles
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
        return transcript
    except TranscriptsDisabled as e:
        print(f"TranscriptsDisabled: {e}", flush=True)
        return jsonify({"error": "Subtitles are disabled for this video."}), 400
    except NoTranscriptFound as e:
        print(f"NoTranscriptFound: {e}", flush=True)
        return jsonify({"error": "Japanese subtitles not found for this video."}), 404
    except Exception as e:
        print(f"Unexpected error: {e}", flush=True)
        return jsonify({"error": "An unexpected error occurred while fetching subtitles."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')