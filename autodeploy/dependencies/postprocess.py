''' a simple postprocess dependency class '''
from os import path
import json
import importlib

from config import Config
from register import POSTPROCESS


class PostprocessDependency:
  '''
  a postprocess dependency class which creates
  postprocess dependency on predict endpoints.

  Args:
    config (str): configuration file.

  '''

  def __init__(self, config):
    self.config = config

    # import to invoke the register
    try:
      importlib.import_module(f'{config.postprocess.path}')
    except ImportError as ie:
      raise ImportError('could not import postprocess from given path.')

  def _get_fxn(self, ):
    fxns = POSTPROCESS
    # TODO: check fxn signatures with input schema
    return fxns.module_dict
