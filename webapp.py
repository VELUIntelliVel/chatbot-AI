import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from googletrans import Translator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Translator and API Configurations
translator = Translator()
API_KEY = "0c4d8e49f1244043408a7cced81993aa"
CHARACTER_ID = "32a6a8bc-b656-11ef-b082-42010a7be016"
SESSION_ID = -1

# User-agent for Wikipedia
user_agent = 'ChatbotAI/1.0 (no-website.com; contact@placeholder.com)'

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
    except Exception as e:
        return f"Translation error: {str(e)}"

def get_wikipedia_summary(query):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {'action': 'query', 'format': 'json', 'prop': 'extracts', 'exintro': True, 'titles': query}
    headers = {'User-Agent': user_agent}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        if 'extract' in page:
            return page['extract']
        return "No relevant information found on Wikipedia for this query."
    except Exception as e:
        return f"Error fetching data from Wikipedia: {str(e)}"

def send_request_to_convai(user_input):
    url = "https://api.convai.com/character/getResponse"
    headers = {"CONVAI-API-KEY": API_KEY}
    payload = {"userText": user_input, "charID": CHARACTER_ID, "sessionID": SESSION_ID, "voiceResponse": "false"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("text", "No response available.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Conva.ai: {str(e)}"

# Routes
@app.route("/")
def health_check():
    return "Service is live!", 200

@app.route("/chat", methods=["POST"])
@cross_origin()
def chat():
    try:
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "Invalid request. 'message' is required."}), 400

        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400

        # Process the message (example response for now)
        bot_response = send_request_to_convai(user_message)

        return jsonify({"response": bot_response}), 200
    except Exception as e:
        app.logger.error(f"Error in /chat: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500



        # Log detected language
        detected_lang = detect_language(user_message)
        print(f"Detected language: {detected_lang}")

        user_message_translated = translate_text(user_message, target_lang="en") if detected_lang != "en" else user_message

        # Log translation
        print(f"Translated user message: {user_message_translated}")

        if "what is" in user_message_translated.lower() or "explain" in user_message_translated.lower():
            query = user_message_translated.split("what is")[-1].strip()
            bot_response = get_wikipedia_summary(query)
        else:
            bot_response = send_request_to_convai(user_message_translated)

        bot_response_translated = translate_text(bot_response, target_lang=detected_lang) if detected_lang != "en" else bot_response

        # Log bot response
        print(f"Bot response: {bot_response_translated}")

        return jsonify({"response": bot_response_translated})

    except Exception as e:
        print(f"Error in /chat endpoint: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Main
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
