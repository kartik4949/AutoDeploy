''' A monitoring utility micro service. '''
import json
import os
import sys
from typing import Any, List, Dict, Optional, Union
import functools

import pika
import uvicorn
import numpy as np
from fastapi import FastAPI
from sqlalchemy.orm import Session
from prometheus_client import start_http_server

from base import BaseMonitorService
from config import Config
from monitor import Monitor
from database import _models as models
from logger import AppLogger
from monitor import PrometheusModelMetric
from monitor import drift_detection_algorithms
from _backend import RabbitMQConsume, Database

applogger = AppLogger(__name__)
logger = applogger.get_logger()

''' A simple Monitor Driver class. '''


class MonitorDriver(RabbitMQConsume, BaseMonitorService, Database):
  '''
  A simple Monitor Driver class for creating monitoring model
  and listening to rabbitmq queue i.e Monitor.

  Ref: [https://www.rabbitmq.com/tutorials/tutorial-one-python.html]
  RabbitMQ is a message broker: it accepts and forwards messages.
  You can think about it as a post office: when you put the mail
  that you want posting in a post box, you can be sure that Mr.
  or Ms. Mailperson will eventually deliver the mail to your
  recipient. In this analogy, RabbitMQ is a post box, a post
  office and a postman


  Protocol:
  AMQP - The Advanced Message Queuing Protocol (AMQP) is an open
  standard for passing business messages between applications or
  organizations.  It connects systems, feeds business processes
  with the information they need and reliably transmits onward the
  instructions that achieve their goals.

  Ref: [https://pika.readthedocs.io/en/stable/]
  Pika:
  Pika is a pure-Python implementation of the AMQP 0-9-1 protocol
  that tries to stay fairly independent of the underlying network
  support library.

  Attributes:
    config (Config): configuration file contains configuration.
    host (str): name of host to connect with rabbitmq server.
    queue (str): name of queue to connect to for consuming message.

  '''

  def __init__(self, config) -> None:
    self.config = Config(config).get_config()
    super().__init__(self.config)
    self.queue = 'monitor'
    self.drift_detection = None
    self.model_metric_port = 8001
    self.database = Database(config)

  def _get_array(self, body: Dict) -> List:
    '''

    A simple internal helper function  `_get_array` function
    to convert request body to input for model monitoring.

    Args:
      body (Dict): a body request incoming to monitor service
      from rabbitmq.

    '''
    input_schema = self.config.input_schema
    input = []

    # TODO: do it better
    try:
      for k in input_schema.keys():
        if self.config.model.input_type == 'serialized' and k == 'input':
          input.append(json.loads(body[k]))
        else:
          input.append(body[k])
    except KeyError as ke:
      logger.error(f'{k} key not found')
      raise KeyError(f'{k} key not found')

    return [input]

  def _convert_str_to_blob(self, body):
    _body = {}
    for k, v in body.items():
      if isinstance(v, str):
        _body[k] = bytes(v, 'utf-8')
      else:
        _body[k] = v
    return _body

  def _callback(self, ch: Any, method: Any,
                properties: Any, body: Dict) -> None:
    '''
    a simple callback function attached for post processing on
    incoming message body.

    '''

    try:
      body = json.loads(body)
    except JSONDecodeError as jde:
      logger.error('error while loading json object.')
      raise JSONDecodeError('error while loading json object.')

    input = self._get_array(body)
    input = np.asarray(input)
    output = body['prediction']
    if self.drift_detection:
      drift_status = self.drift_detection.get_change(input)
      self.prometheus_metric.set_drift_status(drift_status)

      # modify data drift status
      body['is_drift'] = drift_status['data']['is_drift']

    # store request data and model prediction in database.
    if self.config.model.input_type == 'serialized':
      body = self._convert_str_to_blob(body)
    request_store = models.Requests(**dict(body))
    self.database.store_request(request_store)
    if self.drift_detection:
      logger.info(
          f'Data Drift Detection {self.config.monitor.data_drift.name} detected: {drift_status}')

    # expose prometheus_metric metrics
    self.prometheus_metric.expose(input, output)

  def _load_monitor_algorithm(self) -> Optional[Union[Monitor, None]]:
    reference_data = None
    monitor = None
    drift_name = self.config.monitor.data_drift.name
    reference_data = os.path.join(
        self.config.dependency.path, self.config.monitor.data_drift.reference_data)
    reference_data = np.load(reference_data)
    monitor = Monitor(self.config, drift_name, reference_data)
    return monitor

  def prometheus_server(self) -> None:
    # Start up the server to expose the metrics.
    start_http_server(self.model_metric_port)

  def setup(self, ) -> None:
    '''
    a simple setup function to setup rabbitmq channel and queue connection
    to start consuming.

    This function setups the loading of model monitoring algorithm from config
    and define safe connection to rabbitmq.

    '''
    self.prometheus_metric = PrometheusModelMetric(self.config)
    self.prometheus_metric.setup()
    if self.config.monitor.get('data_drift', None):
      self.drift_detection = self._load_monitor_algorithm()

    # setup rabbitmq channel and queue.
    self.setupRabbitMQ(self._callback)

    self.prometheus_server()

    # expose model deployment name.
    self.prometheus_metric.model_deployment_name.info(
        {'model_name': self.config.model.get('name', 'N/A')})

    # expose model port name.
    self.prometheus_metric.monitor_port.info(
        {'model_monitoring_port': str(self.model_metric_port)})

    # setup database i.e connect and bind.
    self.database.setup()

  def __call__(self) -> None:
    '''
    __call__ for execution `start_consuming` method for consuming messages
    from queue.

    Consumers consume from queues. In order to consume messages there has
    to be a queue. When a new consumer is added, assuming there are already
    messages ready in the queue, deliveries will start immediately.

    '''
    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    try:
      self.channel.start_consuming()
    except Exception as e:
      raise Exception('uncaught error while consuming message')
    finally:
      self.database.close()


if __name__ == '__main__':
  monitordriver = MonitorDriver(os.environ['CONFIG'])
  monitordriver.setup()
  monitordriver()
