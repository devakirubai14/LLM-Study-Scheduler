# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import db

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "LLM Backend Running Successfully!"})

# @app.route("/test-db")
# def test_db():
#     db.test.insert_one({"status": "MongoDB connected"})
#     return {"message": "MongoDB test document inserted"}

# @app.route("/debug-db")
# def debug_db():
#     return {
#         "database": db.name,
#         "collections": db.list_collection_names()
#     }


if __name__ == '__main__':
    app.run(debug=True)

