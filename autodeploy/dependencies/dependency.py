''' a simple dependency class '''
import os
import json
import sys
import glob
import importlib

from config import Config
from register import PREPROCESS, POSTPROCESS, METRICS


class LoadDependency:
  '''
  a dependency class which creates
  dependency on predict endpoints.

  Args:
    config (str): configuration file.

  '''

  def __init__(self, config):
    self.config = config

  @staticmethod
  def convert_python_path(file):
    # TODO: check os.
    file = file.split('.')[-2]
    file = file.split('/')[-1]
    return file

  @property
  def postprocess_fxn(self):
    _fxns = list(POSTPROCESS.module_dict.values())
    if _fxns:
      return _fxns[0]
    return None

  @property
  def preprocess_fxn(self):
    _fxns = list(PREPROCESS.module_dict.values())
    if _fxns:
      return _fxns[0]
    return None

  @property
  def custom_metric_fxn(self):
    _fxns = list(METRICS.module_dict.values())
    if _fxns:
      return _fxns[0]
    return None

  def import_dependencies(self):
    # import to invoke the register
    try:
      path = self.config.dependency.path
      sys.path.append(path)
      _py_files = glob.glob(os.path.join(path, '*.py'))

      for file in _py_files:
        file = self.convert_python_path(file)
        importlib.import_module(file)
    except ImportError as ie:
      raise ImportError('could not import dependency from given path.')
