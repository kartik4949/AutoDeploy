from register import METRICS
import numpy as np

@METRICS.register_module(name='some_metric')
def length_of_petal(x):
  return x[0]

@METRICS.register_module(name='some_metric')
def brightness(x):
  b = calculate_brightness(x)
  return b
