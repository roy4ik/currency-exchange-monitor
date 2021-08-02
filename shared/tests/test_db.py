from pymongo import MongoClient
import os
import pytest
from settings import settings
print("data processor tests running")


class TestDatabase:
    db_uri = settings.CONFIG['mongo']['db_uri'].get(str)

    def test_mongo_connection(self):
        client = MongoClient(self.db_uri, username='root', password='example')
        assert client.admin.command('ping')

    def test_mongo_exchange_db_exists(self):
        try:
            client = MongoClient(self.db_uri,  username='root', password='example')
            dbs = client.list_database_names()
            if 'exchange_rates' not in dbs:
                db = client.exchange_rates
                print("Mongo Connected - exchange_rates exists")
                assert db.exchange_rates
            else:
                db = client.exchange_rates
                assert db
                print("Mongo Connected - exchange_rates created")
        except Exception as e:
            print(e)
            raise e

    def test_mongo_exchange_db_write_case(self):
        try:
            client = MongoClient(self.db_uri, username='root', password='example')
            db = client.exchange_rates
            test = db.exchange_rates.insert_one({"test_entry": "TEST"}).inserted_id
            test_result = db.exchange_rates.find_one()
            db.exchange_rates.delete_one(test)
            print(test)
            print(test_result)
        except Exception as e:
            print(e)
            raise e