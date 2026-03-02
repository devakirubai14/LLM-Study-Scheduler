from datetime import datetime, timedelta
from config import db
from services.motivation_service import generate_missed_message
from models.notification_model import notification_collection

task_collection = db.daily_tasks
plan_collection = db.study_plans

GRACE_PERIOD_HOURS = 0.05

def check_and_mark_missed_tasks():
    now = datetime.now()
    grace_cutoff = now - timedelta(hours=GRACE_PERIOD_HOURS)

    overdue_tasks = list(task_collection.find({
        "scheduled_end": {"$lt": grace_cutoff},
        "status": "pending"
    }))

    for task in overdue_tasks:

        task_collection.update_one(
            {"_id": task["_id"]},
            {"$set": {"status": "missed"}}
        )

        topic_name = task.get("topic", "Study Session")

        # 🔥 Generate motivation
        message = generate_missed_message(topic_name)

        # 🔹 Save to notifications
        notification_collection.insert_one({
            "plan_id": task["plan_id"],
            "message": message,
            "type": "motivation",
            "created_at": datetime.now(),
            "read": False
        })

        # 🔹 Simulate SMS
        plan = plan_collection.find_one({"_id": task["plan_id"]})
        phone = plan.get("phone_number", "Unknown")

        print(f"Task auto-marked missed: {topic_name}")
        print(f"SMS to {phone}: {message}")