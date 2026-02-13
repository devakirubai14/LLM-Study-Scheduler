from datetime import datetime
from bson import ObjectId
from config import db

task_collection = db.daily_tasks


def reschedule_missed_tasks(plan_id):
    """
    Finds missed tasks for a plan and reschedules them
    to the next available days.
    """

    # Fetch missed tasks
    missed_tasks = list(task_collection.find({
        "plan_id": ObjectId(plan_id),
        "status": "missed"
    }))

    if not missed_tasks:
        return {
            "message": "No missed tasks to reschedule",
            "rescheduled": 0
        }

    # Find last scheduled day
    last_task = task_collection.find_one(
        {"plan_id": ObjectId(plan_id)},
        sort=[("day", -1)]
    )

    start_day = last_task["day"] + 1
    new_tasks = []
    current_day = start_day

    for task in missed_tasks:
        new_tasks.append({
            "plan_id": ObjectId(plan_id),
            "day": current_day,
            "subject": task["subject"],
            "status": "pending",
            "type": "rescheduled",
            "rescheduled_from": task["_id"],
            "created_at": datetime.utcnow()
        })

        # Mark old task as rescheduled
        task_collection.update_one(
            {"_id": task["_id"]},
            {"$set": {"status": "rescheduled"}}
        )

        current_day += 1

    # Insert new rescheduled tasks
    task_collection.insert_many(new_tasks)

    return {
        "rescheduled": len(new_tasks),
        "new_days_added": len(new_tasks)
    }
