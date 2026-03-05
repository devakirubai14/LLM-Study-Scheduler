from datetime import datetime
from models.chat_history_model import chat_history_collection


def save_message(user_id, role, message):

    chat_history_collection.insert_one({
        "user_id": user_id,
        "role": role,
        "message": message,
        "created_at": datetime.now()
    })


def get_recent_messages(user_id, limit=5):

    messages = list(
        chat_history_collection
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(limit)
    )

    messages.reverse()

    chat_format = []

    for m in messages:
        chat_format.append({
            "role": m["role"],
            "content": m["message"]
        })

    return chat_format