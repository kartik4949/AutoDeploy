import json
import asyncio
from contextlib import suppress
from time import sleep
import threading
import uuid
from typing import Dict

import pika

class RabbitMQClient:
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

  @staticmethod
  def _beat(connection):
    while True:
      # TODO: remove hardcode
      sleep(5)
      connection.process_data_events()

  def beat(self):
    ''' process_data_events preodically. 
    TODO: hackish way, think other way.
    '''
    heartbeat = threading.Thread(target=self._beat, args=(self.connection,), daemon=True)
    heartbeat.start()

  def publish_rbmq(self, body: Dict):
    self.channel.basic_publish(
        exchange='',
        routing_key='monitor',
        properties=pika.BasicProperties(
            reply_to=self.callback_queue,
        ),
        body=json.dumps(dict(body)))
