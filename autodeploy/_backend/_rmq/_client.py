import json
import asyncio
from contextlib import suppress
import uuid
from typing import Dict

import pika

from _backend._heartbeat import HeartBeatMixin

class RabbitMQClient(HeartBeatMixin):
  def __init__(self, config):
    self.host = config.monitor.server.name
    self.port = config.monitor.server.port

  def setupRabbitMq(self, ):
    ''' a simple setup for rabbitmq server connection
    and queue connection.
    '''

    # connect to RabbitMQ Server.
    self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=self.host, port=self.port))

    self.channel = self.connection.channel()

    result = self.channel.queue_declare(queue='monitor', exclusive=False)
    self.callback_queue = result.method.queue
    self.channel.basic_qos(prefetch_count=1)
    self.beat()

  def publish_rbmq(self, body: Dict):
    self.channel.basic_publish(
        exchange='',
        routing_key='monitor',
        properties=pika.BasicProperties(
            reply_to=self.callback_queue,
        ),
        body=json.dumps(dict(body)))
