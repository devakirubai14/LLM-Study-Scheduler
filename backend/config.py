import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = MongoClient("mongodb://localhost:27017/")  # Update if needed
db = client["study_scheduler"]  # Your database name
