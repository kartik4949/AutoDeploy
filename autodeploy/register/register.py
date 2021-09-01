''' a register for registering Inference and preprocess modules. '''
from utils.registry import Registry

INFER = Registry('Inference')
PREPROCESS = Registry('Preprocess')
