from collections import defaultdict


def reorder_sessions_by_cognitive_curve(tasks, adaptive_level):
    """
    Reorders sessions per day based on adaptive level.

    low    → Easy → Medium → Hard
    high   → Hard → Medium → Easy
    medium → Keep original order
    """

    if adaptive_level == "medium":
        return tasks  # no change

    # Group tasks by date
    tasks_by_date = defaultdict(list)

    for task in tasks:
        date_key = task["scheduled_start"].date()
        tasks_by_date[date_key].append(task)

    reordered_tasks = []

    for date, day_tasks in tasks_by_date.items():

        # Sort by weight
        if adaptive_level == "low":
            # Easy first (lower weight first)
            day_tasks_sorted = sorted(day_tasks, key=lambda x: x.get("weight", 1))
        elif adaptive_level == "high":
            # Hard first (higher weight first)
            day_tasks_sorted = sorted(day_tasks, key=lambda x: x.get("weight", 1), reverse=True)
        else:
            day_tasks_sorted = day_tasks

        # After sorting by difficulty, preserve original time slots
        # Reassign topics in new order but keep time slots intact

        sorted_by_time = sorted(day_tasks, key=lambda x: x["scheduled_start"])

        for original_slot, reordered_task in zip(sorted_by_time, day_tasks_sorted):
            original_slot["topic"] = reordered_task["topic"]
            original_slot["weight"] = reordered_task.get("weight", 1)

        reordered_tasks.extend(sorted_by_time)

    return reordered_tasks