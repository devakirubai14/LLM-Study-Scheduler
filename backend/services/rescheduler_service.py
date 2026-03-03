from datetime import datetime, timedelta
from bson import ObjectId
from config import db
from services.scheduler_service import build_priority_based_plan
from models.notification_model import notification_collection

task_collection = db.daily_tasks
plan_collection = db.study_plans


def reschedule_missed_tasks(plan_id, new_days, new_sessions):
    
    # ✅ VALIDATE INPUT FIRST
    if not new_days or new_days <= 0:
        return {"error": "Invalid exam days"}

    if not new_sessions or not isinstance(new_sessions, list):
        return {"error": "Invalid sessions input"}
    
    plan_id = ObjectId(plan_id)

    # Get original plan
    plan = plan_collection.find_one({"_id": plan_id})
    if not plan:
        return {"error": "Plan not found"}

    subjects = plan["constraints"]["subjects"]

    # Get all missed + pending tasks
    remaining_tasks = list(task_collection.find({
        "plan_id": plan_id,
        "status": {"$in": ["missed", "pending"]}
    }))

    if not remaining_tasks:
        return {"message": "No tasks to reschedule", "rescheduled": 0}

    # Delete future pending/missed tasks
    task_collection.delete_many({
        "plan_id": plan_id,
        "status": {"$in": ["missed", "pending"]}
    })

    # Build new schedule from today
    start_date = datetime.utcnow().date()
    
    dummy_topics = [
        {"topic": "Algebra", "priority": "High"},
        {"topic": "Calculus", "priority": "Medium"},
        {"topic": "Trigonometry", "priority": "Low"}
    ]

    new_tasks = build_priority_based_plan(
    topics_with_priority=dummy_topics,
    days=new_days,
    sessions_per_day=new_sessions,
    start_date=start_date
    )

    for task in new_tasks:
        task["plan_id"] = plan_id
        task["type"] = "rescheduled"

    task_collection.insert_many(new_tasks)

    return {
        "rescheduled": len(new_tasks),
        "new_days": new_days
    }
    
def adaptive_reschedule(plan_id):
    """
    Triggered when student misses 3+ sessions.
    Makes schedule easier automatically.
    """

    print("Adaptive system triggered — Student struggling.")

    plan_id = ObjectId(plan_id)

    # Reduce duration by 20%
    pending_tasks = list(task_collection.find({
        "plan_id": plan_id,
        "status": "pending"
    }))

    for task in pending_tasks:
        new_duration = int(task["duration_minutes"] * 0.8)

        new_end = task["scheduled_start"] + timedelta(minutes=new_duration)

        task_collection.update_one(
            {"_id": task["_id"]},
            {
                "$set": {
                    "duration_minutes": new_duration,
                    "scheduled_end": new_end
                }
            }
        )

    # Send stronger support message
    from services.motivation_service import generate_support_message

    message = generate_support_message()

    notification_collection.insert_one({
        "plan_id": plan_id,
        "message": "We noticed you're having difficulty. We've adjusted your schedule to make it easier 💛\n\n" + message,
        "type": "adaptive_support",
        "created_at": datetime.now(),
        "read": False
    })