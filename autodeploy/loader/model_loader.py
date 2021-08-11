''' A simple Model Loader Class. '''
from loader.loaders import *
from logger import AppLogger

ALLOWED_MODEL_TYPES = ['pickle', 'hdf5', 'joblib']

class ModelLoader:
  def __init__(self, model_path, model_type):
    self.model_path = model_path
    self.model_type = model_type
    self.logger = AppLogger(__name__).get_logger()

  def load(self):
    self.logger.info('model loading started')
    if self.model_type in ALLOWED_MODEL_TYPES:
      if self.model_type == 'pickle':
        loader = PickleLoader(self.model_path)
        return loader.load()

    else:
      self.logger.debug('model type is not allowed')
      raise ValueError('Model type is not supported yet!!!')
    self.logger.debug('model loaded successfully!')
