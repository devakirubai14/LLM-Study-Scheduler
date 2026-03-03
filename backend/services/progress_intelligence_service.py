from datetime import datetime
from bson import ObjectId

from config import db
from models.notification_model import notification_collection

task_collection = db.daily_tasks
plan_collection = db.study_plans

LOW_THRESHOLD = 40
HIGH_THRESHOLD = 80
MIN_TASKS_REQUIRED = 5
MIN_MISSED_FOR_LOW = 3


def evaluate_progress_and_notify(plan_id):
    """
    Intelligent progress evaluator.

    Triggers:
    - Low performance → only if:
        total tasks >= 5
        completion rate < 40%
        missed sessions >= 3
    - High performance → completion rate > 80%
    """

    plan_id = ObjectId(plan_id)

    total = task_collection.count_documents({"plan_id": plan_id})
    if total == 0:
        return

    completed = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "completed"
    })

    missed = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "missed"
    })

    completion_rate = (completed / total) * 100

    plan = plan_collection.find_one({"_id": plan_id})
    if not plan:
        return

    low_alert_sent = plan.get("low_performance_alert_sent", False)
    high_alert_sent = plan.get("high_performance_alert_sent", False)

    # =========================
    # 📉 LOW PERFORMANCE LOGIC
    # =========================
    if (
        total >= MIN_TASKS_REQUIRED and
        completion_rate < LOW_THRESHOLD and
        missed >= MIN_MISSED_FOR_LOW and
        not low_alert_sent
    ):

        message = (
            "It's okay to move slowly. Progress matters more than speed 💛 "
            "Let’s reset and focus on one session at a time."
        )

        notification_collection.insert_one({
            "plan_id": plan_id,
            "message": message,
            "type": "progress_support",
            "created_at": datetime.now(),
            "read": False
        })

        plan_collection.update_one(
            {"_id": plan_id},
            {"$set": {
                "low_performance_alert_sent": True,
                "high_performance_alert_sent": False
            }}
        )

        print("Progress Intelligence: Low performance support triggered.")
        return

    # =========================
    # 📈 HIGH PERFORMANCE LOGIC
    # =========================
    if (
        completion_rate >= HIGH_THRESHOLD and
        total >= MIN_TASKS_REQUIRED and
        not high_alert_sent
    ):

        message = (
            "Outstanding consistency! You're operating at high performance 🚀 "
            "Keep this rhythm — 90+ is absolutely within reach!"
        )

        notification_collection.insert_one({
            "plan_id": plan_id,
            "message": message,
            "type": "high_performance",
            "created_at": datetime.now(),
            "read": False
        })

        plan_collection.update_one(
            {"_id": plan_id},
            {"$set": {
                "high_performance_alert_sent": True,
                "low_performance_alert_sent": False
            }}
        )

        print("Progress Intelligence: High performance reinforcement triggered.")