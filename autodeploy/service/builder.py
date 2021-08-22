''' Inference Model Builder classes. '''
import random

import numpy as np

from register.register import INFER
from logger import AppLogger

logger = AppLogger(__name__).get_logger()

''' A simple inference model builder. '''


class InfereBuilder:
  '''
  A simple inference builder class which binds inference
  fxn with appropiate class from configuration file.

  Inference builder class builds request AB testing routing
  to route to correct model for inference according to the 
  ab split provided in model configuration.

  Args:
    config (Config): configuration file.
    model (Model): list of models loaded for inference.

  '''

  def __init__(self, config, model_list):
    self.config = config
    self.multi_model = False
    self.num_models = 1
    self._version = self.config.model.get('version', 'n.a')
    if len(model) > 1:
      self.num_models = len(model)
      self.multi_model = True
      logger.info('running multiple models..')

    _infere_class = INFER.get(self.config.model.model_type)
    self._infere_class_instances = []

    for model in model_list:
      self._infere_class_instances.append(_infere_class(config, model))

  def _get_split(self):
    '''
    a helper function to get split weights for choice
    of routing model for inference.

    '''
    if not self.config.model.get('ab_split', None):
      return [1/self.num_models]*self.num_models
    return self.config.model.ab_split

  def _get_model_id_from_split(self):
    '''
    a helper function to get model id to route request.

    '''
    return random.choices(np.arange(self.num_models), weights=self._get_split())[0]

  def get_inference(self, input):
    '''
    a function to get inference from model routed from split.
    '''
    _idx = 0
    if self.multi_model:
      _idx = self._get_model_id_from_split()
    model_infere_detail = {'model': 'primary' if _idx ==
                           0 else 'non_primary', 'id': _idx, 'version': self._version}
    logger.info(model_infere_detail)
    return self._infere_class_instances[_idx].infere(input)
