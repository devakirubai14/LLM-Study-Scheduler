def build_basic_plan(subjects, days, hours_per_day):
    tasks = []

    per_day_hours = hours_per_day / len(subjects)

    for day in range(1, days + 1):
        for sub in subjects:
            tasks.append({
                "day": day,
                "subject": sub,
                "duration_hours": round(per_day_hours, 2),
                "type": "study",
                "status": "pending"
            })

    return tasks
