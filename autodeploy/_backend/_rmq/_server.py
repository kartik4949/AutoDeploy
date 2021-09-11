''' a simple rabbitmq server/consumer. '''
import pika

from logger import AppLogger

logger = AppLogger(__name__).get_logger()

class RabbitMQConsume:
  def __init__(self, config) -> None:
    self.host = config.monitor.server.name
    self.port = config.monitor.server.port
    self.queue = 'monitor'

  def setupRabbitMQ(self, callback):
    try:
      connection = pika.BlockingConnection(
          pika.ConnectionParameters(self.host, port=self.port))
    except Exception as exc:
      logger.critical(
          'Error occured while creating connnection in rabbitmq')
      raise Exception(
          'Error occured while creating connnection in rabbitmq', exc)
    channel = connection.channel()

    channel.queue_declare(queue=self.queue)

    channel.basic_consume(
        queue=self.queue, on_message_callback=callback, auto_ack=True)
    self.channel = channel
