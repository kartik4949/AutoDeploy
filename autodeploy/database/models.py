''' a simple pydantic and sqlalchemy models utilities. '''
from os import path

from sqlalchemy import Boolean, Column, Integer, String, Float
from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic import create_model

from typing import Any, Dict, Optional

from .database import Base
from utils import utils
from config import Config

SQLTYPE_MAPPER = {
    'float': Float,
    'string': String,
    'int': Integer,
    'bool': Boolean}
config_path = path.join(path.dirname(path.abspath(__file__)),
                        '../../configs/config.yaml')

config = Config(config_path).get_config()


def set_dynamic_inputs(cls):
  ''' a decorator to set dynamic model attributes. '''
  for k, v in dict(config.input_schema).items():
    setattr(cls, k, Column(SQLTYPE_MAPPER[v]))
  return cls


@set_dynamic_inputs
class Requests(Base):
  '''
  Requests class pydantic model with input_schema.
  '''
  __tablename__ = "requests"

  id = Column(Integer, primary_key=True, index=True)
  time_stamp = Column(String)
  prediction = Column(Integer)
  is_drift = Column(Boolean, default=True)


# TODO: create dynamic input attributes
class RequestMonitor:
  def __init__(self, config):
    _default_attr = {
        'time_stamp': (
            str, ...), 'prediction': (
            int, ...), 'is_drift': (
            bool, ...)}
    self._model_attr = utils.annotator(dict(config.input_schema))
    self._model_attr.update(_default_attr)
    self.ModelMonitorSchema = create_model(
        'ModelMonitorSchema', **self._model_attr)
