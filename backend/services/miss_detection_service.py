from datetime import datetime, timedelta
from config import db

task_collection = db.daily_tasks

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
        print(f"Task auto-marked missed: {topic_name}")