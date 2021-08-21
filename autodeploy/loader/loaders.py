import pickle


class PickleLoader:
  def __init__(self, model_path):
    self.model_path = model_path

  def load(self):
    # TODO: do handling
    with open(self.model_path, 'rb') as reader:
      return pickle.load(reader)
