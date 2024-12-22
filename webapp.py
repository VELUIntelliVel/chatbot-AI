from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Your Flask routes and functions
@app.route("/", methods=["GET"])
def home():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    # Chat logic here
    pass

@app.route("/chat", methods=["GET"])
def chat_get():
    return "This endpoint only supports POST requests.", 405

# Entry point for running the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
