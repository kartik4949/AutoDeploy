import pickle
from os import path

class PickleLoader:
  def __init__(self, model_path):
    self.model_path = model_path

  def load(self):
    # TODO: do handling
    config_path = path.join(path.dirname(path.abspath(__file__)), self.model_path)    
    with open(config_path, 'rb') as reader:
      return pickle.load(reader)
