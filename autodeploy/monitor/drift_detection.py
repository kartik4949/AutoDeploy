""" Drift detection algorithms. """
import inspect
import sys

import alibi_detect.cd as alibi_drifts


class AverageDriftDetection:
  def __init__(self) -> None:
      pass

  def add_stream(self, x):
    return x

class DriftDetectionAlgorithmsMixin:

  def get_drift(self, name):
    _built_in_drift_detecition = {}
    _built_in_clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for n , a in _built_in_clsmembers:
      _built_in_drift_detecition[n] = a

    if name not in _built_in_drift_detecition.keys():
      return getattr(alibi_drifts, name)
    return _built_in_drift_detecition[name]
