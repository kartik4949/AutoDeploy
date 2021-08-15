''' Base class for inference service. '''
from abc import ABC, abstractmethod

class BaseInfere(ABC):
  def __init__(self, *args, **kwargs):
    ...
  
  @abstractmethod
  def infere(self, *args, **kwargs):
    '''
    infere function which inferes the input 
    data based on the model loaded.
    Needs to be overriden in child class with 
    custom implementation.

    '''
    raise NotImplementedError('Infere function is not implemeneted.')
