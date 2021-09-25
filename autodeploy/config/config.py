""" A simple configuration class. """
from typing import Dict
from os import path
import copy
import yaml


class AttrDict(dict):
  """ Dictionary subclass whose entries can be accessed by attributes (as well
      as normally).
  """

  def __init__(self, *args, **kwargs):
    super(AttrDict, self).__init__(*args, **kwargs)
    self.__dict__ = self

  @classmethod
  def from_nested_dicts(cls, data):
    """ Construct nested AttrDicts from nested dictionaries.
    Args:
      data (dict): a dictionary data.
    """
    if not isinstance(data, dict):
      return data
    else:
      try:
        return cls({key: cls.from_nested_dicts(data[key]) for key in data})
      except KeyError as ke:
        raise KeyError('key not found in data while loading config.')


class Config(AttrDict):
  """ A Configuration Class.
  Args:
    config_file (str): a configuration file.
  """

  def __init__(self, config_file):
    super().__init__()
    self.config_file = config_file
    self.config = self._parse_from_yaml()

  def as_dict(self):
    """Returns a dict representation."""
    config_dict = {}
    for k, v in self.__dict__.items():
      if isinstance(v, Config):
        config_dict[k] = v.as_dict()
      else:
        config_dict[k] = copy.deepcopy(v)
    return config_dict

  def __repr__(self):
    return repr(self.as_dict())

  def __str__(self):
    print("Configurations:\n")
    try:
      return yaml.dump(self.as_dict(), indent=4)
    except TypeError:
      return str(self.as_dict())

  def _parse_from_yaml(self) -> Dict:
    """Parses a yaml file and returns a dictionary."""
    config_path = path.join(path.dirname(path.abspath(__file__)), self.config_file)
    try:
      with open(config_path, "r") as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
        return config_dict
    except FileNotFoundError as fnfe:
      raise FileNotFoundError('configuration file not found.')
    except Exception as exc:
      raise Exception('Error while loading config file.')

  def get_config(self):
    return AttrDict.from_nested_dicts(self.config)

class InternalConfig():
  """ An Internal Configuration Class. 
  """

  # model backend redis
  REDIS_SERVER = 'redis'
  REDIS_PORT = 6379

  # api endpoint
  API_PORT = 8000
  API_NAME = 'AutoDeploy'

  # Monitor endpoint
  MONITOR_PORT = 8001

  # Rabbitmq

  RETRIES = 3
  RABBITMQ_PORT = 5672
  RABBITMQ_HOST = 'rabbitmq'
  RABBITMQ_QUEUE = 'monitor'


  # model prediction service
  PREDICT_PORT = 8009
  PREDICT_ENDPOINT = 'model_predict'
  PREDICT_URL = 'prediction'
  PREDICT_INPUT_DTYPE = 'float32'
