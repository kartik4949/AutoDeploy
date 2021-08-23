from collections import defaultdict

from prometheus_client import Counter, Gauge, Summary, Info

from monitor.drift_detection import drift_detection_algorithms


_metric_types = {'gauge': Gauge, 'summary': Summary,
                 'counter': Counter, 'info': Info}


class PrometheusModelMetric:
  def __init__(self, config, metrics_meta) -> None:
    self.config = config
    self._metrics = defaultdict()
    self.data_drift = None
    for k, v in metrics_meta.items():
      self._metrics.update(
          {v['name']: _metric_types[v['type']](v['name'], 'N/A')})

  def set_metrics_attributes(self):
    for k, v in self._metrics.items():
      if k in drift_detection_algorithms:
        self.data_drift = v
        continue
      setattr(self, k, v)

  def convert_str(self, status):
    _dict = {}
    for k, v in status.items():
      _dict.update({k: str(v)})
    return _dict
