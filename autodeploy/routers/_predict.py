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
from predict.builder import InfereBuilder
from logger import AppLogger
from database import _database as database, _models as models
from dependencies import LoadDependency
from logger import AppLogger
from security.scheme import oauth2_scheme
from _backend import Database, RabbitMQClient
from _backend import RedisDB
from dependencies import LoadDependency
from config.config import InternalConfig


router = APIRouter()

applogger = AppLogger(__name__)
logger = applogger.get_logger()


class PredictRouter(RabbitMQClient, Database):
  ''' a simple prediction router class
  which routes model prediction endpoint to fastapi
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
    self.internal_config = InternalConfig()
    self.backend_redis = RedisDB(config)
    if config.get('dependency', None):
      self.dependencies = LoadDependency(
          config)
    self._post_dependency_fxn = None

  def setup(self):
    ''' setup api endpoint method.
    '''
    if self.user_config.model.model_type == 'onnx' and not self.user_config.get('postprocess', None):
      logger.error('Postprocess is required in model type `ONNX`.')
      raise Exception('Postprocess is required in model type `ONNX`.')

    # create model loader instance.
    if isinstance(self.user_config.model.model_path, str):
      model_path = os.path.join(self.user_config.dependency.path,
                                self.user_config.model.model_path)
    elif isinstance(self.user_config.model.model_path, list):
      model_path = [os.path.join(self.user_config.dependency.path, _model_path)
                    for _model_path in self.user_config.model.model_path]
    else:
      logger.error('Invalid model path!!')
      raise Exception('Invalid model path!!')

    _model_loader = ModelLoader(
        model_path, self.user_config.model.model_file_type)
    __model = _model_loader.load()
    self.dependencies.import_dependencies()

    self._post_dependency_fxn = self.dependencies.postprocess_fxn

    # inference model builder.
    self.__inference_executor = InfereBuilder(self.user_config, __model)

  def read_input_array(self, id, ndim):
    input = self.backend_redis.pull(
        id, dtype=self.internal_config.PREDICT_INPUT_DTYPE, ndim=int(ndim))
    return input

  def register_router(self):
    ''' a main router registering funciton
    which registers the prediction service to
    user defined endpoint.
    '''
    user_config = self.user_config
    postprocess_fxn = self._post_dependency_fxn

    @router.post('/model_predict')
    async def structured_server(id, ndim):
      nonlocal self
      try:
        _input_array = self.read_input_array(id, ndim)

        # model inference/prediction.
        model_output, _ = self.__inference_executor.get_inference(
            _input_array)

        if postprocess_fxn:
          out_response = postprocess_fxn(model_output)
        else:
          out_response = self.get_out_response(model_output)

      except BaseException:
        logger.error('uncaught exception: %s', traceback.format_exc())
        raise ModelException(name='structured_server')
      else:
        logger.debug('model predict successfull.')
        return out_response
