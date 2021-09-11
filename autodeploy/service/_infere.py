""" Inference model classes """
import sklearn
import numpy as np
import cv2
from fastapi.exceptions import RequestValidationError

from register.register import INFER
from base import BaseInfere


@INFER.register_module(name='sklearn')
class SkLearnInfere(BaseInfere):
  """ a SKLearn  inference class. 
  Args:
    config (Config): a configuring instance.
    model (Any): prediction model instance.
  """

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
  """ a Onnx inference class.
  Args:
    config (Config): a configuring instance.
    model (Any): prediction model instance.
    input_name (str): Onnx model input layer name. 
    label_name (str): Onnx model output layer name. 
  """

  def __init__(self, user_config, model):
    self.config = user_config
    self.model = model
    self.input_name = self.model.get_inputs()[0].name
    self.label_name = self.model.get_outputs()[0].name

  def infere(self, input):
    '''
    inference method to predict with onnx model
    on input data.

    Args:
      input (ndarray): numpy input array.

    '''
    assert type(input) in [np.ndarray, list], 'Model input are not valid!'
    pred_onx = self.model.run(
        [self.label_name], {self.input_name: [input]})[0]
    pred_onx = pred_onx.tolist()
    out_class = np.argmax(pred_onx[0])
    return pred_onx[0][out_class], out_class
