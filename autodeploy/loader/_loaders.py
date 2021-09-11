''' A loader class utilities. '''
from os import path

from logger import AppLogger
from base import BaseLoader

logger = AppLogger(__name__).get_logger()


class PickleLoader(BaseLoader):
  ''' a simple PickleLoader class.
  class which loads pickle model file.
  Args:
    model_path (str): model file path.
    multi_model (bool): multi model flag.
  '''

  def __init__(self, model_path, multi_model=False):
    self.model_path = model_path
    self.multi_model = multi_model

  def load(self):
    ''' a helper function to load model_path file. '''
    import pickle
    # TODO: do handling
    try:
      if not self.multi_model:
        self.model_path = [self.model_path]
      models = []
      for model in self.model_path:
        model_path = path.join(path.dirname(path.abspath(__file__)), model)
        with open(model_path, 'rb') as reader:
          models.append(pickle.load(reader))
      return models
    except FileNotFoundError as fnfe:
      logger.error('model file not found...')
      raise FileNotFoundError('model file not found ...')

class OnnxLoader(BaseLoader):
  ''' a simple OnnxLoader class.
  class which loads pickle model file.
  Args:
    model_path (str): model file path.
    multi_model (bool): multi model flag.
  '''

  def __init__(self, model_path, multi_model=False):
    self.model_path = model_path
    self.multi_model = multi_model

  def model_assert(self, model_name):
    ''' a helper function to assert model file name. '''
    if not model_name.endswith('.onnx'):
      logger.error(f'OnnxLoader save model extension is not .onnx but {model_name}')
      raise Exception(f'OnnxLoader save model extension is not .onnx but {model_name}')

  def load(self):
    ''' a function to load onnx model file. '''
    import onnxruntime as ort

    try:
      if not self.multi_model:
        self.model_path = [self.model_path]
      models = []
      for model in self.model_path:
        self.model_assert(model)
        model_path = path.join(path.dirname(path.abspath(__file__)), model)
        # onnx model load.
        sess = ort.InferenceSession(model_path)
        models.append(sess)
      return models
    except FileNotFoundError as fnfe:
      logger.error('model file not found...')
      raise FileNotFoundError('model file not found ...')
