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
            currency_fetcher = CurrencyApiAdapter(base_currency="USD")
            base_currency, rates_dict = currency_fetcher.fetch()
            if rates_dict:
                # save data to db
                self.db_manager.set_rates(base_currency, rates_dict)
            time.sleep(self.fetch_interval)

        # # # testing rates increase/decrease --comment out after test -> move to tests file
        # rates_dicts = [{"EUR": 0.1, "CHF": 0.2}, {"EUR": 0.3, "CHF": 0.4}, {"EUR": 0.1, "CHF": 0.2},
        # {"EUR": 0.5, "CHF": 0.1}, {"EUR": 0.1, "CHF": 0.2},
        # {"EUR": 0.3, "CHF": 0.4}, {"EUR": 0.1, "CHF": 0.2}, {"EUR": 0.5, "CHF": 0.1}, {"EUR": 0.1, "CHF": 0.2},
        # {"EUR": 0.3, "CHF": 0.4}, {"EUR": 0.1, "CHF": 0.2}, {"EUR": 0.5, "CHF": 0.1}, {"EUR": 0.1, "CHF": 0.2},
        # {"EUR": 0.3, "CHF": 0.4}, {"EUR": 0.1, "CHF": 0.2}, {"EUR": 0.5, "CHF": 0.1}]
        # for rates_dict in rates_dicts:
        #     if rates_dict:
        #         # save data to db
        #         self.db_manager.set_rates("USD", rates_dict)
        #     time.sleep(self.fetch_interval)


db_manager = MongoDataBaseManager()

# run data processor
data_processor = DataProcessor()
data_processor.run()
