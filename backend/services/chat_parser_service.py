import requests
import json
from config import GROQ_API_KEY

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def detect_intent(message):

    prompt = f"""
Classify the student message.

Return JSON only.

Possible intents:

plan → student wants a new study plan
reschedule → student wants to reschedule missed sessions
progress → student asking about study progress
chat → normal conversation

Example:
{{"intent":"plan"}}

Message:
{message}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    result = response.json()

    text = result["choices"][0]["message"]["content"]

    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except:
        return {"intent": "chat"}


def parse_study_request(message):

    prompt = f"""
Extract study planning information from the message.

Return ONLY JSON like this:

{{
 "subjects": ["Math"],
 "exam_days": 1,
 "start_time": "07:00",
 "end_time": "13:00",
 "target_score": 90
}}

Message:
{message}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    result = response.json()

    text = result["choices"][0]["message"]["content"]

    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except:
        return {"error": text}


def generate_chat_reply(message, history=None):

    messages = [
        {
            "role": "system",
            "content": "You are a friendly AI study assistant. Reply in 1-2 short sentences."
        }
    ]

    # Add previous conversation
    if history:
        messages.extend(history)

    # Add latest user message
    messages.append({
        "role": "user",
        "content": message
    })

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    result = response.json()

    return result["choices"][0]["message"]["content"]