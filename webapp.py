import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import logging

app = Flask(__name__, static_folder='static')
# Allow requests from all origins
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["POST", "GET"])

# Configure API credentials
API_KEY = "0c4d8e49f1244043408a7cced81993aa"
CHARACTER_ID = "32a6a8bc-b656-11ef-b082-42010a7be016"
SESSION_ID = -1

logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET"])
def home():
    logging.debug("Serving chatbot.html")
    return render_template("chatbot.html", backend_url="https://chatbot-ai-1-zb7c.onrender.com/chat")

@app.errorhandler(500)
def internal_error(error):
    return jsonify(response="Internal Server Error"), 500

def send_request_to_convai(user_message):
    url = "https://api.convai.com/character/getResponse"
    headers = {"CONVAI-API-KEY": API_KEY}

    # Prepare payload as form-data
    payload = {
        "userText": user_message,
        "charID": CHARACTER_ID,
        "sessionID": SESSION_ID,
        "voiceResponse": "false"  # Set to 'true' if you want audio responses
    }

    logging.debug(f"Payload: {payload}")
    logging.debug(f"Headers: {headers}")

    try:
        # Send request with form-data format
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        logging.debug(f"Raw ConvAI API response: {response.text}")

        # Parse the bot's response
        bot_response = response.json().get("text", "No response available from the bot.")
        return bot_response
    except requests.exceptions.Timeout:
        logging.error("ConvAI API timed out.")
        return "Error: ConvAI API timed out. Please try again later."
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error from ConvAI API: {e.response.status_code} - {e.response.text}")
        return f"Error: ConvAI API returned status code {e.response.status_code}."
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception: {e}")
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
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000
    app.run(host="0.0.0.0", port=port, debug=True)
