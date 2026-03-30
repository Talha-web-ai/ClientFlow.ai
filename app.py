from flask import Flask, request, jsonify, render_template
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# -------------------------
# GROQ SETUP
# -------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_history = []

# -------------------------
# BOOKING STATE (NEW)
# -------------------------
current_booking = {
    "day": None,
    "time": None
}

# -------------------------
# SIMPLE BOOKING DATABASE
# -------------------------
booked_slots = {
    "friday": ["2 pm"],
    "saturday": []
}

# -------------------------
# EXTRACT DAY & TIME
# -------------------------
def extract_booking_details(text):
    text = text.lower()

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    day_found = None
    time_found = None

    for day in days:
        if day in text:
            day_found = day

    # detect times like "2 am", "5 pm"
    words = text.split()
    for i in range(len(words) - 1):
        if words[i].isdigit() and words[i+1] in ["am", "pm"]:
            time_found = f"{words[i]} {words[i+1]}"

    return day_found, time_found


# -------------------------
# BUILD PROMPT
# -------------------------
def build_prompt(user_input):
    global chat_history

    system_prompt = """
You are ClientFlow AI, the assistant for GlowUp Salon in Mumbai.

Your job:
- Answer customer queries
- Help users book appointments
- Guide conversations toward booking

Salon Details:
- Haircut: ₹500
- Facial: ₹1200
- Hair Spa: ₹1500
- Bridal Package: Available
- Timings: 10 AM - 8 PM
- Location: Mumbai

Rules:
- Keep responses under 1-2 short sentences
- Be friendly and natural
- Ask one question at a time
- Guide users toward booking
- When booking is confirmed → clearly confirm it
"""

    chat_history.append(f"User: {user_input}")
    history_text = "\n".join(chat_history[-6:])

    return f"{system_prompt}\n{history_text}\nAssistant:"


# -------------------------
# AI RESPONSE
# -------------------------
def chat_with_bot(prompt):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",  # WORKING MODEL
            temperature=0.7,
            max_tokens=80
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"].lower()

    day, time = extract_booking_details(user_input)

    valid_times = ["10 am", "11 am", "12 pm", "1 pm", "2 pm", "3 pm", "4 pm", "5 pm", "6 pm", "7 pm"]

    # STORE PARTIAL INFO
    if day:
        current_booking["day"] = day

    if time:
        current_booking["time"] = time

    # ASK FOR MISSING TIME
    if current_booking["day"] and not current_booking["time"]:
        return jsonify({
            "reply": f"Great, what time on {current_booking['day'].title()}?"
        })

    # ASK FOR MISSING DAY
    if current_booking["time"] and not current_booking["day"]:
        return jsonify({
            "reply": "Got it. Which day would you like to book?"
        })

    # INVALID TIME
    if current_booking["time"] and current_booking["time"] not in valid_times:
        current_booking["time"] = None
        return jsonify({
            "reply": "We are open from 10 AM to 8 PM. Please choose a valid time."
        })

    # COMPLETE BOOKING
    if current_booking["day"] and current_booking["time"]:
        day = current_booking["day"]
        time = current_booking["time"]

        if day not in booked_slots:
            booked_slots[day] = []

        if time in booked_slots[day]:
            return jsonify({
                "reply": f"Sorry, {time} on {day.title()} is already booked. Try another time."
            })

        booked_slots[day].append(time)

        # RESET STATE
        current_booking["day"] = None
        current_booking["time"] = None

        return jsonify({
            "reply": f"✅ Your appointment is confirmed for {day.title()} at {time}."
        })

    # FALLBACK AI
    prompt = build_prompt(user_input)
    reply = chat_with_bot(prompt)

    chat_history.append(f"Assistant: {reply}")

    return jsonify({"reply": reply})


# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))