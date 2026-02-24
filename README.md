# 📘 EduPlan-AI – LLM-Based Smart Study Scheduler

EduPlan-AI is a time-based intelligent study scheduling system designed for school and college students.
It generates structured study plans, supports multiple daily sessions, tracks progress, and adapts to missed tasks with smart rescheduling.

This project is designed to evolve into an LLM-powered personalized study assistant.

---

## 🚀 Features

### ✅ Core Features (Completed)

* Time-based study scheduling
* Multiple sessions per day (e.g., 5:00–6:30 AM & 6:00–8:30 PM)
* Subject rotation across days
* Task status tracking (Pending / Completed / Missed / Rescheduled)
* Smart rescheduling of missed tasks
* Progress calculation with completion percentage
* MongoDB-based storage
* REST API architecture
* Clean service-layer backend structure

---

## 🧠 Planned Features (Next Phase)

* LLM-powered personalized study planning
* Adaptive scheduling based on performance
* Automatic SMS reminders at scheduled study time
* WhatsApp reminders (future scope)
* User authentication system
* Analytics dashboard

---

## 🏗️ Tech Stack

### Backend

* Python
* Flask
* MongoDB
* APScheduler (for reminders – upcoming)

### Frontend

* React (Vite)
* Custom CSS

### Database

* MongoDB (Local)

---

## 🧩 System Architecture

```
Frontend (React)
        ↓
Flask REST API
        ↓
Service Layer (Scheduler / Rescheduler / LLM)
        ↓
MongoDB
```

---

## 📂 Project Structure

```
backend/
│
├── app.py
├── config.py
├── models/
│   ├── study_plan_model.py
│   ├── task_model.py
│   └── user_model.py
│
├── services/
│   ├── scheduler_service.py
│   ├── rescheduler_service.py
│   ├── llm_service.py
│   └── reminder_service.py (upcoming)
│
frontend/
│
├── src/
│   ├── App.jsx
│   └── App.css
```

---

## ⚙️ How It Works

### 1️⃣ Plan Creation

User provides:

* Subjects
* Exam days
* Study sessions per day (start & end time)

System generates:

* Time-based tasks with scheduled_start and scheduled_end
* Rotated subjects
* Stored in MongoDB

---

### 2️⃣ Progress Tracking

System calculates:

* Total tasks
* Completed tasks
* Missed tasks
* Pending tasks
* Completion percentage

---

### 3️⃣ Smart Rescheduling

If tasks are missed:

* User provides updated timeline
* System rebuilds schedule from current date
* Old pending/missed tasks are replaced
* Completed tasks remain unchanged

---

## 🔌 API Endpoints

### Create Plan

```
POST /api/plan/create
```

### Get Tasks

```
GET /api/plan/<plan_id>/tasks
```

### Mark Task Complete

```
POST /api/task/complete
```

### Mark Task Missed

```
POST /api/task/miss
```

### Get Progress

```
GET /api/plan/<plan_id>/progress
```

### Reschedule Plan

```
POST /api/plan/<plan_id>/reschedule
```

---

## 🧪 Example Request

### Create Plan

```json
{
  "subjects": ["Math", "Physics", "Chemistry"],
  "exam_days": 3,
  "hours_per_day": 4,
  "sessions": [
    { "start": "05:00", "end": "06:30" },
    { "start": "18:00", "end": "20:00" }
  ]
}
```

---

## 📈 Future Research Direction

* Using LLM to:

  * Detect study patterns
  * Adjust workload dynamically
  * Suggest optimal time slots
  * Prevent burnout
  * Provide motivational nudges

* Integration with SMS/WhatsApp APIs for real-time reminders

---

## 🎓 Academic Value

This project demonstrates:

* REST API design
* Service-layer architecture
* Time-based scheduling logic
* Adaptive rescheduling algorithms
* MongoDB schema design
* Frontend-backend integration
* Extensibility for AI integration

---

## 👩‍💻 Author

Final Year Project – LLM-Based Study Scheduler
Developed using Flask, React, and MongoDB.

---

