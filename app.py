from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

chat_history = []

def build_prompt(user_input):
    global chat_history

    system_prompt = """
You are ClientFlow AI, a smart assistant helping salons manage bookings and customer queries.

Your job:
- Answer customer queries
- Suggest services
- Help with booking appointments

Salon Details:
- Haircut: ₹500
- Facial: ₹1200
- Hair Spa: ₹1500
- Bridal Package: Available
- Timings: 10 AM - 8 PM
- Location: Mumbai

Rules:
- Be short, clear, and polite
- Guide users toward booking
- If user wants to book, ask for name + time
"""

    chat_history.append(f"User: {user_input}")
    history_text = "\n".join(chat_history[-6:])

    return f"{system_prompt}\n{history_text}\nAssistant:"

def chat_with_bot(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]

    prompt = build_prompt(user_input)
    reply = chat_with_bot(prompt)

    chat_history.append(f"Assistant: {reply.strip()}")

    return jsonify({"reply": reply.strip()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))