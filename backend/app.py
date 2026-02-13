# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from bson import ObjectId
from config import db
from models.study_plan_model import study_plan_collection
from models.task_model import task_collection
from services.scheduler_service import build_basic_plan
from services.llm_service import generate_schedule
from services.rescheduler_service import reschedule_missed_tasks

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "EduPlan-AI Backend Running"})

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.json
    plan = generate_schedule(data)
    return jsonify({
        "status": "success",
        "study_plan": plan
    })
#creating plan & generating task
@app.route("/api/plan/create", methods=["POST"])
def create_plan():

    data = request.json

    subjects = data.get("subjects")
    days = int(data.get("exam_days"))
    hours = float(data.get("hours_per_day"))

    # Save study plan
    plan_doc = {
        "raw_input": data,
        "constraints": {
            "subjects": subjects,
            "exam_days": days,
            "hours_per_day": hours
        },
        "status": "active",
        "created_at": datetime.utcnow()
    }

    plan_id = study_plan_collection.insert_one(plan_doc).inserted_id

    # Generate tasks
    tasks = build_basic_plan(subjects, days, hours)

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
    tasks = list(db.daily_tasks.find(
        {"plan_id": ObjectId(plan_id)},
        {"_id": 1, "day": 1, "subject": 1, "status": 1}
    ))

    for task in tasks:
        task["_id"] = str(task["_id"])

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
                "completed_at": datetime.utcnow()
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

    total = task_collection.count_documents({
        "plan_id": ObjectId(plan_id)
    })

    completed = task_collection.count_documents({
        "plan_id": ObjectId(plan_id),
        "status": "completed"
    })

    missed = task_collection.count_documents({
        "plan_id": ObjectId(plan_id),
        "status": "missed"
    })

    pending = total - completed - missed

    return jsonify({
        "total_tasks": total,
        "completed": completed,
        "missed": missed,
        "pending": pending,
        "completion_percent": round((completed/total)*100, 2) if total else 0
    })
    
# Reschedule missed tasks API
@app.route("/api/plan/<plan_id>/reschedule", methods=["POST"])
def reschedule_plan(plan_id):

    result = reschedule_missed_tasks(plan_id)

    return jsonify({
        "status": "success",
        "details": result
    })





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

