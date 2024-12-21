import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from googletrans import Translator
import json

app = Flask(__name__)
CORS(app)

# Initialize Translator
translator = Translator()

# Conva.ai API Configuration
API_KEY = "0c4d8e49f1244043408a7cced81993aa"
CHARACTER_ID = "32a6a8bc-b656-11ef-b082-42010a7be016"
SESSION_ID = -1

# User-agent for Wikipedia requests
user_agent = 'ChatbotAI/1.0 (no-website.com; contact@placeholder.com)'

# Define functions before using them in the routes
def detect_language(text):
    """Detects the language of the given text."""
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def translate_text(text, target_lang="en"):
    """Translates text into the target language."""
    translated = translator.translate(text, dest=target_lang)
    return translated.text

def get_wikipedia_summary(query):
    """Fetches a summary from Wikipedia for the given query using requests."""
    url = f'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'exintro': True,
        'titles': query
    }

    headers = {'User-Agent': user_agent}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        if 'extract' in page:
            return page['extract']
        else:
            return "No relevant information found on Wikipedia for this query."
    except Exception as e:
        return f"Error fetching data from Wikipedia: {e}"

def send_request_to_convai(user_input):
    """Sends a request to the Conva.ai API."""
    url = "https://api.convai.com/character/getResponse"
    headers = {"CONVAI-API-KEY": API_KEY}
    payload = {
        "userText": user_input,
        "charID": CHARACTER_ID,
        "sessionID": SESSION_ID,
        "voiceResponse": "false"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)  # Use json=payload
        response.raise_for_status()
        return response.json().get("text", "No response available.")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Define the routes after function definitions

@app.route("/")
def health_check():
    """Health check route for the application."""
    return "Service is live!", 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Detect user language
        detected_lang = detect_language(user_message)

        # Translate user message to English if necessary
        if detected_lang != "en":
            user_message_translated = translate_text(user_message, target_lang="en")
        else:
            user_message_translated = user_message

        # Determine whether to fetch from Wikipedia or use Conva.ai
        if "what is" in user_message_translated.lower() or "explain" in user_message_translated.lower():
            # Assume general knowledge question and fetch from Wikipedia
            query = user_message_translated.split("what is")[-1].strip()
            bot_response = get_wikipedia_summary(query)
        else:
            # Otherwise, use Conva.ai for character responses
            bot_response = send_request_to_convai(user_message_translated)

        # Translate response back to user language
        if detected_lang != "en":
            bot_response_translated = translate_text(bot_response, target_lang=detected_lang)
        else:
            bot_response_translated = bot_response

        return jsonify({"response": bot_response_translated})

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Test the API from within the script (this runs only if the script is executed directly)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

    # Send a test POST request to the Flask API
    url = "http://127.0.0.1:5000/chat"
    headers = {"Content-Type": "application/json"}
    data = {"message": "Hello, how are you?"}

    response = requests.post(url, headers=headers, json=data)
    print(response.json())
