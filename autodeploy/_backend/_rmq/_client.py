''' a rabbitmq client class. '''
import json
import asyncio
from contextlib import suppress
import uuid
from typing import Dict

import pika

from _backend._heartbeat import HeartBeatMixin
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


class RabbitMQClient(HeartBeatMixin):
  def __init__(self, config):
    self.host = config.monitor.server.name
    self.port = config.monitor.server.port

    self.retries = 2

  def connect(self):
    ''' a simple function to get connection to rmq '''
    # connect to RabbitMQ Server.
    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=self.host, port=self.port))

    self.channel = self.connection.channel()

    result = self.channel.queue_declare(queue='monitor', exclusive=False)
    self.callback_queue = result.method.queue
    self.channel.basic_qos(prefetch_count=1)

  def setupRabbitMq(self, ):
    ''' a simple setup for rabbitmq server connection
    and queue connection.
    '''
    self.connect()
    self.beat()

  def _publish(self, body: Dict):
    self.channel.basic_publish(
        exchange='',
        routing_key='monitor',
        properties=pika.BasicProperties(
            reply_to=self.callback_queue,
        ),
        body=json.dumps(dict(body)))

  def publish_rbmq(self, body: Dict):
    try:
      self._publish(body)
    except:
      logger.error('Error while publish!!, restarting connection.')
      for i in range(self.retries):
        try:
          self._publish(body)
        except:
          continue
        else:
          logger.debug('published success after {i + 1} retries')
          return
          break

      logger.critical('cannot publish after retries!!')
