from kafka import KafkaProducer, KafkaConsumer, errors
import json
import time
import requests

from settings import settings


class MessageBroker:
    def __init__(self, topic='exchange_rate_increase'):
        self.topic = topic
        self.producer = self.set_producer()

    def set_producer(self,
                     reconnect_time_seconds=5,
                     bootstrap_servers=settings.CONFIG['kafka']['bootstrap_servers'].get(list),
                     retry_limit=10):
        n_attempt = 0
        while True:
            n_attempt += 1
            try:
                return self.connect_producer(bootstrap_servers)
            except errors.KafkaTimeoutError as e:
                if retry_limit and n_attempt == retry_limit:
                    raise ConnectionError("Could not connect to kafka!")
                print(e)
                time.sleep(reconnect_time_seconds)
                print(f'Trying to reconnect to {bootstrap_servers} in {reconnect_time_seconds} seconds')

    @staticmethod
    def connect_producer(bootstrap_servers):
        return KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            api_version=(0, 10),
            value_serializer=lambda x:
            json.dumps(x).encode('utf-8'))

    def send(self, message):
        print(f'sent message: {message}')
        self.producer.send(self.topic, value=message)


class MessageConsumer:
    def __init__(self, topic='exchange_rate_increase'):
        self.consumer = self.set_consumer(topic)
        self.consumer.subscribe([topic])

    def set_consumer(self,
                     topic,
                     reconnect_time_seconds=5,
                     bootstrap_servers=settings.CONFIG['kafka']['bootstrap_servers'].get(list),
                     retry_limit=10):
        n_attempt = 0
        while True:
            n_attempt += 1
            try:
                return self.consumer_connect(topic, bootstrap_servers)
            except errors.KafkaTimeoutError as e:
                if retry_limit and n_attempt == retry_limit:
                    raise ConnectionError("Could not connect to kafka!")
                time.sleep(reconnect_time_seconds)
                print(e)
                print(f'Trying to reconnect to {bootstrap_servers} in {reconnect_time_seconds} seconds')

    @staticmethod
    def consumer_connect(topic, bootstrap_servers):
        return KafkaConsumer(
            topic,
            api_version=(0, 10),
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    def consume(self):
        for message in self.consumer:
            print(message.value)
            prarams = {"message": message.value}
            requests.get("https://webhook.site/88f80d7e-75fa-4261-9a05-0d22443012c6",
                         params=prarams)
            time.sleep(2)
