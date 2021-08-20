''' Base class for deploy driver service. '''
from abc import ABC, abstractmethod


class BaseDriverService(ABC):
  def __init__(self, *args, **kwargs):
    ...

  @abstractmethod
  def setup(self, *args, **kwargs):
    '''
    abstractmethod for setup to be implemeneted in child class
    for setup of monitor driver.

    '''
    raise NotImplementedError('setup function is not implemeneted.')
