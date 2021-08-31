""" a simple utilities functions. """
import random
from typing import Text

import requests
import io
from urllib.request import urlopen
from PIL import Image
import numpy as np

from logger import AppLogger
from database import database

# datatypes mapper dictionary.
DATATYPES = {'string': str, 'int': int, 'float': float, 'bool': bool}

logger = AppLogger(__name__).get_logger()


def annotator(_dict):
  __dict = {}
  for key, value in _dict.items():
    if value not in DATATYPES:
      logger.error('input schema datatype is not valid.')
      # TODO: handle exception

    __dict[key] = (DATATYPES[value], ...)
  return __dict


def generate_random_number(type=float):
  if isinstance(type, float):
    # TODO: remove hardcoded values
    return random.uniform(0.0, 10.0)
  return random.randint(0, 10)


def generate_random_from_schema(schema):
  __dict = {}
  for k, v in dict(schema).items():
    if v not in DATATYPES:
      logger.error('input schema datatype is not valid.')
      # TODO: handle exception
    v = DATATYPES[v]
    value = generate_random_number(v)
    __dict[k] = value
  return __dict


def store_request(db, db_item):
  """ a helper function to store
      request in database.
  """
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item


def get_db():
  db = database.SessionLocal()
  try:
    yield db
  finally:
    db.close()

def url_loader(url: Text):
  response = requests.get(url)
  array_bytes = io.BytesIO(response.content)
  array = Image.open(array_bytes)
  return np.asarray(array)
