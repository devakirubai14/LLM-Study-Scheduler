from datetime import datetime, timedelta
from config import db

task_collection = db.daily_tasks
plan_collection = db.study_plans


def check_and_send_reminders():
    now = datetime.now()
    alert_time = now + timedelta(minutes=5)

    tasks = list(task_collection.find({
        "scheduled_start": {"$lte": alert_time},
        "status": "pending",
        "reminder_sent": False
    }))

    for task in tasks:
        plan = plan_collection.find_one({"_id": task["plan_id"]})
        phone = plan.get("phone_number")

        # Convert to 12-hour format for display
        readable_time = task["scheduled_start"].strftime("%I:%M %p")

        print(f"Reminder: Study {task['subject']} at {readable_time}. Phone: {phone}")

        task_collection.update_one(
            {"_id": task["_id"]},
            {"$set": {"reminder_sent": True}}
        )