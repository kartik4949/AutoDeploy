from collections import defaultdict
from typing import Dict

from prometheus_client import Counter, Gauge, Summary, Info, Enum

from monitor.drift_detection import drift_detection_algorithms


_metric_types = {'gauge': Gauge, 'summary': Summary,
                 'counter': Counter, 'info': Info}


class PrometheusModelMetric:
  '''
  a `PrometheusModelMetric` class to setup and define
  prometheus_client metrics default and custom metrics
  from config file.

  Args:
    config (Config): a configuration instance.
    data_drift (Any): a data drift detection fxn.

  '''

  def __init__(self, config) -> None:
    self.config = config
    metrics_meta = dict(self.config.monitor.metrics)
    self._metrics = defaultdict()
    self.data_drift = None
    for k, v in metrics_meta.items():
      self._metrics.update(
          {v['name']: _metric_types[v['type']](v['name'], 'N/A')})

  def default_model_metric(self):
    '''
    a default_model_metric method which contains default
    model prometheus_client metrics.

    monitor_state: monitoring service state.
    monitor_port: stores monitor port number.
    model_deployment_name: stores model name.

    '''
    self.monitor_state = Enum(
        'monitor_service_state', 'Monitoring service state i.e up or down', states=['up', 'down'])
    self.monitor_port = Info('monitor_port', 'monitor service port number')
    self.model_deployment_name = Info(
        'model_deployment_name', 'Name for model deployment.')

  def set_metrics_attributes(self):
    '''
    a helper function to set custom metrics from
    config file in prometheus_client format.

    '''
    for k, v in self._metrics.items():
      if k in drift_detection_algorithms:
        self.data_drift = v
        continue
      setattr(self, k, v)

  def convert_str(self, status: Dict):
    ''' a helper function to convert dict to str '''
    _dict = {}
    for k, v in status.items():
      _dict.update({k: str(v)})
    return _dict

  def setup(self):
    '''
    A setup function which binds custom and default prometheus_client
    metrics to PrometheusModelMetric class.

    '''
    self.set_metrics_attributes()
    self.default_model_metric()
