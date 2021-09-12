''' a simple prediction router. '''
import traceback
import argparse
import os
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
from loader import ModelLoader
from service.builder import InfereBuilder
from logger import AppLogger
from database import _database as database, _models as models
from dependencies import LoadDependency
from logger import AppLogger
from security.scheme import oauth2_scheme
from _backend import Database, RabbitMQClient


router = APIRouter()

applogger = AppLogger(__name__)
logger = applogger.get_logger()


class PredictRouter(RabbitMQClient, Database):
  ''' a simple prediction router class
  which routes prediction endpoint to fastapi 
  application.

  Args:
    user_config (Config): a configuration instance.
    dependencies (LoadDependency): instance of LoadDependency.
    port (int): port number for monitor service
    host (str): hostname.
  Raises:
    BaseException: model prediction exception.


  '''

  def __init__(self, config: Config) -> None:
    super(PredictRouter, self).__init__(config)
    # user config for configuring model deployment.
    self.user_config = config
    self.dependencies = None
    if config.get('dependency', None):
      self.dependencies = LoadDependency(
          config)

    self._dependency_fxn = None
    self._post_dependency_fxn = None
    self._protected = config.model.get('protected', False)

  def setup(self, schemas):
    ''' setup prediction endpoint method.

    Args:
      schemas (tuple): a user input and output schema tuple.
    '''

    self.input_model_schema = schemas[0]
    self.output_model_schema = schemas[1]
    # create database connection.
    self.bind()

    # create model loader instance.
    model_path = os.path.join(self.user_config.dependency.path,
                              self.user_config.model.model_path)
    _model_loader = ModelLoader(
        model_path, self.user_config.model.model_file_type)
    __model = _model_loader.load()

    # inference model builder.
    self.__inference_executor = InfereBuilder(self.user_config, __model)

    # setupRabbitMq
    self.setupRabbitMq()

    self.dependencies.import_dependencies()

    # pick one function to register
    # TODO: picks first preprocess function.
    self._dependency_fxn = self.dependencies.preprocess_fxn

    self._post_dependency_fxn = self.dependencies.postprocess_fxn

  def get_out_response(self, model_output):
    ''' a helper function to get ouput response. '''
    # TODO: change status code.
    return {'out': model_output[1],
            'probablity': model_output[0], 'status': 200}

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
    # TODO remove db
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

        cache = None
        if preprocess_fxn:
          _input_array = preprocess_fxn(_input_array)

          if isinstance(_input_array, tuple):
            _input_array = _input_array, cache

        # model inference/prediction.
        model_output, model_detail = self.__inference_executor.get_inference(
            _input_array)

        if postprocess_fxn:
          if cache:
            out_response = postprocess_fxn(model_output, cache)
          else:
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
      self.publish_rbmq(_request_store)

      if not postprocess_fxn:
        out_response = self.get_out_response(model_output)
      return out_response
