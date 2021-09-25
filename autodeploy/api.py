""" A simple deploy service utility."""
import traceback
import argparse
import requests
import os
import json
from typing import List, Dict, Tuple, Any
from datetime import datetime

import uvicorn
import numpy as np
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Depends, FastAPI, Request, HTTPException

from config.config import Config, InternalConfig
from utils import utils
from logger import AppLogger
from routers import AutoDeployRouter
from routers import api_router
from routers import ModelDetailRouter
from routers import model_detail_router
from routers import auth_router
from base import BaseDriverService


# ArgumentParser to get commandline args.
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--mode", default='debug', type=str,
                    help="model for running deployment ,mode can be PRODUCTION or DEBUG")
args = parser.parse_args()

# __main__ (root) logger instance construction.
applogger = AppLogger(__name__)
logger = applogger.get_logger()


def set_middleware(app):
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


class APIDriver(BaseDriverService):
  '''
  APIDriver class for creating deploy driver which setups
  , registers routers with `app` and executes the server.

  This class is the main driver class responsible for creating
  and setupping the environment.
  Args:
    config (str): a config path.

  Note:
    `setup` method should get called before `register_routers`.

  '''

  def __init__(self, config_path) -> None:
    # user config for configuring model deployment.
    self.user_config = Config(config_path).get_config()
    self.internal_config = InternalConfig()

  def setup(self, app) -> None:
    '''
    Main setup function responsible for setting up
    the environment for model deployment.
    setups prediction and model routers.

    Setups Prometheus instrumentor
    '''
    # print config

    logger.info(self.user_config)
    if isinstance(self.user_config.model.model_path, list):
      logger.info('multi model deployment started...')

    # expose prometheus data to /metrics
    Instrumentator().instrument(app).expose(app)
    _schemas = self._setup_schema()

    apirouter = AutoDeployRouter(self.user_config, self.internal_config)
    apirouter.setup(_schemas)
    apirouter.register_router()

    modeldetailrouter = ModelDetailRouter(self.user_config)
    modeldetailrouter.register_router()
    set_middleware(app)

    # setup exception handlers
    self.handler_setup(app)

  def register_routers(self, app):
    '''
    a helper function to register routers in the app.
    '''
    self._app_include([api_router, model_detail_router, auth_router], app)

  def run(self, app):
    '''
    The main executing function which runs the uvicorn server
    with the app instance and user configuration.
    '''
    # run uvicorn server.
    uvicorn.run(app, port=self.user_config.model.server.port, host="0.0.0.0")


def main():
  # create fastapi application
  app = FastAPI()
  deploydriver = APIDriver(os.environ['CONFIG'])
  deploydriver.setup(app)
  deploydriver.register_routers(app)
  deploydriver.run(app)


if __name__ == "__main__":
  main()
