from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]
scores_collection = db["scores"]