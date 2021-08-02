import requests
from pymongo import MongoClient
import time
from settings import settings


class DataProcessor:
    db_uri = settings.CONFIG['mongo']['db_uri'].get(str)
    client = MongoClient(db_uri, username='mongo', password='mongo')
    print(f"connecting to {db_uri}")

    def run(self, fetch_interval):
        while True:
            # connect to db
            if self.client:
                print('connected to mongo successfully')
            else:
                client = MongoClient(self.db_uri,
                                     username=settings.CONFIG['mongo']['user'].get(str),
                                     password=settings.CONFIG['mongo']['password'].get(str))

            self.get_latest(target_currency_codes=['EUR', 'CHF'])
            time.sleep(fetch_interval)

    @staticmethod
    def get_api_url():
        return settings.CONFIG['exchange_api_uri'].get(str)

    def get_latest(self, base_currency=None, target_currency_codes=None):
        url = f"{self.get_api_url()}+latest"
        params = {}
        if base_currency:
            params.update({'base': base_currency})
        if target_currency_codes:
            params.update({'symbols': ','.join(target_currency_codes)})
        response = requests.get(url, params=params)
        data = response.json()
        print(data)
        return data


data_processor = DataProcessor()
fetch_interval = settings.CONFIG['exchange_api_fetch_interval_seconds'].get(int)
print(f"running data processor with fetch inverval: {fetch_interval}")
data_processor.run(fetch_interval)
