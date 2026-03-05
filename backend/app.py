from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from bson import ObjectId
import os

from config import db
from models.study_plan_model import study_plan_collection
from models.task_model import task_collection

from services.scheduler_service import build_priority_based_plan
from services.llm_service import analyze_topics
from services.rescheduler_service import reschedule_missed_tasks
from services.reminder_service import check_and_send_reminders
from services.miss_detection_service import check_and_mark_missed_tasks
from services.motivation_service import generate_completed_message
from services.motivation_service import generate_support_message
from models.notification_model import notification_collection
from services.progress_intelligence_service import evaluate_progress_and_notify
from services.auth_service import register_user, login_user
from services.auth_guard import get_user_from_token
from services.chat_parser_service import detect_intent, parse_study_request, generate_chat_reply
from services.chat_history_service import save_message, get_recent_messages

from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
CORS(app)


# Scheduler setup
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":

    scheduler = BackgroundScheduler()

    # reminder checker
    scheduler.add_job(
        check_and_send_reminders,
        "interval",
        minutes=1
    )

    # missed session detector
    scheduler.add_job(
        check_and_mark_missed_tasks,
        "interval",
        minutes=1
    )

    scheduler.start()

    print("Background scheduler started...")


@app.route('/')
def home():
    return jsonify({"message": "EduPlan-AI Backend Running"})

# ============================================
# REGISTER 
# ============================================
@app.route("/api/auth/register", methods=["POST"])
def register():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    
    # ✅ validation
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password required"}), 400

    user_id, error = register_user(name, email, password)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "User registered",
        "user_id": user_id
    })

# ============================================
#                   LOGIN
# ============================================

@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")
    
    # ✅ validation
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    token, error = login_user(email, password)

    if error:
        return jsonify({"error": error}), 401

    return jsonify({
        "message": "Login successful",
        "token": token
    })
    
# ============================================
#   CHAT PARSER
# ============================================
@app.route("/api/chat", methods=["POST"])
def chat():

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"error": "Message required"}), 400

    user_id = user["_id"]

    # Save user message
    save_message(user_id, "user", message)

    # Get recent chat history
    history = get_recent_messages(user_id)

    intent = detect_intent(message)

    if intent.get("intent") == "plan":

        parsed = parse_study_request(message)

        reply = "Got it! I’ll create a study plan for you."

        save_message(user_id, "assistant", reply)

        return jsonify({
            "type": "plan",
            "data": parsed,
            "message": reply
        })

    else:

        reply = generate_chat_reply(message, history)

        save_message(user_id, "assistant", reply)

        return jsonify({
            "type": "chat",
            "message": reply
        })


# ============================================
# CREATE PLAN (LLM + Priority Scheduler)
# ============================================


@app.route("/api/plan/create", methods=["POST"])
def create_plan():

    data = request.json

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user["_id"]

    subjects = data.get("subjects", [])
    if not subjects or not isinstance(subjects, list):
        return jsonify({
            "status": "error",
            "message": "Subjects must be a non-empty list"
        }), 400

    try:
        days = int(data.get("exam_days"))
        
    except:
        return jsonify({"status": "error", "message": "Invalid exam days"}), 400

    if days <= 0:
        return jsonify({"status": "error", "message": "Invalid exam days"}), 400

    sessions = data.get("sessions", [])
    if not sessions:
        return jsonify({"status": "error", "message": "Sessions required"}), 400

    sessions = data.get("sessions", [])

    phone = data.get("phone_number")
    if not phone:
        return jsonify({"status": "error", "message": "Phone number required"}), 400

    # 🔹 Call LLM for topic analysis
    topics_from_llm = analyze_topics({
        "subjects": subjects,
        "target_score": data.get("target_score", 90),
        "syllabus_text": data.get("syllabus_text", ""),
        "past_questions_text": data.get("past_questions_text", "")
    })
    unique_topics = {}
    for t in topics_from_llm:
        topic = t["topic"].strip().lower()

        if topic not in unique_topics:
            unique_topics[topic] = t

    topics_from_llm = list(unique_topics.values())
    
    # Validate LLM response
    if not isinstance(topics_from_llm, list):
        return jsonify({
            "error": "LLM topic analysis failed",
            "details": topics_from_llm
        }), 500
    
    from services.weight_engine_service import (
    extract_marks_from_blueprint,
    extract_frequency_from_past_questions,
    calculate_final_weights
    )

    # 🔹 Extract marks if blueprint exists
    marks_data = extract_marks_from_blueprint(
        data.get("marks_blueprint_text", "")
    )

    # 🔹 Extract frequency if past questions exist
    frequency_data = extract_frequency_from_past_questions(
        data.get("past_questions_text", "")
    )

    # 🔹 Calculate final weights
    weighted_topics = calculate_final_weights(
        topics_with_priority=topics_from_llm,
        past_question_frequency=frequency_data,
        marks_data=marks_data
    )
    # 🔒 Safety validation
    clean_topics = []

    for t in weighted_topics:
        topic_name = t.get("topic")
        weight = t.get("weight", 1)

        if not topic_name:
            continue

        clean_topics.append({
            "topic": topic_name,
            "weight": weight
        })

    # Save plan
    self_rating = data.get("self_rating", "medium")

    plan_doc = {
        "user_id" : user_id,
        "raw_input": data,
        "constraints": {
            "subjects": subjects,
            "exam_days": days
        },
        "phone_number": phone,
        "status": "active",
        "self_rating": self_rating,
        "adaptive_level": self_rating,  # starts same as self rating
        "adaptive_last_updated": datetime.now(),
        "created_at": datetime.now()
    }

    plan_id = study_plan_collection.insert_one(plan_doc).inserted_id

    start_date = datetime.now().date()

    # 🔹 Generate priority-based schedule
    tasks = build_priority_based_plan(
        topics_with_priority=weighted_topics,
        days=days,
        sessions_per_day=sessions,
        start_date=start_date,
        adaptive_level=plan_doc["adaptive_level"]
    )
    from services.cognitive_ordering_service import reorder_sessions_by_cognitive_curve

    tasks = reorder_sessions_by_cognitive_curve(
        tasks,
        plan_doc["adaptive_level"]
    )

    for t in tasks:
        t["plan_id"] = plan_id

    task_collection.insert_many(tasks)

    return jsonify({
        "status": "success",
        "plan_id": str(plan_id),
        "tasks_created": len(tasks)
    })
    
