''' Base class for loaders. '''
from abc import ABC, abstractmethod


class BaseLoader(ABC):
    def __init__(self, *args, **kwargs):
        ...

    @abstractmethod
    def load(self, *args, **kwargs):
        '''
        abstractmethod for loading model file.

        '''
        raise NotImplementedError('load function is not implemeneted.')
