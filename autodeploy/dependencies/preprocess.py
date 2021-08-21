import importlib

from config import Config
from register import PREPROCESS


class PreprocessDependency:
  def __init__(self, config):
    self.config = config

    # import to invoke the register
    try:
      importlib.import_module(f'{config.preprocess.path}')
    except ImportError as ie:
      raise ImportError('could not import preprocess from given path.')

  def _get_fxn(self, ):
    fxns = PREPROCESS
    # TODO: check fxn signatures with input schema
    return fxns.module_dict


if __name__ == '__main__':
  pd = PreprocessDependency(
      Config(open('../configs/config.yaml')).get_config())
  pd._get_fxn()
