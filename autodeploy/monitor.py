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
from database import database, models
from monitor import Monitor
from logger import AppLogger
from monitor import PrometheusModelMetric
from monitor.drift_detection import drift_detection_algorithms

applogger = AppLogger(__name__)
logger = applogger.get_logger()

''' A simple Monitor Driver class. '''


class MonitorDriver(BaseMonitorService):
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
    self.host = 'localhost'
    self.queue = 'monitor'
    self.drift_detection = None
    self.model_metric_port = 8001

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
        input.append(body[k])
    except KeyError as ke:
      logger.error(f'{k} key not found')
      raise KeyError(f'{k} key not found')

    return [input]

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
    status = self.monitor.get_change(input)
    logger.info(
        f'Data Drift Detection {self.drift_detection} detected: {status}')

    # TODO : delete it
    print(
        f'Data Drift Detection {self.drift_detection} detected: {status}')

    # expose prometheus_metric metrics
    status = self.prometheus_metric.convert_str(status)
    self.prometheus_metric.data_drift.info(status)
    self.prometheus_metric.monitor_state.state('up')

  def _load_monitor_algorithm(self) -> Optional[Union[Monitor, None]]:
    reference_data = None
    monitor = None
    drift_name = None
    for k, v in self.config.monitor.metrics.items():
      if v['name'] in drift_detection_algorithms:
        reference_data = v['reference_data']
        drift_name = v['name']
    if reference_data:
      reference_data = np.load(reference_data)
      monitor = Monitor(self.config, drift_name, reference_data)
    self.drift_detection = drift_name
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

    monitor = self._load_monitor_algorithm()
    self.monitor = monitor

    try:
      connection = pika.BlockingConnection(
          pika.ConnectionParameters(host=self.host))
    except Exception as exc:
      logger.critical(
          'Error occured while creating connnection in rabbitmq')
      raise Exception(
          'Error occured while creating connnection in rabbitmq')
    channel = connection.channel()

    channel.queue_declare(queue=self.queue)

    channel.basic_consume(
        queue=self.queue, on_message_callback=self._callback, auto_ack=True)
    self.channel = channel

    self.prometheus_server()

    # expose model deployment name.
    self.prometheus_metric.model_deployment_name.info(
        {'model_name': self.config.model.get('name', 'N/A')})

    # expose model port name.
    self.prometheus_metric.monitor_port.info(
        {'model_monitoring_port': str(self.model_metric_port)})

  def __call__(self) -> None:
    '''
    __call__ for execution `start_consuming` method for consuming messages
    from queue.

    Consumers consume from queues. In order to consume messages there has
    to be a queue. When a new consumer is added, assuming there are already
    messages ready in the queue, deliveries will start immediately.

    '''
    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    self.channel.start_consuming()


''' A simple database class utility. '''


class Database:
  '''
  A database class that creates and stores incoming requests
  in user define database with given schema.
  Args:
    config (Config): A configuration object which contains configuration
    for the deployment.

  Attributes:
    config (Config): internal configuration object for configurations.

  Example:
    >> with Database(config) as db:
    >> .... db.store_request(item)

  '''

  def __init__(self, config) -> None:
    '''


    '''
    self.config = config

  def __enter__(self):
    # create database engine and bind all.
    models.Base.metadata.create_all(bind=database.engine)
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    # TODO: close connecttion to database while exiting.
    pass

  def store_request(self, db, db_item) -> None:

    try:
      db.add(db_item)
      db.commit()
      db.refresh(db_item)
    except Exception as exc:
      logger.error(
          'Some error occured while storing request in database.')
      raise Exception(
          'Some error occured while storing request in database.')
    return db_item

  async def get_db(self) -> None:
    db = database.SessionLocal()
    try:
      yield db
    finally:
      db.close()


if __name__ == '__main__':
  monitordriver = MonitorDriver('../../configs/config.yaml')
  monitordriver.setup()
  monitordriver()
