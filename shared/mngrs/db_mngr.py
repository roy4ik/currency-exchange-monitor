import pymongo

from settings import settings
from pymongo import MongoClient, errors
import datetime
import time


class DataBaseManager:
    def connect(self):
        raise NotImplementedError

    def get_rates(self, currency_code, n_recent_rates=1, target_currency='GBP'):
        raise NotImplementedError

    def set_rates(self, currency_code, target_rates):
        timestamp = int(datetime.datetime.now().timestamp())
        raise NotImplementedError

    # def delete_rate(self, timestamp):
    #     raise NotImplementedError


class MongoDataBaseManager(DataBaseManager):
    def __init__(self):
        super().__init__()
        self.db = self.connect(0)
        self.collection = self.get_collection()

    def connect(self, retry_limit=10, reconnect_time_seconds=5):
        n_attempt = 0
        while True:
            n_attempt += 1
            print(f"Trying to connect to DB: attempt: {n_attempt}")
            try:
                print(f"Trying to connect to db with username: {settings.CONFIG['mongo']['user'].get(str)}")
                client = MongoClient(settings.CONFIG['mongo']['db_uri'].get(str),
                                     username=settings.read_key_from_file('user', 'mongo'),
                                     password=settings.read_key_from_file('password', 'mongo'),
                                     authSource="admin")
                if client:
                    db = client[settings.CONFIG['mongo']['collection_name'].get(str)]
                    if db.command('ping'):
                        print('Connected to mongo successfully')
                        print(f"DB: {db}\n collection: {db}")
                    return db

            except errors.ServerSelectionTimeoutError as e:
                print(e)
            except errors.ConnectionFailure as e:
                print(e)
            finally:
                if retry_limit and n_attempt == retry_limit:
                    raise ConnectionError("Could not connect to db!")
                time.sleep(reconnect_time_seconds)

    def get_collection(self):
        return self.db[settings.CONFIG['mongo']['collection_name'].get(str)]

    def get_rates(self, currency_code, n_recent_rates=1, target_currency="GBP", sort_newest_to_oldest=True) -> list:
        """gets the rate entries from the db. if n_recent_rates is not defined it will provide the current rate
        Args:
            currency_code (str): currency code like 'EUR'
            n_recent_rates (int): amount of rates to be returned sorted by newest to oldest
            target_currency (str): required_target_currency code
            sort_newest_to_oldest (bool): sorts results descending from newest to oldest rate
        Returns:
            rates (list): list of tuples of rates sorted by newest to oldest [(timestamp, rate), ..]
        """
        try:
            # get results sorted by latest timestamp first, and limited by n_recent_rates
            query = {"$and": [{"currency_code": currency_code.upper()},
                              {f"rates.{target_currency.upper()}": {"$exists": True}}]}
            results_cursor = self.collection.find(query).sort("timestamp", pymongo.DESCENDING).limit(n_recent_rates)
            results = [(result.get('timestamp'), result.get('rates').get(target_currency))
                       for result in results_cursor]
            if len(results) == n_recent_rates:
                return results
            else:
                print(f"Warning - less than requested ({n_recent_rates}) rates found in db: "
                      f"\ttarget currency: {target_currency} "
                      f"({len(results)}), returning [(None, None)]")
                return [(None, None)]
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            self.connect(retry_limit=0)
            return [(None, None)]

    def set_rates(self, currency_code, new_rates):
        """saves the rate and all target rates included in target rates to the db
        Args:
            currency_code (str): currency code like 'EUR'
            new_rates (dict): {'EUR': 1, 'CHF': 1.2}
        Returns:
            timestamp (int): timestamp is returned if a rate entry has been made, otherwise returns None
        """
        # get most recent rate to check if it has a newer rate is available
        updates = {}

        for currency, new_rate in new_rates.items():
            # get existing rates
            if new_rate is not None:
                rate = self.get_rates(currency_code,
                                      n_recent_rates=1,
                                      target_currency=currency,
                                      sort_newest_to_oldest=True)[0][1]
                if rate != new_rate:
                    if rate is None:
                        # rate does not exist -> add to updates:
                        print(f"saving initial data for {currency}: {new_rate}")
                    else:
                        print(f"saving rate change: new:\t{new_rate} -> old:\t{rate}")
                        # rate changed -> add to updates
                    updates.update({currency: new_rate})

        timestamp = int(datetime.datetime.utcnow().timestamp())
        if updates:
            try:
                document = {
                    "currency_code": currency_code.upper(),
                    'timestamp': timestamp,
                    "rates": updates
                }
                # save rate to db
                saved_rate = self.collection.insert_one(document)
                if saved_rate.acknowledged:
                    print(f"Successfully saved rates to db:\n{document}")
                    return timestamp
            except errors.ServerSelectionTimeoutError as e:
                print(e)
