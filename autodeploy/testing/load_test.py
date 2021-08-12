""" a simple locust file for load testing. """
import os

import numpy as np
from locust import HttpUser, task

from config.config import Config 
from utils import utils

user_config = Config(os.environ['CONFIG']).get_config()

class LoadTesting(HttpUser):
    """ LoadTesting Class for load testing. """

    @task
    def load_test_request(self):
      global user_config
      """ a simple request load test task. """
      input = utils.generate_random_from_schema(user_config.input_schema) 
      self.client.post(f"/{user_config.model.endpoint}", json = input)
