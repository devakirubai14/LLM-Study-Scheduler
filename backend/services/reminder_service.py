from datetime import datetime, timedelta
from config import db
from services.fcm_service import send_push_notification
from models.user_model import users_collection

task_collection = db.daily_tasks
plan_collection = db.study_plans


def check_and_send_reminders():

    now = datetime.now()
    alert_time = now + timedelta(minutes=5)

    tasks = list(task_collection.find({
        "scheduled_start": {
            "$gte": now,
            "$lte": alert_time
        },
        "status": "pending",
        "reminder_sent": False,
        "type": {"$ne": "break"}
    }))

    for task in tasks:

        plan = plan_collection.find_one({"_id": task["plan_id"]})
        user = users_collection.find_one({"_id": plan["user_id"]})
        
        if not user:
            continue

        device_token = user.get("device_token")

        readable_time = task["scheduled_start"].strftime("%I:%M %p")
        topic_name = task.get("topic", "Study Session")

        title = "Study Reminder"
        body = f"Study {topic_name} at {readable_time}"

        # 🔥 Send push notification
        if device_token:
            send_push_notification(device_token, title, body)

        print(f"Reminder: {body}")

        # mark reminder sent
        task_collection.update_one(
            {"_id": task["_id"]},
            {"$set": {"reminder_sent": True}}
        )