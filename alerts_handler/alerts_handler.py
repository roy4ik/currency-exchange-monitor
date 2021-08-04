from mngrs.mq_manager import MessageConsumer


class AlertsHandler:
    message_consumer = MessageConsumer()
    topic = 'exchange_rate_increase'

    def run(self):
        if self.message_consumer.consumer:
            self.message_consumer.consume()
        else:
            self.message_consumer.set_consumer(self.topic, retry_limit=0)


alerts_handler = AlertsHandler()
alerts_handler.run()
