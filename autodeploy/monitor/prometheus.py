from collections import defaultdict
import os
import operator
import glob
import sys
import importlib
from typing import Dict

from prometheus_client import Counter, Gauge, Summary, Info, Enum

from monitor.drift_detection import drift_detection_algorithms
from register import METRICS
from logger import AppLogger

logger = AppLogger(__name__).get_logger()


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
    self.custom_metric_fxn_name = config.monitor.get('custom_metrics', None)
    self.custom_metrics = None
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

  @staticmethod
  def convert_python_path(file):
    # TODO: check os.
    file = file.split('.')[-2]
    file = file.split('/')[-1]
    return file

  def import_custom_metric_files(self):
    try:

      path = self.config.dependency.path
      sys.path.append(path)
      _py = glob.glob(os.path.join(path, '*.py'))
      for file in _py:
        file = self.convert_python_path(file)
        if 'metric' in file:
          importlib.import_module(file)
    except ImportError as ie:
      logger.error('could not import dependency from given path.')
      raise ImportError('could not import dependency from given path.')

  def get_custom_metrics(self):
    ''' a fxn to get custom metrics dict or list from model dependencies module. '''
    _fxns = METRICS.module_dict
    if self.custom_metric_fxn_name:
      if isinstance(self.custom_metric_fxn_name, list):
        _fxn_dict = {}
        _fxn_metrics = operator.itemgetter(
            *self.custom_metric_fxn_name)(METRICS.module_dict)
        for i, name in enumerate(self.custom_metric_fxn_name):
          _fxn_dict[name] = _fxn_metrics[i]
        return _fxn_dict
      elif isinstance(self.custom_metric_fxn_name, str):
        try:
          return [METRICS.module_dict[self.custom_metric_fxn_name]]
        except KeyError as ke:
          logger.error(
              f'{self.custom_metric_fxn_name} not found in {METRICS.keys()} keys')
          raise KeyError(
              f'{self.custom_metric_fxn_name} not found in {METRICS.keys()} keys')
      else:
        logger.error(
            f'wrong custom metric type {type(self.custom_metric_fxn_name)}, `list` or `str` expected.')
        raise Exception(
            f'wrong custom metric type {type(self.custom_metric_fxn_name)}, `list` or `str` expected.')
    if _fxns:
      return _fxns
    return None

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

    if self.custom_metrics:
      if isinstance(self.custom_metrics, dict):
        for name, metric in self.custom_metrics.items():
          result = metric(input)
          self._metrics[name].set(result)
      elif isinstance(self.custom_metrics, list):
        result = self.custom_metrics[0](input)
        self._metrics[self.custom_metric_fxn_name].set(result)

  def setup_custom_metric(self):
    ''' a simple setup custom metric function to set
    custom functions.
    '''
    custom_metrics = self.get_custom_metrics()
    if isinstance(custom_metrics, dict):
      self.custom_metrics = custom_metrics
      for name, module in custom_metrics.items():
        self._metrics[name] = Gauge(name, 'N/A')
    elif isinstance(custom_metrics, list):
      self._metrics[self.custom_metric_fxn_name] = Gauge(
          self.custom_metric_fxn_name, 'N/A')

  def set_drift_status(self, status):
    self.drift_status = status

  def setup(self):
    '''
    A setup function which binds custom and default prometheus_client
    metrics to PrometheusModelMetric class.

    '''
    self.import_custom_metric_files()
    self.setup_custom_metric()
    self.set_metrics_attributes()
    self.default_model_metric()
