from fcm_service import send_push_notification

try:
    response = send_push_notification(
        "fake_token_123",
        "EduPlan Test",
        "Firebase connection working"
    )

    print("Firebase response:", response)

except Exception as e:
    print("Firebase error:", e)