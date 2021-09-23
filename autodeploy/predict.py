""" A simple prediction service utility."""
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

from config.config import Config
from utils import utils
from logger import AppLogger
from routers import PredictRouter
from routers import prediction_router
from base import BaseDriverService


# __main__ (root) logger instance construction.
applogger = AppLogger(__name__)
logger = applogger.get_logger()


class PredictDriver(BaseDriverService):
    '''
    PredictDriver class for creating prediction driver which 
    takes input tensor and predicts with loaded model.

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

    def setup(self, app) -> None:
        '''
        Main setup function responsible for setting up
        the environment for model deployment.
        setups prediction and model routers.

        Setups Prometheus instrumentor
        '''

        # expose prometheus data to /metrics
        Instrumentator().instrument(app).expose(app)

        apirouter = PredictRouter(self.user_config)
        apirouter.setup()
        apirouter.register_router()

        # setup exception handlers
        self.handler_setup(app)

    def register_routers(self, app):
        '''
        a helper function to register routers in the app.
        '''
        self._app_include([prediction_router], app)

    def run(self, app):
        '''
        The main executing function which runs the uvicorn server
        with the app instance and user configuration.
        '''
        # run uvicorn server.
        uvicorn.run(app, port=8009, host="0.0.0.0")


def main():
    # create fastapi application
    app = FastAPI()
    deploydriver = PredictDriver(os.environ['CONFIG'])
    deploydriver.setup(app)
    deploydriver.register_routers(app)
    deploydriver.run(app)


if __name__ == "__main__":
    main()
