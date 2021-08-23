""" a simple model data drift detection monitering utilities. """
from typing import Any, Dict, Text

import numpy as np

from config import Config
from monitor.drift_detection import DriftDetectionAlgorithmsMixin


class Monitor(DriftDetectionAlgorithmsMixin):
  def __init__(self, config: Config, drift_name: Text,
               reference_data: np.ndarray, *args, **kwargs) -> None:
    super(Monitor, self).__init__(*args, *kwargs)
    self.config = config
    _data_drift_instance = self.get_drift(drift_name)
    self._data_drift_instance = _data_drift_instance(reference_data)

  def get_change(self, x: np.ndarray) -> Dict:
    _status = self._data_drift_instance.predict(x)
    return _status
