""" Inference model classes """
import sklearn
import numpy as np
import cv2
from fastapi.exceptions import RequestValidationError

from register.register import INFER
from base import BaseInfere


@INFER.register_module(name='sklearn')
class SkLearnInfere(BaseInfere):
  """ a SKLearn  inference class. """

  def __init__(self, user_config, model):
    self.config = user_config
    self.model = model

  def infere(self, input):
    assert type(input) in [np.ndarray, list], 'Model input are not valid!'
    class_probablities = self.model.predict_proba([input])
    out_class = np.argmax(class_probablities)
    return class_probablities[0][out_class], out_class

@INFER.register_module(name='onnx')
class OnnxInfere(BaseInfere):
  """ a Onnx inference class. """

  def __init__(self, user_config, model):
    self.config = user_config
    self.model = model
    self.input_name = self.model.get_inputs()[0].name
    self.label_name = self.model.get_outputs()[0].name

  def input_preprocess(self, input):
    if self.config.model.type == 'cv':
      _channels = self.config.cv.channels
      _input_shape = self.config.cv.input_shape
      _channels_first = self.config.cv.channels_first
      input = cv2.resize(
          input[0], dsize=self.config.cv.input_shape, interpolation=cv2.INTER_CUBIC)
      if _channels_first:
        input = np.reshape(input, (_channels, *self.config.cv.input_shape))
      else:
        input = np.reshape(input, (*self.config.cv.input_shape, _channels))
      return np.asarray(input, dtype=getattr(np, self.config.cv.dtype))

  def infere(self, input):
    input = self.input_preprocess(input=input)
    assert type(input) in [np.ndarray, list], 'Model input are not valid!'
    pred_onx = self.model.run(
        [self.label_name], {self.input_name: [input]})[0]
    pred_onx = pred_onx.tolist()
    out_class = np.argmax(pred_onx[0])
    return pred_onx[0][out_class], out_class
