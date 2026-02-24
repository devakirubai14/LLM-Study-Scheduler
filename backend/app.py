from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from bson import ObjectId
from config import db
from models.study_plan_model import study_plan_collection
from models.task_model import task_collection
from services.scheduler_service import build_time_based_plan
from services.llm_service import generate_schedule
from services.rescheduler_service import reschedule_missed_tasks
from apscheduler.schedulers.background import BackgroundScheduler
from services.reminder_service import check_and_send_reminders


app = Flask(__name__)
CORS(app)

scheduler = BackgroundScheduler()
scheduler.add_job(check_and_send_reminders, "interval", minutes=1)
scheduler.start()

@app.route('/')
def home():
    return jsonify({"message": "EduPlan-AI Backend Running"})


# @app.route('/generate-plan', methods=['POST'])
# def generate_plan():
#     data = request.json
#     plan = generate_schedule(data)
#     return jsonify({
#         "status": "success",
#         "study_plan": plan
#     })

# #creating plan & generating task
@app.route("/api/plan/create", methods=["POST"])
def create_plan():
    
    data = request.json

    subjects = data.get("subjects", [])
    if not subjects or not isinstance(subjects, list):
        return jsonify({
            "status": "error",
            "message": "Subjects must be a non-empty list"
        }), 400

    try:
        days = int(data.get("exam_days"))
        hours = float(data.get("hours_per_day"))
    except:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    if days <= 0:
        return jsonify({"status": "error", "message": "Invalid days"}), 400

    sessions = data.get("sessions", [])
    if not sessions:
        return jsonify({"status": "error", "message": "Sessions required"}), 400

    phone = data.get("phone_number")
    if not phone:
        return jsonify({"error": "Phone number required"}), 400

    plan_doc = {
        "raw_input": data,
        "constraints": {
            "subjects": subjects,
            "exam_days": days,
            "hours_per_day": hours
        },
        "phone_number": phone,
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    }

    plan_id = study_plan_collection.insert_one(plan_doc).inserted_id

    start_date = datetime.now().date()

    tasks = build_time_based_plan(
        subjects=subjects,
        days=days,
        sessions_per_day=sessions,
        start_date=start_date
    )

    for t in tasks:
        t["plan_id"] = plan_id

    task_collection.insert_many(tasks)

    return jsonify({
        "status": "success",
        "plan_id": str(plan_id),
        "tasks_created": len(tasks)
    })
    
# to get tasks
@app.route("/api/plan/<plan_id>/tasks", methods=["GET"])
def get_plan_tasks(plan_id):
    tasks = list(task_collection.find(
        {"plan_id": ObjectId(plan_id)},
        {
            "_id": 1,
            "subject": 1,
            "status": 1,
            "scheduled_start": 1,
            "scheduled_end": 1,
            "duration_minutes": 1
        }
    ))

    for task in tasks:
        task["_id"] = str(task["_id"])
        task["scheduled_start"] = task["scheduled_start"].isoformat()
        task["scheduled_end"] = task["scheduled_end"].isoformat()

    return jsonify(tasks)



# task complete api
@app.route("/api/task/complete", methods=["POST"])
def mark_task_complete():


    data = request.json
    task_id = data.get("task_id")


    result = task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc)
            }
        }
    )


    return jsonify({
        "status": "updated",
        "matched": result.matched_count
    })
# Task missed api
@app.route("/api/task/miss", methods=["POST"])
def mark_task_missed():


    data = request.json
    task_id = data.get("task_id")


    result = task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {
            "$set": {
                "status": "missed"
            }
        }
    )


    return jsonify({
        "status": "updated",
        "matched": result.matched_count
    })


#Plan Progress API
@app.route("/api/plan/<plan_id>/progress")
def plan_progress(plan_id):
    plan_id = ObjectId(plan_id)

    total = task_collection.count_documents({
        "plan_id": plan_id
    })

    completed = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "completed"
    })

    missed = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "missed"
    })

    pending = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "pending"
    })

    percent = round((completed / total) * 100, 2) if total else 0

    return jsonify({
        "total_tasks": total,
        "completed": completed,
        "missed": missed,
        "pending": pending,
        "completion_percent": percent
    })
    
# Reschedule missed tasks API
@app.route("/api/plan/<plan_id>/reschedule", methods=["POST"])
def reschedule_plan(plan_id):
    data = request.json

    try:
        new_days = int(data.get("exam_days"))
    except:
        return jsonify({"error": "Invalid exam days"}), 400

    new_sessions = data.get("sessions")

    result = reschedule_missed_tasks(plan_id, new_days, new_sessions)

    return jsonify(result)


# @app.route("/test-db")
# def test_db():
#     db.test.insert_one({"status": "MongoDB connected"})
#     return {"message": "MongoDB test document inserted"}


# @app.route("/debug-db")
# def debug_db():
#     return {
#         "database": db.name,
#         "collections": db.list_collection_names()
#     }



if __name__ == '__main__':
    app.run(debug=True)
    