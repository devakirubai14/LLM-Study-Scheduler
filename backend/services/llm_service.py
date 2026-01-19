def generate_schedule(data):
    subject = data.get("subject", "")

    # Convert safely to int
    try:
        hours = int(data.get("hours_per_day", 0))
        days = int(data.get("exam_days", 0))
    except ValueError:
        return ["Invalid input: hours and days must be numbers"]

    # return f"Study {subject} for {hours} hours daily for {days} days. Revise on the last day." - first done
    plan = []
    
    # Adaptive logic based on exam proximity
    if days <= 3:
        plan.append("High Priority: Focus only on core topics and revision") 
    
    for day in range(1, days + 1):
        if day == days:
            plan.append(f"Day {day}: Revise {subject} for {hours} hours")
        else:
            plan.append(f"Day {day}: Study {subject} for {hours} hours")
    
    return plan