# ============================================
# Device Token
# ============================================

@app.route("/api/device/register", methods=["POST"])
def register_device():

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    device_token = data.get("device_token")

    if not device_token:
        return jsonify({"error": "device_token required"}), 400

    from models.user_model import users_collection

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"device_token": device_token}}
    )

    return jsonify({
        "message": "Device token saved"
    })

# ============================================
# LLM Topic Analyzer Test Endpoint
# ============================================

@app.route("/api/analyze-topics", methods=["POST"])
def analyze_topics_route():
    data = request.json
    result = analyze_topics(data)
    return jsonify(result)


# ============================================
# GET TASKS
# ============================================

@app.route("/api/plan/<plan_id>/tasks", methods=["GET"])
def get_plan_tasks(plan_id):

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # ✅ Plan ownership check
    plan = study_plan_collection.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user["_id"]
    })

    if not plan:
        return jsonify({"error": "Access denied"}), 403
    
    tasks = list(task_collection.find(
        {"plan_id": ObjectId(plan_id)
        },
        {
            "_id": 1,
            "topic": 1,
            "phase": 1,
            "weight": 1,
            "status": 1,
            "scheduled_start": 1,
            "scheduled_end": 1,
            "duration_minutes": 1
        }
    ).sort("scheduled_start", 1))

    for task in tasks:
        task["_id"] = str(task["_id"])
        task["scheduled_start"] = task["scheduled_start"].isoformat()
        task["scheduled_end"] = task["scheduled_end"].isoformat()

    return jsonify(tasks)


# ============================================
# MARK TASK COMPLETE
# ============================================

@app.route("/api/task/complete", methods=["POST"])
def mark_task_complete():

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    task_id = data.get("task_id")
    
    if not task_id:
        return jsonify({"error": "task_id required"}), 400

    task = task_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # ✅ Verify task belongs to user's plan
    plan = study_plan_collection.find_one({
        "_id": task["plan_id"],
        "user_id": user["_id"]
    })

    if not plan:
        return jsonify({"error": "Access denied"}), 403

    #Mark task completed
    task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now()
            }
        }
    )

    topic_name = task.get("topic", "Study Session")

    # 🔥 Generate completion motivation
    message = generate_completed_message(topic_name)

    # 🔹 Save notification
    notification_collection.insert_one({
        "plan_id": task["plan_id"],
        "message": message,
        "type": "completion",
        "created_at": datetime.now(),
        "read": False
    })
    
    # 🧠 Progress Intelligence
    evaluate_progress_and_notify(task["plan_id"])
    
    from services.adaptive_level_service import evaluate_adaptive_level
    evaluate_adaptive_level(task["plan_id"])

    print(f"Completion Motivation: {message}")

    return jsonify({
        "status": "updated",
        "message": message
    })


# ============================================
# MARK TASK MISSED
# ============================================

