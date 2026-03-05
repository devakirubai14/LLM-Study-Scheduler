import bcrypt
import secrets
from datetime import datetime
from models.user_model import users_collection


# ================================
# REGISTER USER
# ================================
def register_user(name, email, password):

    # Normalize email
    email = email.lower().strip()

    existing = users_collection.find_one({"email": email})

    if existing:
        return None, "Email already registered"

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    user = {
        "name": name,
        "email": email,
        "password": password_hash,
        "token": None,
        "device_token": None,
        "created_at": datetime.now()
    }

    result = users_collection.insert_one(user)

    return str(result.inserted_id), None


# ================================
# LOGIN USER
# ================================
def login_user(email, password):

    # Normalize email
    email = email.lower().strip()

    user = users_collection.find_one({"email": email})

    if not user:
        return None, "Invalid email"

    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return None, "Invalid password"

    # Generate login token
    token = secrets.token_hex(32)

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"token": token}}
    )

    return token, None