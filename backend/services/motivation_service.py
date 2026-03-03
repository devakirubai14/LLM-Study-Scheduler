import random

def generate_missed_message(topic):
    messages = [
        f"You missed {topic}, but that's okay. Progress is not always linear 💛",
        f"A small setback in {topic}. Let’s bounce back stronger 💪",
        f"Even toppers miss sessions sometimes. Let’s retry {topic} 🔥",
        f"You’re capable of 90+. Let’s take control of {topic} next time ✨",
        f"Missing one session won’t define you. Your comeback will 💯"
    ]
    return random.choice(messages)

def generate_completed_message(topic):
    messages = [
        f"Great job completing {topic}! Momentum is building 🚀",
        f"You’re becoming consistent. {topic} done ✔",
        f"That’s discipline! {topic} completed 💪",
        f"Keep this up and 90+ is yours 🎯",
        f"You showed up for {topic}. That’s powerful."
    ]
    return random.choice(messages)

def generate_support_message():
    messages = [
        "It’s okay to feel tired. Even strong students have slow days 💛",
        "Marks don’t define you. Your effort does. And you’re trying.",
        "Take a deep breath. One small step today is enough.",
        "You don’t have to be perfect. Just don’t give up.",
        "You are stronger than this moment. Keep going 🌟"
    ]
    return random.choice(messages)

def generate_high_performance_message():
    messages = [
        "Outstanding consistency! You're operating at a top performer level 🔥",
        "This is elite discipline. Keep going — you're exam ready 🚀",
        "High performance detected. This is how toppers train 🎯",
        "You're not just studying. You're mastering it 💎",
        "This momentum is dangerous — in a good way 😎"
    ]
    import random
    return random.choice(messages)