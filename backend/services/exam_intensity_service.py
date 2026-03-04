from datetime import datetime, timedelta
def calculate_intensity_multiplier(days_left):
    """
    Returns intensity multiplier based on exam proximity
    """

    if days_left <= 1:
        return 1.8   # revision heavy
    elif days_left <= 3:
        return 1.7
    elif days_left <= 5:
        return 1.4
    elif days_left <= 7:
        return 1.2
    else:
        return 1.0
    


def scale_sessions(sessions, days_left):

    multiplier = calculate_intensity_multiplier(days_left)

    extra_sessions = int(len(sessions) * (multiplier - 1))

    if extra_sessions <= 0:
        return sessions

    scaled_sessions = list(sessions)

    for i in range(extra_sessions):

        last_session = scaled_sessions[-1]

        start = datetime.strptime(last_session["start"], "%H:%M")
        end = datetime.strptime(last_session["end"], "%H:%M")

        duration = end - start

        new_start = end + timedelta(minutes=10)
        new_end = new_start + duration

        scaled_sessions.append({
            "start": new_start.strftime("%H:%M"),
            "end": new_end.strftime("%H:%M")
        })

    return scaled_sessions