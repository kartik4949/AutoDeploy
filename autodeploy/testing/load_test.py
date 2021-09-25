""" a simple locust file for load testing. """
import os
import json

import numpy as np
from locust import HttpUser, task

from config.config import Config
from utils import utils

user_config = Config(os.environ['CONFIG']).get_config()


class LoadTesting(HttpUser):
    """ LoadTesting class for load testing. """

    @task
    def load_test_request(self):
        global user_config
        """ a simple request load test task. """
        if user_config.model.input_type == 'serialized':
            input = utils.generate_random_from_schema(
                user_config.input_schema, shape=user_config.model.input_shape, serialized=True)
        elif user_config.mode.input_type == 'structured':
            input = utils.generate_random_from_schema(user_config.input_schema)
        self.client.post(f"/{user_config.model.endpoint}", json=input)
