''' Base class for monitor driver service. '''
from abc import ABC, abstractmethod

class BaseMonitorService(ABC):
  def __init__(self, *args, **kwargs):
    ...
  
  @abstractmethod
  def setup(self, *args, **kwargs):
    '''
    abstractmethod for setup to be implemeneted in child class
    for setup of monitor driver.

    '''
    raise NotImplementedError('setup function is not implemeneted.')

  @abstractmethod
  def _load_monitor_algorithm(self, *args, **kwargs):
    '''
    abstractmethod for loading monitor algorithm which needs
    to be overriden in child class.
    '''

    raise NotImplementedError('load monitor function is not implemeneted.')