@app.route("/api/task/miss", methods=["POST"])
def mark_task_missed():
    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    task_id = data.get("task_id")
    
    if not task_id:
        return jsonify({"error": "task_id required"}), 400

    task = task_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # ✅ Verify task belongs to user's plan
    plan = study_plan_collection.find_one({
        "_id": task["plan_id"],
        "user_id": user["_id"]
    })

    if not plan:
        return jsonify({"error": "Access denied"}), 403

    # 1️⃣ Mark as missed
    task_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": "missed"}}
    )

    topic_name = task.get("topic", "Study Session")
    plan_id = task["plan_id"]

    # 2️⃣ Generate missed motivation
    from services.motivation_service import generate_missed_message
    message = generate_missed_message(topic_name)

    # 3️⃣ Save notification
    notification_collection.insert_one({
        "plan_id": plan_id,
        "message": message,
        "type": "motivation",
        "created_at": datetime.now(),
        "read": False
    })

    # 4️⃣ Count total missed sessions
    missed_count = task_collection.count_documents({
        "plan_id": plan_id,
        "status": "missed"
    })

    # 5️⃣ Adaptive logic trigger
    if missed_count >= 3:
        from services.rescheduler_service import adaptive_reschedule
        adaptive_reschedule(plan_id)
        
    # 🧠 Progress Intelligence
    evaluate_progress_and_notify(plan_id)
    
    from services.adaptive_level_service import evaluate_adaptive_level
    evaluate_adaptive_level(plan_id)

    return jsonify({
        "status": "updated",
        "missed_count": missed_count,
        "message": message
    })


# ============================================
# PLAN PROGRESS
# ============================================

@app.route("/api/plan/<plan_id>/progress")
def plan_progress(plan_id):

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # ✅ Plan ownership check
    plan = study_plan_collection.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user["_id"]
    })

    if not plan:
        return jsonify({"error": "Access denied"}), 403
    
    plan_id = ObjectId(plan_id)

    total = task_collection.count_documents({"plan_id": plan_id})
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


# ============================================
# RESCHEDULE MISSED
# ============================================

@app.route("/api/plan/<plan_id>/reschedule", methods=["POST"])
def reschedule_plan(plan_id):

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    plan = study_plan_collection.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user["_id"]
    })

    if not plan:
        return jsonify({"error": "Access denied"}), 403
    
    data = request.json

    try:
        new_days = int(data.get("exam_days"))
    except:
        return jsonify({"error": "Invalid exam days"}), 400

    new_sessions = data.get("sessions")

    result = reschedule_missed_tasks(plan_id, new_days, new_sessions)

    return jsonify(result)


# ============================================
# SAVING NOTIFICATION TO DB
# ============================================

@app.route("/api/plan/<plan_id>/notifications", methods=["GET"])
def get_notifications(plan_id):

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    plan = study_plan_collection.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user["_id"]
    })

    if not plan:
        return jsonify({"error": "Access denied"}), 403
    
    notifications = list(notification_collection.find(
        {"plan_id": ObjectId(plan_id)}
    ).sort("created_at", -1))

    clean_notifications = []

    for n in notifications:
        clean_notifications.append({
            "_id": str(n["_id"]),
            "plan_id": str(n["plan_id"]),
            "message": n.get("message"),
            "type": n.get("type"),
            "created_at": n.get("created_at").isoformat() if n.get("created_at") else None,
            "read": n.get("read", False)
        })

    return jsonify(clean_notifications)

# ============================================
# SUPPORT MESSAGE
# ============================================

@app.route("/api/support/<plan_id>", methods=["POST"])
def emotional_support(plan_id):

    user = get_user_from_token()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    plan = study_plan_collection.find_one({
        "_id": ObjectId(plan_id),
        "user_id": user["_id"]
    })

    if not plan:
        return jsonify({"error": "Access denied"}), 403
    
    message = generate_support_message()

    notification_collection.insert_one({
        "plan_id": ObjectId(plan_id),
        "message": message,
        "type": "support",
        "created_at": datetime.now(),
        "read": False
    })

    return jsonify({
        "message": message
    })
    
@app.route("/api/test-blueprint", methods=["POST"])
def test_blueprint():
    from services.weight_engine_service import extract_marks_from_blueprint
    data = request.json
    blueprint = data.get("blueprint_text")
    result = extract_marks_from_blueprint(blueprint)
    return jsonify(result)

@app.route("/api/test-frequency", methods=["POST"])
def test_frequency():
    from services.weight_engine_service import extract_frequency_from_past_questions
    data = request.json
    text = data.get("past_questions_text")
    result = extract_frequency_from_past_questions(text)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)