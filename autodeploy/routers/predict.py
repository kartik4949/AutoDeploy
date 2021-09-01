''' a simple prediction router. '''
import traceback
import argparse
import requests
from typing import List, Optional, Union, Text, Any
import json
from datetime import datetime

import uvicorn
import validators
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
from dependencies import preprocess, postprocess

from logger import AppLogger
from security.scheme import oauth2_scheme
router = APIRouter()

applogger = AppLogger(__name__)
logger = applogger.get_logger()


class PredictRouter:
  ''' a simple prediction router class
  which routes prediction endpoint to fastapi 
  application.

  Args:
    user_config (Config): a configuration instance.
    preprocess_dependency (preprocess.PreprocessDependency): instance of PreprocessDependency.
    port (int): port number for monitor service
    host (str): hostname.
  Raises:
    BaseException: model prediction exception.


  '''

  def __init__(self, config: Config) -> None:
    # user config for configuring model deployment.
    self.user_config = config

    self.preprocess_dependency = None
    if config.get('preprocess', None):
      self.preprocess_dependency = preprocess.PreprocessDependency(
          config)

    self.postprocess_dependency = None
    if config.get('postprocess', None):
      self.postprocess_dependency = postprocess.PostprocessDependency(
          config)
    self._dependency_fxn = None
    self._post_dependency_fxn = None
    self._protected = config.model.get('protected', False)
    self.host = self.user_config.monitor.server.name
    self.port = self.user_config.monitor.server.port

  def setupRabbitMq(self, ):
    ''' a simple setup for rabbitmq server connection
    and queue connection.
    '''

    # connect to RabbitMQ Server.

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(self.host, port=self.port))
    self.__channel = connection.channel()

    # create a queue named monitor.
    self.__channel.queue_declare(queue='monitor')
    self.__channel.basic_qos(prefetch_count=1)

  def setup(self, schemas):
    ''' setup prediction endpoint method.

    Args:
      schemas (tuple): a user input and output schema tuple.
    '''

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

    # pick one function to register
    # TODO: picks first preprocess function.
    if self.preprocess_dependency:
      self._dependency_fxn = list(
          self.preprocess_dependency._get_fxn().values())[0]

    if self.postprocess_dependency:
      self._post_dependency_fxn = list(
          self.postprocess_dependency._get_fxn().values())[0]

  def get_out_response(self, model_output):
    ''' a helper function to get ouput response. '''
    # TODO: change status code.
    return {'out': model_output[0],
            'probablity': model_output[1], 'status': 200}

  def register_router(self):
    ''' a main router registering funciton
    which registers the prediction service to
    user defined endpoint.
    '''
    user_config = self.user_config
    input_model_schema = self.input_model_schema
    output_model_schema = self.output_model_schema
    preprocess_fxn = self._dependency_fxn
    _protected = self._protected
    postprocess_fxn = self._post_dependency_fxn

    @router.post(f'/{user_config.model.endpoint}',
                 response_model=output_model_schema.UserOutputSchema)
    async def structured_server(payload: input_model_schema.UserInputSchema, db: Session = Depends(utils.get_db), token: Optional[Union[Text, Any]] = Depends(oauth2_scheme) if _protected else None):
      nonlocal self
      try:
        _input_array = []
        _input_type = self.user_config.model.get('input_type', 'na')
        if _input_type == 'structured':
          _input_array = [v for k, v in payload]

        elif _input_type == 'serialized':
          for k, v in payload:
            if isinstance(v, str):
              v = np.asarray(json.loads(v))
            _input_array.append(v)
        elif _input_type == 'url':
          for k, v in payload:
            if validators.url(v):
              _input_array.append(utils.url_loader(v))
            else:
              _input_array.append(v)

        if preprocess_fxn:
          _input_array = preprocess_fxn(_input_array)

        # model inference/prediction.
        model_output, model_detail = self.__inference_executor.get_inference(
            _input_array)

        if postprocess_fxn:
          out_response = postprocess_fxn(model_output)
      except BaseException:
        logger.error('uncaught exception: %s', traceback.format_exc())
        raise ModelException(name='structured_server')
      else:
        logger.debug('model predict successfull.')

      _time_stamp = datetime.now()
      _request_store = {'time_stamp': str(
          _time_stamp), 'prediction': model_output[0], 'is_drift': False}
      _request_store.update(dict(payload))

      self.__channel.basic_publish(exchange='',
                                   routing_key='monitor',
                                   body=json.dumps(dict(_request_store)))
      if not postprocess_fxn:
        out_response = self.get_out_response(model_output)
      return out_response
