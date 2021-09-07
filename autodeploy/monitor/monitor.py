""" a simple model data drift detection monitering utilities. """
from typing import Any, Dict, Text

import numpy as np

from config import Config
from monitor.drift_detection import DriftDetectionAlgorithmsMixin


class Monitor(DriftDetectionAlgorithmsMixin):
  '''
  a simple `Monitor` class to drive and setup monitoring
  algorithms for monitor of inputs to the model

  Args:
    config (Config): a configuration instance. 

  '''

  def __init__(self, config: Config, drift_name: Text,
               reference_data: np.ndarray, *args, **kwargs) -> None:
    super(Monitor, self).__init__(*args, *kwargs)
    self.config = config
    _data_drift_instance = self.get_drift(drift_name)
    self._data_drift_instance = _data_drift_instance(reference_data)

  def get_change(self, x: np.ndarray) -> Dict:
    '''
    a helper funciton to get data drift.

    '''
    _status = self._data_drift_instance.predict(x)
    return _status
