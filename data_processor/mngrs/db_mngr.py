from settings import settings, read_key_from_file
from pymongo import MongoClient
import datetime


class DataBaseManager:
    def connect(self):
        raise NotImplementedError

    def get_rates(self, currency_code, n_recent_rates=1, required_target_currencies=['GBP']):
        raise NotImplementedError

    def set_rate(self, currency_code, target_rates):
        timestamp = datetime.datetime.now().timestamp()
        raise NotImplementedError

    def delete_rate(self, timestamp):
        raise NotImplementedError


class MongoDataBaseManager(DataBaseManager):
    def __init__(self):
        super().__init__()
        self.db = self.connect()

    def connect(self):
        try:
            print(f"Trying to connect to db with username: {settings.CONFIG['mongo']['user'].get(str)}")
            client = MongoClient(settings.CONFIG['mongo']['db_uri'].get(str),
                                 username=read_key_from_file('user', 'mongo'),
                                 password=read_key_from_file('password', 'mongo'),
                                 authSource="admin")
            if client:
                print('Connected to mongo successfully')
            db = client[settings.CONFIG['mongo']['collection_name'].get(str)]
            collection = db[settings.CONFIG['mongo']['collection_name'].get(str)]

            print(f"DB: {db}\n collection: {collection}")
            return collection
        except ConnectionError as e:
            raise e

    def get_rates(self, currency_code, n_recent_rates=1, required_target_currencies=['GBP']):
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
            results = self.db.find({"currency_code": currency_code.upper()}
                                   ).sort("timestamp", -1).limit(n_recent_rates)
            if results.count(with_limit_and_skip=True) == n_recent_rates:
                print(f"results found: {results.count(with_limit_and_skip=True)}")
                if required_target_currencies:
                    # TODO: optimization -> move filter to query ("$exists") ..didn't work so far
                    return [(result.get('timestamp'), result.get('rates')) for result in results
                            if [result.get('rates', {}).get(target) for target in required_target_currencies]]
                else:
                    return [(result.get('timestamp'), result.get('rates')) for result in results]
            else:
                print("Warning - less than requested rates found in db, returning [(None, None)]")
                return [(None, None)]
        except ConnectionError as e:
            print(e)
            self.connect()

    def set_rate(self, currency_code, target_rates) -> float:
        """saves the rate and all target rates included in target rates to the db
        Args:
            currency_code (str): currency code like 'EUR'
            target_rates (dict): {'eur': 1, 'chf': 1.2}
        Returns:
            timestamp (float):
        """
        timestamp = datetime.datetime.utcnow().timestamp()
        timestamp_to_update, rates_to_update = self.get_rates(currency_code,
                                                              n_recent_rates=1,
                                                              required_target_currencies=list(target_rates.keys()))[0]
        document = {"currency_code": currency_code, 'timestamp': timestamp, "rates": target_rates}
        if rates_to_update:
            print(f"found existing rates: {timestamp_to_update}, {rates_to_update}")
            time_delta = datetime.datetime.fromtimestamp(timestamp) - \
                         datetime.datetime.fromtimestamp(timestamp_to_update)
            if time_delta.total_seconds() > settings.CONFIG['exchange_api_fetch_interval_seconds'].get(int) and \
                    rates_to_update != target_rates:
                try:
                    saved_rate = self.db.insert_one(document)
                    print(f"saving rates to db:\n{document}, {saved_rate.acknowledged}")
                    return timestamp
                except ConnectionError as e:
                    print(e)
            else:
                print("rates didn't change no update needed")
                return
        else:
            saved_rate = self.db.insert_one(document)
            print(f"saving initial rates to db:\n{document}, {saved_rate.acknowledged}")
            return timestamp

    def delete_rate(self, timestamp):
        """deletes a rate entry from db based on a timestamp"""
        results = self.db.find_one({"timestamp": timestamp})
        return self.db.delete_one(results).deleted_count

