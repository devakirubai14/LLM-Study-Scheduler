from flask import request
from models.user_model import users_collection


def get_user_from_token():

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split(" ")

    if len(parts) != 2 or parts[0] != "Bearer":
        return None

    token = parts[1]

    user = users_collection.find_one({"token": token})

    return user