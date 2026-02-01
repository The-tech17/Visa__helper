import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Google Custom Search setup
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def google_search(query):
    """Fetch results from Google Custom Search Engine"""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    results = response.json().get("items", [])
    snippets = [item["snippet"] for item in results]
    return "\n".join(snippets)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Step 1: Retrieve context from Google CSE
        context = google_search(user_input)

        # Step 2: Augment query with retrieved context
        prompt = f"""
        You are a helpful visa assistant chatbot.
        User question: {user_input}
        Relevant context: {context}
        Provide a clear, accurate, and concise answer.
        """

        # Step 3: Generate response with Gemini
        response = model.generate_content(prompt)
        answer = response.text

        return jsonify({"reply": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Visa Helper Chatbot is running!"

if __name__ == "__main__":
    app.run(debug=True)
