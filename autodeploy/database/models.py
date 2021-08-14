from sqlalchemy import Boolean, Column, Integer, String, Float
from pydantic import BaseModel 
from pydantic.fields import ModelField
from typing import Any, Dict, Optional

from .database import Base
from config import Config

SQLTYPE_MAPPER  = {'float': Float, 'str': String, 'integer': Integer, 'bool': Boolean}
config = Config('../configs/config.yaml').get_config()

def set_dynamic_inputs(cls):
  for k, v in dict(config.input_schema).items():
    setattr(cls, k, Column(SQLTYPE_MAPPER[v]))
  return cls

@set_dynamic_inputs
class Requests(Base):
  __tablename__ = "requests"

  id = Column(Integer,primary_key=True, index=True)
  time_stamp = Column(String)
  prediction = Column(Integer)
  is_drift = Column(Boolean, default=True)

#TODO: create dynamic input attributes
class RequestModel(BaseModel):
  id : int
  time_stamp: str
  prediction: str
  is_drift: bool
  @classmethod
  def add_fields(cls, **field_definitions: Any):
      new_fields: Dict[str, ModelField] = {}
      new_annotations: Dict[str, Optional[type]] = {}

      for f_name, f_def in field_definitions.items():
          if isinstance(f_def, tuple):
              try:
                  f_annotation, f_value = f_def
              except ValueError as e:
                  raise Exception(
                      'field definitions should either be a tuple of (<type>, <default>) or just a '
                      'default value, unfortunately this means tuples as '
                      'default values are not allowed'
                  ) from e
          else:
              f_annotation, f_value = None, f_def

          if f_annotation:
              new_annotations[f_name] = f_annotation

          new_fields[f_name] = ModelField.infer(name=f_name, value=f_value, annotation=f_annotation, class_validators=None, config=cls.__config__)

      cls.__fields__.update(new_fields)
      cls.__annotations__.update(new_annotations)
