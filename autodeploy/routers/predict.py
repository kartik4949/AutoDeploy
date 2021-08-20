''' a simple prediction router. '''
import traceback
import argparse
import requests
from typing import List
import json
from datetime import datetime

import uvicorn
import pika
import numpy as np
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session

from config.config import Config
from utils import utils
from handlers import Handler, ModelException
from schema import schema
from loader import ModelLoader
from service.builder import InfereBuilder
from logger import AppLogger
from database import database, models

from logger import AppLogger

router = APIRouter()

applogger = AppLogger(__name__)
logger = applogger.get_logger()

''' a simple prediction router class. '''


class PredictRouter:
  def __init__(self, config: Config) -> None:
    # user config for configuring model deployment.
    self.user_config = config

  def setupRabbitMq(self, ):

    # connect to RabbitMQ Server.
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    self.__channel = connection.channel()

    # create a queue named monitor.
    self.__channel.queue_declare(queue='monitor')

  def setup(self, schemas):

    self.input_model_schema = schemas[0]
    self.output_model_schema = schemas[1]
    # create database connection.
    models.Base.metadata.create_all(bind=database.engine)

    # create model loader instance.
    _model_loader = ModelLoader(
        self.user_config.model.model_path, self.user_config.model.model_file_type)
    __model = _model_loader.load()

    # inference model builder.
    self.__inference_executor = InfereBuilder(self.user_config, __model)

    # setupRabbitMq
    self.setupRabbitMq()

  def register_router(self):
    user_config = self.user_config
    input_model_schema = self.input_model_schema
    output_model_schema = self.output_model_schema

    @router.post(f'/{user_config.model.endpoint}', response_model=output_model_schema.UserOutputSchema)
    async def structured_server(payload: input_model_schema.UserInputSchema, db: Session = Depends(utils.get_db)):
      nonlocal self
      try:
        # model inference/prediction.
        model_output = self.__inference_executor.get_inference(payload)
      except:
        logger.error('uncaught exception: %s', traceback.format_exc())
        raise ModelException(name='structured_server')
      else:
        logger.debug('model predict successfull.')

      # store request data and model prediction in database.
      _time_stamp = datetime.now()
      _request_store = {'time_stamp': str(
          _time_stamp), 'prediction': model_output[0], 'is_drift': False}
      _request_store.update(dict(payload))

      request_store = models.Requests(**dict(_request_store))
      utils.store_request(db, request_store)
      self.__channel.basic_publish(exchange='',
                                   routing_key='monitor',
                                   body=json.dumps(dict(_request_store)))

      out_response = {'out': model_output[0],
                      'probablity': model_output[1], 'status': 200}
      return out_response
