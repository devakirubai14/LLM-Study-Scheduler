import json
import requests
from config import GROQ_API_KEY

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

PRIORITY_BASE_WEIGHT = {
    "High": 3,
    "Medium": 2,
    "Low": 1
}


def extract_marks_from_blueprint(blueprint_text):
    """
    Ask LLM to extract marks per topic from blueprint text.
    Returns:
    [
        {"topic": "Algebra", "marks": 20},
        {"topic": "Calculus", "marks": 15}
    ]
    """

    if not blueprint_text:
        return None

    prompt = f"""
            Extract topic-wise marks distribution from the following exam blueprint.

            Return ONLY valid JSON array in format:
            [
            {{"topic": "Topic Name", "marks": number}}
            ]

Blueprint:
{blueprint_text}
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

    if response.status_code != 200:
        return None

    result = response.json()
    text = result["choices"][0]["message"]["content"]

    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])
    except:
        return None
    
def extract_frequency_from_past_questions(past_questions_text):
    """
    Ask LLM to count topic frequency from past questions text.

    Returns:
    [
        {"topic": "Algebra", "frequency": 5},
        {"topic": "Calculus", "frequency": 3}
    ]
    """

    if not past_questions_text:
        return None

    prompt = f"""
From the following past exam questions, count how many times each topic appears.

Return ONLY valid JSON array in format:
[
  {{"topic": "Topic Name", "frequency": number}}
]

Past Questions:
{past_questions_text}
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

    if response.status_code != 200:
        return None

    result = response.json()
    text = result["choices"][0]["message"]["content"]

    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])
    except:
        return None


def calculate_final_weights(topics_with_priority, past_question_frequency=None, marks_data=None):
    """
    Priority order:
    1. If marks_data exists → use marks
    2. Else if frequency exists → frequency * base_weight
    3. Else → base_weight only
    """

    final_weights = []

    for topic in topics_with_priority:
        name = topic["topic"]
        priority = topic["priority"]
        base_weight = PRIORITY_BASE_WEIGHT.get(priority, 1)

        # 🔥 Layer 3: Marks override everything
        if marks_data:
            mark_entry = next(
                (
                    m for m in marks_data
                    if m["topic"].lower() in name.lower()
                ),
                None
            )
            if mark_entry:
                final_weights.append({
                    "topic": name,
                    "weight": mark_entry["marks"]
                })
                continue

        # 🔥 Layer 2: Frequency-based
        if past_question_frequency:
            freq_entry = next((f for f in past_question_frequency if f["topic"].lower() == name.lower()), None)
            if freq_entry:
                final_weights.append({
                    "topic": name,
                    "weight": freq_entry["frequency"] * base_weight
                })
                continue

        # 🔥 Layer 1: Base only
        final_weights.append({
            "topic": name,
            "weight": base_weight
        })

    return final_weights