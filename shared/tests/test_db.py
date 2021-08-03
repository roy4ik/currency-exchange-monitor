from pymongo import MongoClient
import os
import pytest
from mngrs.db_mngr import MongoDataBaseManager
from settings import settings
print("data processor tests running")


class TestDatabase:
    db_manager = MongoDataBaseManager()

    def test_mongo_connection(self):
        assert self.db_manager.db.command('ping')

    def test_mongo_exchange_db_write_case(self):
        test = self.db_manager.set_rate('usd', {'eur': 1, 'chf': 1.2})
        assert self.db_manager.delete_rate(test)
