from register import PREPROCESS
import cv2
import numpy as np


@PREPROCESS.register_module(name='some_custom_preprocess_fxn')
def custom_preprocess_fxn(input):
  _channels = 3
  _input_shape = (224, 224)
  _channels_first = 1
  input = cv2.resize(
      input[0], dsize=_input_shape, interpolation=cv2.INTER_CUBIC)
  if _channels_first:
    input = np.reshape(input, (_channels, *_input_shape))
  else:
    input = np.reshape(input, (*_input_shape, _channels))
  return np.asarray(input, np.float32)
