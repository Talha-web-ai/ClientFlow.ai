import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

chat_history = []

def build_prompt(user_input):
    global chat_history

    system_prompt = """
You are a professional and helpful customer support assistant for a gym.

Answer clearly, politely, and concisely.

Gym Details:
- Monthly Plan: ₹1500
- Personal Training: Available
- Timings: 6 AM - 10 PM
- Location: Mumbai
"""

    chat_history.append(f"User: {user_input}")

    history_text = "\n".join(chat_history[-6:])  # last 6 messages

    full_prompt = f"{system_prompt}\n{history_text}\nAssistant:"

    return full_prompt

def chat_with_bot(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]
    except Exception as e:
        return f"Error: {e}"

def main():
    print("🤖 AI Gym Chatbot with Memory (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye 👋")
            break

        prompt = build_prompt(user_input)
        reply = chat_with_bot(prompt)

        chat_history.append(f"Assistant: {reply.strip()}")

        print("Bot:", reply.strip(), "\n")

if __name__ == "__main__":
    main()