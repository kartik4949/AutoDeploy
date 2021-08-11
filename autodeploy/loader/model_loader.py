''' A simple Model Loader Class. '''
from loader.loaders import *

ALLOWED_MODEL_TYPES = ['pickle', 'hdf5', 'joblib']

class ModelLoader:
  def __init__(self, model_path, model_type):
    self.model_path = model_path
    self.model_type = model_type

  def load(self):
    if self.model_type in ALLOWED_MODEL_TYPES:
      if self.model_type == 'pickle':
        loader = PickleLoader(self.model_path)
        return loader.load()

    else:
      raise ValueError('Model type is not supported yet!!!')
