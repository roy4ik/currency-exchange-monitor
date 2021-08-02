import requests
from pymongo import MongoClient
import time
import os

db_host = os.environ.get("DB_HOST", "localhost")
print("data processor running")

while True:
    time.sleep(10)
