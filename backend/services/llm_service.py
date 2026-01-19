def generate_schedule(data):
    subject = data["subject"]
    hours = data["hours_per_day"]
    days = data["exam_days"]

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
