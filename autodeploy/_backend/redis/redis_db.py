from uuid import uuid4
import struct

import redis
import numpy as np


class RedisDB:
  def __init__(self, config) -> None:
    self.config = config
    self.redis = redis.Redis()

  def encode(self, input, shape):
    bytes = input.tobytes()
    _encoder = 'I'*len(shape)
    shape = struct.pack('>' + _encoder, *shape)
    return shape + bytes

  def pull(self, id, dtype, ndim):
    input_encoded = self.redis.get(id)
    shape = struct.unpack('>' + ('I'*ndim), input_encoded[:ndim*4])
    a = np.frombuffer(input_encoded[ndim*4:], dtype=dtype).reshape(shape)
    return a

  def push(self, input, dtype, shape):
    input_hash = str(uuid4())
    input = np.asarray(input, dtype=dtype)
    encoded_input = self.encode(input, shape=shape)
    self.redis.set(input_hash, encoded_input)
    return input_hash

  def pop():
    NotImplementedError('Not implemented yet!')
