''' a simple dependency class '''
import os
import json
import sys
import glob
import importlib

from config import Config
from register import PREPROCESS, POSTPROCESS, METRICS
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


class LoadDependency:
    '''
    a dependency class which creates
    dependency on predict endpoints.

    Args:
      config (str): configuration file.

    '''

    def __init__(self, config):
        self.config = config
        self.preprocess_fxn_name = config.get('preprocess', None)
        self.postprocess_fxn_name = config.get('postprocess', None)

    @staticmethod
    def convert_python_path(file):
        # TODO: check os.
        file = file.split('.')[-2]
        file = file.split('/')[-1]
        return file

    @property
    def postprocess_fxn(self):
        _fxns = list(POSTPROCESS.module_dict.values())
        if self.postprocess_fxn_name:
            try:
                return POSTPROCESS.module_dict[self.postprocess_fxn_name]
            except KeyError as ke:
                raise KeyError(
                    f'{self.postprocess_fxn_name} not found in {POSTPROCESS.keys()} keys')
        if _fxns:
            return _fxns[0]
        return None

    @property
    def preprocess_fxn(self):
        _fxns = list(PREPROCESS.module_dict.values())
        if self.preprocess_fxn_name:
            try:
                return PREPROCESS.module_dict[self.preprocess_fxn_name]
            except KeyError as ke:
                raise KeyError(
                    f'{self.preprocess_fxn_name} not found in {PREPROCESS.keys()} keys')
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
            logger.error('could not import dependency from given path.')
            raise ImportError('could not import dependency from given path.')
