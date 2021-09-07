''' a simple preprocess dependency class '''
from os import path
import json
import importlib

from config import Config
from register import PREPROCESS


class PreprocessDependency:
  '''
  a preprocess dependency class which creates
  preprocess dependency on predict endpoints.

  Args:
    config (str): configuration file.

  '''

  def __init__(self, config):
    self.config = config

    # import to invoke the register
    try:
      importlib.import_module(f'{config.preprocess.path}')
    except ImportError as ie:
      import sys; print(sys.path)
      raise ImportError(f'could not import preprocess from given path: {config.preprocess.path}')

  def _get_fxn(self, ):
    fxns = PREPROCESS
    # TODO: check fxn signatures with input schema
    return fxns.module_dict
