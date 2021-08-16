from settings import settings
from pymongo import MongoClient, errors
import datetime
import time


class DataBaseManager:
    def connect(self):
        raise NotImplementedError

    def get_rates(self, currency_code, n_recent_rates=1, required_target_currencies=['GBP']):
        raise NotImplementedError

    def set_rate(self, currency_code, target_rates):
        timestamp = datetime.datetime.now().timestamp()
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

    def get_rates(self, currency_code, n_recent_rates=1, required_target_currencies=["GBP"]):
        """gets the rate entries from the db. if n_recent_rates is not defined it will provide the current rate
        Args:
            currency_code (str): currency code like 'EUR'
            n_recent_rates (int): amount of rates to be returned sorted by newest to oldest
            required_target_currencies (list): rrequired_target_currencies
        Returns:
            rates (list): list of tuples of rates sorted by newest to oldest [(timestamp, rates), ..]
        """
        try:
            # get results sorted by latest timestamp first, and limited by n_recent_rates
            required_target_currencies_query = [{f"rate.{currency.upper()}": {"$exists": True}}
                                                for currency in required_target_currencies]
            results = self.collection.find({"$and": [{"currency_code": currency_code.upper()},
                                                     *required_target_currencies_query]
                                            }).sort("timestamp", -1).limit(n_recent_rates)
            if results.count(with_limit_and_skip=True) == n_recent_rates:
                print(f"results found: {results.count(with_limit_and_skip=True)}")
                return [(result.get('timestamp'), result.get('rates')) for result in results]
            else:
                print(f"Warning - less than requested rates found in db "
                      f"({results.count(with_limit_and_skip=True)}), returning [(None, None)]")
                return [(None, None)]
        except errors.ServerSelectionTimeoutError as e:
            print(e)
            self.connect(retry_limit=0)
            return [(None, None)]

    def set_rate(self, currency_code, target_rates):
        """saves the rate and all target rates included in target rates to the db
        Args:
            currency_code (str): currency code like 'EUR'
            target_rates (dict): {'eur': 1, 'chf': 1.2}
        Returns:
            timestamp (float): timestamp is returned if a rate entry has been made, otherwise returns None
        """
        timestamp = datetime.datetime.utcnow().timestamp()
        # get most recent rate to check if it a newer rate is available
        timestamp_to_update, rates_to_update = self.get_rates(currency_code,
                                                              n_recent_rates=1,
                                                              required_target_currencies=list(target_rates.keys()))[0]
        document = {
            "currency_code": currency_code.upper(),
            'timestamp': timestamp,
            "rates": {k.upper(): v for k, v in target_rates.items()}
        }
        try:
            if rates_to_update:
                time_delta = datetime.datetime.fromtimestamp(timestamp) - \
                             datetime.datetime.fromtimestamp(timestamp_to_update)
                # only save rate if rates changed
                # TODO: check on currency base
                #  - currently adding a currency will cause to saving new rates even if only one is new or changed
                if time_delta.total_seconds() > settings.CONFIG['exchange_api_fetch_interval_seconds'].get(int) and \
                        rates_to_update != target_rates:
                    saved_rate = self.collection.insert_one(document)
                    print(f"saving rates to db:\n{document}, {saved_rate.acknowledged}")
                    return timestamp
                else:
                    print(f"Setting rate: found existing rates: {timestamp_to_update}, {rates_to_update}")
                    print("rates didn't change no update needed")
                    return
            else:
                # if never run insert below code to make sure you have a low exchange rate for testing
                initial_rates = {"rates": {"CHF": 0.00001, "GBP": 0.00001, "EUR": 0.00001}}
                document.update(initial_rates)
                saved_rate = self.collection.insert_one(document)
                print(f"saving initial rates to db:\n{document}, {saved_rate.acknowledged}")
                return timestamp
        except errors.ServerSelectionTimeoutError as e:
            print(e)

# TODO: clean up rates to only keep a certain amount of rates in db

#     def delete_rate(self, timestamp):
#         """deletes a rate entry from db based on a timestamp"""
#         results = self.db.find_one({"timestamp": timestamp})
#         return self.db.delete_one(results).deleted_count
