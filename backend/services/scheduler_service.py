from datetime import datetime, timedelta, time


def build_priority_based_plan(topics_with_priority, days, sessions_per_day, start_date):
    """
    topics_with_priority format:
    [
        {"topic": "Algebra", "priority": "High"},
        {"topic": "Calculus", "priority": "Medium"},
        {"topic": "Trigonometry", "priority": "Low"}
    ]
    """

    tasks = []

    # 🔹 Step 1: Expand topics based on priority weight
    weighted_topics = []

    for item in topics_with_priority:
        topic = item["topic"]
        priority = item["priority"]

        if priority == "High":
            weighted_topics.extend([item] * 3)  # High appears 3 times
        elif priority == "Medium":
            weighted_topics.extend([item] * 2)  # Medium appears 2 times
        else:
            weighted_topics.append(item)  # Low appears once

    if not weighted_topics:
        return []

    topic_index = 0
    topic_count = len(weighted_topics)

    # 🔹 Step 2: Generate time-based schedule
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

            duration_minutes = int(
                (scheduled_end - scheduled_start).total_seconds() / 60
            )

            topic_data = weighted_topics[topic_index % topic_count]

            tasks.append({
                "topic": topic_data["topic"],
                "priority": topic_data["priority"],
                "scheduled_start": scheduled_start,
                "scheduled_end": scheduled_end,
                "duration_minutes": duration_minutes,
                "status": "pending",
                "reminder_sent": False,
                "type": "study",
                "created_at": datetime.now()
            })

            topic_index += 1

    return tasks