from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from langdetect import detect
from googletrans import Translator
from concurrent.futures import ThreadPoolExecutor

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

def detect_language(text):
    """Detects the language of the given text."""
    return detect(text)

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
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        if 'extract' in page:
            return page['extract']
        else:
            return "No Wikipedia page found for the given query."
    else:
        return "Error: Failed to fetch data from Wikipedia."

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
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get("text", "No response available.")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

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
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
