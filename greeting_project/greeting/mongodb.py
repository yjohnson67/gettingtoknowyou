from pymongo import MongoClient
from django.conf import settings

if not settings.MONGODB_URI:
    raise ValueError("MONGODB_URI is missing. Check your .env file.")

client = MongoClient(settings.MONGODB_URI)

db = client[settings.MONGODB_DB_NAME]
scores_collection = db["scores"]