from collections import defaultdict
import importlib
from typing import Dict

from prometheus_client import Counter, Gauge, Summary, Info, Enum

from monitor.drift_detection import drift_detection_algorithms
from register import METRICS


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
    self._metrics = defaultdict()

    self.data_drift = None
    data_drift_meta = self.config.monitor.get('data_drift', None)
    if data_drift_meta:
      self.data_drift = Info(data_drift_meta.name, 'N/A')
    self.drift_status = None

    self.metric_list = []

    metrics_meta = self.config.monitor.metrics
    if metrics_meta:
      for k, v in metrics_meta.items():
        self._metrics.update(
            {k: _metric_types[v['type']](k, 'N/A')})

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
    self.model_output_score = Gauge(
        'model_output_score', 'This is gauge to output model score.')
    self.data_drift_out = Gauge(
        'data_drift_out', 'This is data drift output i.e binary.')

  def set_metrics_attributes(self):
    '''
    a helper function to set custom metrics from
    config file in prometheus_client format.

    '''
    for k, v in self._metrics.items():
      setattr(self, k, v)

  def convert_str(self, status: Dict):
    ''' a helper function to convert dict to str '''
    _dict = {}
    for k, v in status.items():
      _dict.update({k: str(v)})
    return _dict

  def expose(self, input, output):
    ''' Expose method to expose metrics to prometheus server. '''
    if self.drift_status:
      status = self.convert_str(self.drift_status)
      self.data_drift.info(status)
      self.data_drift_out.set(self.drift_status['data']['is_drift'])

    self.monitor_state.state('up')
    self.model_output_score.set(output)
    for metric in self.metric_list:
      result = metric(input)
      self._metrics[metric.__name__].set(result)

  def setup_custom_metric(self):
    ''' a simple setup custom metric function to set 
    custom functions.
    '''
    for name, module in METRICS.module_dict.items():
      if module.__name__ not in self._metrics.keys():
        self._metrics[module.__name__] = Gauge(module.__name__, 'N/A')
      self.metric_list.append(module)

  def set_drift_status(self, status):
    self.drift_status = status

  def setup(self):
    '''
    A setup function which binds custom and default prometheus_client
    metrics to PrometheusModelMetric class.

    '''
    if self.config.monitor.get('custom_metric', None):
      self.setup_custom_metric()
    self.set_metrics_attributes()
    self.default_model_metric()
