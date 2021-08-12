import time

from settings import settings
from mngrs.mq_manager import MessageBroker
from mngrs.db_mngr import MongoDataBaseManager


class AlertsMonitor:
    def __init__(self,
                 base_currency=settings.CONFIG['base_currency'].get(str),
                 target_currency_codes=settings.CONFIG['target_currency_codes'].get(list),
                 fetch_interval=settings.CONFIG['exchange_api_fetch_interval_seconds'].get(int),
                 threshold=settings.CONFIG['currency_change_threshold'].get(float)):
        self.fetch_interval = fetch_interval
        self.db_manager = MongoDataBaseManager()
        self.base_currency = base_currency
        self.target_currency_codes = target_currency_codes
        self.threshold = threshold
    message_broker = MessageBroker()

    def monitor(self):
        # set n_recent rates minimum to 2 to get more than one rate, otherwise can't compare
        rates = self.db_manager.get_rates(
            self.base_currency,
            n_recent_rates=2,
            required_target_currencies=self.target_currency_codes)
        self._monitor_rate_increase(rates)

    def _monitor_rate_increase(self, rates):
        if len(rates) > 1:
            # check increase for every target currency
            for target_currency in self.target_currency_codes:
                #     get timestamps and rates to compare
                latest_timestamp, latest_rates = rates[0][0], rates[0][1]
                previous_timestamp, previous_rates = rates[-1][0], rates[-1][1]
                # if both timestamps exist compare rates
                if latest_timestamp and previous_timestamp:
                    latest_rate = latest_rates.get(target_currency)
                    previous_rate = previous_rates.get(target_currency)
                    # check if rate exists for both timestamps
                    if latest_rate and previous_rate:
                        rate_delta = latest_rate - previous_rate
                        print(f"{target_currency}:\n"
                              f"\tts: {latest_timestamp}\t\tlatest rate: {latest_rate}\n"
                              f"\tts: {previous_timestamp}\t\tprevious rate: {previous_rate}")
                        # compare delta to threshold
                        if rate_delta >= self.threshold:
                            # rate increase higher or equal threshold -> send alert!
                            self.send_alert(target_currency, latest_rate, rate_delta)
                        else:
                            print(f"{self.base_currency} -> {target_currency} rate not increased beyond threshold")

    def send_alert(self, target_currency, latest_rate, rate_delta):
        """sends alert to message broker
        Args:
            target_currency (str):
            latest_rate (float):
            rate_delta (float):
        """
        alert = f"Exchange rate of {target_currency} increased beyond threshold ({float(self.threshold)}%) ! " \
                f"{self.base_currency} -> {target_currency}:\t{latest_rate} , increase:\t{rate_delta} "
        #   send to MQ
        print(f"Sent alert: {alert}")
        self.message_broker.send(alert)

    def run(self):
        while True:
            if self.message_broker.producer:
                self.monitor()
                time.sleep(self.fetch_interval)
            else:
                self.message_broker.set_producer(retry_limit=0)


alerts_monitor = AlertsMonitor()
alerts_monitor.run()
