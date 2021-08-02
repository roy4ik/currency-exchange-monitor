from pymongo import MongoClient
import os



db_host = os.environ.get("DB_HOST", "localhost")
print("alerts monitor running")
