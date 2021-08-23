""" A simple configuration class. """
from typing import Dict
from os import path
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
    """ Construct nested AttrDicts from nested dictionaries. """
    if not isinstance(data, dict):
      return data
    else:
      return cls({key: cls.from_nested_dicts(data[key]) for key in data})


class Config(AttrDict):
  """ Configuration Class. """

  def __init__(self, config_file):
    super().__init__()
    self.config_file = config_file
    self.config = self._parse_from_yaml()

  def _parse_from_yaml(self) -> Dict:
    """Parses a yaml file and returns a dictionary."""
    config_path = path.join(path.dirname(path.abspath(__file__)), self.config_file)
    with open(config_path, "r") as f:
      config_dict = yaml.load(f, Loader=yaml.FullLoader)
      return config_dict

  def get_config(self):
    return AttrDict.from_nested_dicts(self.config)
