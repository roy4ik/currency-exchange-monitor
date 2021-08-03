import requests
import time

from settings import settings
from mngrs.db_mngr import MongoDataBaseManager


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
            # save data to db
            self.db_manager.set_rate(base_currency, target_rates_dict)

            time.sleep(self.fetch_interval)


class CurrencyFetcher:
    def __init__(self, base_currency=None, target_currency_codes=None):
        self.base_currency = base_currency
        if not base_currency:
            self.base_currency = settings.CONFIG['base_currency'].get(str)
        self.target_currency_codes = target_currency_codes
        if not target_currency_codes:
            self.target_currency_codes = settings.CONFIG['target_currency_codes'].get(list)

    @staticmethod
    def get_api_url():
        return settings.CONFIG['<api-uri-setting>'].get(str)

    def get_latest(self) -> tuple:
        """
        gets the latest exchange rates
        Returns:
            base, rates (tuple): returns the base currency code and a dictionary of rates
        """
        raise NotImplementedError

    def fetch(self):
        """fetches currency data
        Returns:
            base, rates (tuple): returns the base currency code and a dictionary of rates
        """
        return self.get_latest()

    def run(self):
        """
        runs a fetch and returns its results
        Returns:
            base, rates (tuple): returns the base currency code and a dictionary of rates
        """
        results = self.fetch()
        return results


class CurrencyApiAdapter(CurrencyFetcher):
    """Currency-api https://github.com/fawazahmed0/currency-api#readme"""
    def __init__(self, base_currency="USD", target_currency_codes=['EUR', 'CHF']):
        super().__init__(base_currency, target_currency_codes)

    @staticmethod
    def get_api_url():
        return settings.CONFIG['exchange_api_uri'].get(str)

    def get_latest(self):
        """
        gets the latest exchange rates
        Returns:
            base, rates (tuple): returns the base currency code and a dictionary of rates
        """
        url = f"{self.get_api_url()}+latest"
        # set api parameters
        params = {}
        params.update({'base': self.base_currency})
        params.update({'symbols': ','.join(self.target_currency_codes)})
        # call the api for rates
        response = requests.get(url, params=params)
        base, rates = response.json().get('base'), response.json().get('rates')
        # remove base currency from rates if it is returned by the data source
        rates.pop(self.base_currency, None)
        return base, rates


data_processor = DataProcessor()
data_processor.run()
