from os import path

from logger import AppLogger

logger = AppLogger(__name__).get_logger()


class PickleLoader:
  def __init__(self, model_path, multi_model=False):
    self.model_path = model_path
    self.multi_model = multi_model

  def load(self):
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

class OnnxLoader:
  def __init__(self, model_path, multi_model=False):
    self.model_path = model_path
    self.multi_model = multi_model

  def model_assert(self, model_name):
    if not model_name.endswith('.onnx'):
      logger.error(f'OnnxLoader save model extension is not .onnx but {model_name}')
      raise Exception(f'OnnxLoader save model extension is not .onnx but {model_name}')

  def load(self):
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
