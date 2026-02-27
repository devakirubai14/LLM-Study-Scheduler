import requests
import json
from config import GROQ_API_KEY

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def analyze_topics(data):
    syllabus = data.get("syllabus_text", "")
    past_questions = data.get("past_questions_text", "")
    subjects = ", ".join(data.get("subjects", []))
    target_score = data.get("target_score", 0)

    prompt = f"""
You are an academic planner.

Subjects: {subjects}
Target Score: {target_score}+

Based on the following syllabus and past questions,
identify important topics for scoring high marks.

Return ONLY valid JSON array like:
[
  {{"topic":"Topic Name","priority":"High"}},
  {{"topic":"Topic Name","priority":"Medium"}},
  {{"topic":"Topic Name","priority":"Low"}}
]

Syllabus:
{syllabus}

Past Questions:
{past_questions}
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
        "temperature": 0.3
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    generated_text = result["choices"][0]["message"]["content"]

    try:
        start = generated_text.find("[")
        end = generated_text.rfind("]") + 1
        json_text = generated_text[start:end]
        parsed = json.loads(json_text)
        return parsed
    except:
        return {"raw_output": generated_text}