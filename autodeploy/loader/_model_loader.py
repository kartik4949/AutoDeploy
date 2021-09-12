''' A simple Model Loader Class. '''
from loader._loaders import *
from logger import AppLogger

ALLOWED_MODEL_TYPES = ['pickle', 'hdf5', 'joblib', 'onnx']

logger = AppLogger(__name__).get_logger()


class ModelLoader:
  ''' a driver class ModelLoader to setup and load
  model file based on file type.
  Args:
    model_path (str): model file path.
    model_type (str): model file type.
  '''

  def __init__(self, model_path, model_type):
    self.model_path = model_path
    self.multi_model = False
    if isinstance(self.model_path, list):
      self.multi_model = True
    self.model_type = model_type

  def load(self):
    ''' a loading function which loads model file
    based on file type. '''
    logger.info('model loading started')
    if self.model_type in ALLOWED_MODEL_TYPES:
      if self.model_type == 'pickle':
        loader = PickleLoader(
            self.model_path, multi_model=self.multi_model)
        return loader.load()

      elif self.model_type == 'onnx':
        loader = OnnxLoader(
            self.model_path, multi_model=self.multi_model)
        return loader.load()

    else:
      logger.error('model type is not allowed')
      raise ValueError('Model type is not supported yet!!!')
    logger.info('model loaded successfully!')
