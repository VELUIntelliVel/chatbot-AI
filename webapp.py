from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# Allow requests from any origin

# Conva.ai API Configuration
API_KEY = "0c4d8e49f1244043408a7cced81993aa"
CHARACTER_ID = "32a6a8bc-b656-11ef-b082-42010a7be016"
SESSION_ID = -1

# User-agent for Wikipedia requests
user_agent = 'ChatbotAI/1.0 (no-website.com; contact@placeholder.com)'

@app.route("/", methods=["GET"])
def home():
    return render_template("chatbot.html")

def get_wikipedia_summary(query):
    """Fetches a summary from Wikipedia for the given query."""
    url = 'https://en.wikipedia.org/w/api.php'
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
        response = requests.post(url, headers=headers, json=payload)
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
        # Check for Wikipedia query
        if "what is" in user_message.lower() or "explain" in user_message.lower():
            query = user_message.split("what is")[-1].strip()
            bot_response = get_wikipedia_summary(query)
        else:
            bot_response = send_request_to_convai(user_message)

        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["GET"])
def chat_get():
    return "This endpoint only supports POST requests.", 405

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
