import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import logging

app = Flask(__name__, static_folder='static')
# Allow requests from all origins
CORS(app, resources={r"/*": {"origins": "https://chatbot-ai-1-zb7c.onrender.com"}})

# Configure API credentials
API_KEY = "0c4d8e49f1244043408a7cced81993aa"
CHARACTER_ID = "32a6a8bc-b656-11ef-b082-42010a7be016"
SESSION_ID = -1

logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET"])
def home():
    logging.debug("Serving chatbot.html")
    return render_template("chatbot.html")

def send_request_to_convai(user_message):
    url = "https://api.convai.com/character/getResponse"
    headers = {"CONVAI-API-KEY": API_KEY}
    payload = {
        "userText": user_message,
        "charID": CHARACTER_ID,
        "sessionID": SESSION_ID,
        "voiceResponse": "false"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.debug(f"ConvAI API Response: {response.json()}")
        bot_response = response.json().get("text", "No response available from the bot.")
        return bot_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling ConvAI API: {e}")
        return "Error: Unable to fetch response from the bot."

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "").strip()

        if not user_message:
            logging.error("Empty message received")
            return jsonify({"error": "Message is required"}), 400

        logging.debug(f"User message received: {user_message}")
        bot_response = send_request_to_convai(user_message)
        logging.debug(f"Bot response: {bot_response}")

        return jsonify({"response": bot_response})
    except Exception as e:
        logging.error(f"Error processing chat request: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
