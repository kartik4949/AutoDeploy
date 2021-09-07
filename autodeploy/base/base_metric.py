""" a simple model data drift detection monitering utilities. """
from abc import ABC, abstractmethod
from typing import Dict

import numpy as np

from config import Config


class BaseMetric(ABC):

  def __init__(self, config: Config, *args, **kwargs) -> None:
    self.config = config

  @abstractmethod
  def get_change(self, x: np.ndarray) -> Dict:
    '''

    '''
    raise NotImplementedError('setup function is not implemeneted.')
