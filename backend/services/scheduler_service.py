from datetime import datetime, timedelta, time
import math


def build_priority_based_plan(topics_with_priority, days, sessions_per_day, start_date):

    tasks = []

    # 🔥 Sort topics by weight descending
    topics_sorted = sorted(
        topics_with_priority,
        key=lambda x: x.get("weight", 1),
        reverse=True
    )

    # 🔥 Flatten all session slots first
    all_session_slots = []

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        for session in sessions_per_day:
            start_parts = session["start"].split(":")
            end_parts = session["end"].split(":")

            start_time = time(int(start_parts[0]), int(start_parts[1]))
            end_time = time(int(end_parts[0]), int(end_parts[1]))

            scheduled_start = datetime.combine(current_date, start_time)
            scheduled_end = datetime.combine(current_date, end_time)

            if scheduled_end <= scheduled_start:
                continue

            duration = int((scheduled_end - scheduled_start).total_seconds() / 60)

            all_session_slots.append({
                "start": scheduled_start,
                "end": scheduled_end,
                "duration": duration
            })

    total_sessions = len(all_session_slots)

    if total_sessions == 0:
        return []

    total_weight = sum(t.get("weight", 1) for t in topics_sorted)
    if total_weight == 0:
        total_weight = 1

    # ========================================
    # 🎯 STEP 1: Assign session count by weight
    # ========================================

    topic_session_counts = []

    for topic in topics_sorted:
        weight = topic.get("weight", 1)
        proportional_sessions = (weight / total_weight) * total_sessions
        assigned_sessions = math.floor(proportional_sessions)

        topic_session_counts.append({
            "topic": topic["topic"],
            "weight": weight,
            "sessions": assigned_sessions
        })

    # ========================================
    # 🎯 STEP 2: Minimum 1 session per topic
    # ========================================

    for topic_data in topic_session_counts:
        if topic_data["sessions"] == 0:
            topic_data["sessions"] = 1

    # ========================================
    # 🎯 STEP 3: Adjust to match total sessions
    # ========================================

    assigned_total = sum(t["sessions"] for t in topic_session_counts)

    while assigned_total > total_sessions:
        # Remove 1 session from lowest weight topic
        lowest = min(topic_session_counts, key=lambda x: x["weight"])
        if lowest["sessions"] > 1:
            lowest["sessions"] -= 1
            assigned_total -= 1
        else:
            break

    while assigned_total < total_sessions:
        # Add 1 session to highest weight topic
        highest = max(topic_session_counts, key=lambda x: x["weight"])
        highest["sessions"] += 1
        assigned_total += 1
        
    # Build topic → weight lookup
    topic_weight_lookup = {
        t["topic"]: t.get("weight", 1)
        for t in topics_sorted
    }

    # ========================================
    # 🎯 STEP 4: Interleave sessions
    # ========================================

    session_sequence = []

    while any(t["sessions"] > 0 for t in topic_session_counts):
        for topic_data in topic_session_counts:
            if topic_data["sessions"] > 0:
                session_sequence.append(topic_data["topic"])
                topic_data["sessions"] -= 1

    # ========================================
    # 🎯 STEP 5: Map topics to actual time slots
    # ========================================

    phase_cycle = ["study", "solve", "revise"]
    
    for slot, topic_name in zip(all_session_slots, session_sequence):

        weight = topic_weight_lookup.get(topic_name, 1)

        phase = phase_cycle[len(tasks) % 3]

        tasks.append({
            "topic": topic_name,
            "phase": phase,
            "weight": weight,
            "scheduled_start": slot["start"],
            "scheduled_end": slot["end"],
            "duration_minutes": slot["duration"],
            "status": "pending",
            "reminder_sent": False,
            "type": "study",
            "created_at": datetime.now()
        })

    return tasks