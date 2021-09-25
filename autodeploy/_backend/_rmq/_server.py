''' a simple rabbitmq server/consumer. '''
import pika

from logger import AppLogger
from _backend._heartbeat import HeartBeatMixin

logger = AppLogger(__name__).get_logger()

class RabbitMQConsume(HeartBeatMixin):
    def __init__(self, config) -> None:
      self.host = config.RABBITMQ_HOST
      self.port = config.RABBITMQ_PORT
      self.retries = config.RETRIES
      self.queue = config.RABBITMQ_QUEUE
      self.connection = None

    def setupRabbitMQ(self, callback):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.host, port=self.port))
        except Exception as exc:
            logger.critical(
                'Error occured while creating connnection in rabbitmq')
            raise Exception(
                'Error occured while creating connnection in rabbitmq', exc)
        channel = self.connection.channel()

        channel.queue_declare(queue=self.queue)
        self.beat()

        channel.basic_consume(
            queue=self.queue, on_message_callback=callback, auto_ack=True)
        self.channel = channel
