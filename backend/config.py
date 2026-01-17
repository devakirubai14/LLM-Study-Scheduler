from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")  # Update if needed
db = client["study_scheduler"]  # Your database name
