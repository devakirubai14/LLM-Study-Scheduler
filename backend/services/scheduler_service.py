from datetime import datetime, timedelta, time


def build_time_based_plan(subjects, days, sessions_per_day, start_date):
    """
    subjects: list of subjects
    days: total exam days
    sessions_per_day: list of dicts like:
        [
            {"start": "05:00", "end": "06:30"},
            {"start": "18:00", "end": "20:30"}
        ]
    start_date: datetime.date object
    """

    tasks = []
    subject_index = 0
    subject_count = len(subjects)

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

            subject = subjects[subject_index % subject_count]

            tasks.append({
                "subject": subject,
                "scheduled_start": scheduled_start,
                "scheduled_end": scheduled_end,
                "duration_minutes": duration_minutes,
                "status": "pending",
                "reminder_sent": False,
                "type": "study",
                "created_at": datetime.utcnow()
            })

            subject_index += 1

    return tasks