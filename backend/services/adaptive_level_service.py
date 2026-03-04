from datetime import datetime
from bson import ObjectId
from config import db

task_collection = db.daily_tasks
plan_collection = db.study_plans

MIN_TASKS_REQUIRED = 5


def evaluate_adaptive_level(plan_id):

    plan_id = ObjectId(plan_id)

    plan = plan_collection.find_one({"_id": plan_id})
    if not plan:
        return

    total = task_collection.count_documents({"plan_id": plan_id})
    if total < MIN_TASKS_REQUIRED:
        return  # not enough data

    completed = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "completed"
    })

    missed = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "missed"
    })

    completion_rate = (completed / total) * 100

    current_level = plan.get("adaptive_level", "medium")

    new_level = current_level

    # 🔻 Struggling Logic
    if completion_rate < 40 and missed >= 3:
        new_level = "low"

    # 🔺 High Performer Logic
    elif completion_rate > 80 and completed >= 5:
        new_level = "high"

    else:
        new_level = "medium"

    # Only update if changed
    if new_level != current_level:
        plan_collection.update_one(
            {"_id": plan_id},
            {
                "$set": {
                    "adaptive_level": new_level,
                    "adaptive_last_updated": datetime.now()
                }
            }
        )

        print(f"Adaptive Level Updated → {new_level}")