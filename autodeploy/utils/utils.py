""" a simple utilities functions. """
#from logging import logger
DATATYPES = {'string': str, 'int': int, 'float': float, 'bool': bool}


def annotator(_dict):
  __dict = {}
  for key, value in _dict.items():
    if value not in DATATYPES:
      #logger.error('Datatype is not valid.')
      pass
    __dict[key] = (DATATYPES[value], ...)
  return __dict

