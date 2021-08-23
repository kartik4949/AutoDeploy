""" A simple deploy service utility."""
import traceback
import argparse
import requests
from typing import List, Dict, Tuple, Any
import json
from datetime import datetime

import uvicorn
import pika
import numpy as np
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Depends, FastAPI, Request, HTTPException
from sqlalchemy.orm import Session

from config.config import Config
from utils import utils
from handlers import Handler, ModelException
from schema import schema
from logger import AppLogger
from routers.predict import PredictRouter
from routers.predict import router as prediction_router
from routers.model import ModelDetailRouter
from routers.model import router as model_detial_router
from routers.security import router as auth_router
from base import BaseDriverService


# ArgumentParser to get commandline args.
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--mode", default='debug', type=str,
                    help="model for running deployment ,mode can be PRODUCTION or DEBUG")
parser.add_argument("-c", "--config", default='../../configs/config.yaml', type=str,
                    help="a configuration yaml file path.")
args = parser.parse_args()

# __main__ (root) logger instance construction.
applogger = AppLogger(__name__)
logger = applogger.get_logger()

# create fastapi application
app = FastAPI()


@app.middleware('http')
async def log_incoming_requests(request: Request, call_next):
  '''
  Middleware to log incoming requests to server.

  Args:
    request (Request): incoming request payload.
    call_next: function to executing the request.
  Returns:
    response (Dict): reponse from the executing fxn.
  '''
  logger.info(f'incoming payload to server. {request}')
  response = await call_next(request)
  return response


class DeployDriver(BaseDriverService):
  '''
  DeployDriver class for creating deploy driver which setups
  , registers routers with `app` and executes the server.

  This class is the main driver class responsible for creating
  and setupping the environment.
  Args:
    config (str): a config path.

  Note:
    `setup` method should get called before `register_routers`.

  '''

  def __init__(self, config) -> None:
    # user config for configuring model deployment.
    self.user_config = Config(args.config).get_config()

  @staticmethod
  def _handler_setup():
    '''
    a simple helper function to overide handlers
    '''
    # create exception handlers for fastapi.
    handler = Handler()
    handler.overide_handlers(app)
    handler.create_handlers(app)

  def _app_include(self, routers):
    '''
    a simple helper function to register routers
    with the fastapi `app`.

    '''
    for route in routers:
      app.include_router(route)

  def _setup_schema(self) -> Tuple[Any, Any]:
    '''
    a function to setup input and output schema for
    server.

    '''
    # create input and output schema for model endpoint api.
    input_model_schema = schema.UserIn(
        self.user_config)
    output_model_schema = schema.UserOut(
        self.user_config)
    return (input_model_schema, output_model_schema)

  def setup(self) -> None:
    '''
    Main setup function responsible for setting up
    the environment for model deployment.
    setups prediction and model routers.

    Setups Prometheus instrumentor
    '''
    if isinstance(self.user_config.model.model_path, list):
      logger.info('multi model deployment started...')

    # expose prometheus data to /metrics
    Instrumentator().instrument(app).expose(app)
    _schemas = self._setup_schema()

    predictrouter = PredictRouter(self.user_config)
    predictrouter.setup(_schemas)
    predictrouter.register_router()

    modeldetailrouter = ModelDetailRouter(self.user_config)
    modeldetailrouter.register_router()

  def register_routers(self):
    '''
    a helper function to register routers in the app.
    '''
    self._app_include([prediction_router, model_detial_router, auth_router])

  def run(self):
    '''
    The main executing function which runs the uvicorn server
    with the app instance and user configuration.
    '''
    # run uvicorn server.
    global app
    uvicorn.run(app, port=self.user_config.server.port)


def main():
  deploydriver = DeployDriver(args.config)
  deploydriver.setup()
  deploydriver.register_routers()
  deploydriver.run()


if __name__ == "__main__":
  main()