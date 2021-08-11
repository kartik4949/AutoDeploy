import sklearn
import numpy as np
from fastapi.exceptions import RequestValidationError

from register.register import INFERE


@INFERE.register_module(name='sklearn')
class SkLearnInfere:
  """ a SKLearn  inference class. """

  def __init__(self, user_config, model):
    self.config = user_config
    self.model = model

  def infere(self, input):
    input = [v for k, v in input]
    assert type(input) in [np.ndarray, list], RequestValidationError(
        'Model input are not valid!')
    class_probablities = self.model.predict_proba([input])
    out_class = np.argmax(class_probablities)
    return class_probablities[0][out_class], out_class
