from flask import Flask, request, jsonify
from flask_cors import CORS
from langdetect import detect, LangDetectException
from googletrans import Translator
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Translator and API Configurations
translator = Translator()
API_KEY = "0c4d8e49f1244043408a7cced81993aa"
CHARACTER_ID = "32a6a8bc-b656-11ef-b082-42010a7be016"
SESSION_ID = -1

# Helper Functions
def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def translate_text(text, target_lang="en"):
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception:
        return text  # Return the original text if translation fails

def send_request_to_convai(user_input):
    url = "https://api.convai.com/character/getResponse"
    headers = {"CONVAI-API-KEY": API_KEY}
    payload = {
        "userText": user_input,
        "charID": CHARACTER_ID,
        "sessionID": SESSION_ID,
        "voiceResponse": "false"
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("text", "No response available.")
    except requests.exceptions.RequestException:
        return "Error communicating with the chatbot service."

# Routes
@app.route("/")
def health_check():
    return "Service is live!", 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request. 'message' is required."}), 400

        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400

        # Detect language and translate if necessary
        detected_lang = detect_language(user_message)
        user_message_translated = translate_text(user_message, target_lang="en") if detected_lang != "en" else user_message

        # Get chatbot response
        bot_response = send_request_to_convai(user_message_translated)

        # Translate response back to user's language if needed
        final_response = translate_text(bot_response, target_lang=detected_lang) if detected_lang != "en" else bot_response

        return jsonify({"response": final_response}), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Main
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
