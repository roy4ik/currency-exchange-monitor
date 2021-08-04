import time
from settings import settings

from mngrs.db_mngr import MongoDataBaseManager
from currency_api_adapters import CurrencyApiAdapter

class DataProcessor:
    def __init__(self, fetch_interval=None):
        self.fetch_interval = fetch_interval
        if not self.fetch_interval:
            self.fetch_interval = settings.CONFIG['exchange_api_fetch_interval_seconds'].get(int)

        self.db_manager = MongoDataBaseManager()

    def run(self):
        while True:
            # fetch data
            currency_fetcher = CurrencyApiAdapter()
            base_currency, target_rates_dict = currency_fetcher.fetch()
            if target_rates_dict:
                # save data to db
                self.db_manager.set_rate(base_currency, target_rates_dict)
            time.sleep(self.fetch_interval)


data_processor = DataProcessor()
data_processor.run()
