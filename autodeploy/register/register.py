''' a register for registering Inference, preprocess and postprocess modules. '''
from utils.registry import Registry

INFER = Registry('Inference')
PREPROCESS = Registry('Preprocess')
POSTPROCESS = Registry('Postprocess')
