''' user input and output schema models. '''
from pydantic import create_model
from utils import utils


""" Simple user input schema. """


class UserIn:
  '''
  `UserIn` pydantic model
  supports dynamic model attributes creation
  defined by user in configuration file.

  Args:
    UserInputSchema (pydantic.BaseModel): pydantic model.

  '''

  def __init__(self, config, *args, **kwargs):
    self._model_attr = utils.annotator(dict(config.input_schema))
    self.UserInputSchema = create_model(
        'UserInputSchema', **self._model_attr)


class UserOut:
  '''

  `UserOut` pydantic model
  supports dynamic model attributes creation
  defined by user in configuration file.

  Args:
    UserOutputSchema (pydantic.BaseModel): pydantic model.
  '''

  def __init__(self, config, *args, **kwargs):
    self._model_attr = utils.annotator(dict(config.out_schema))
    self.UserOutputSchema = create_model(
        'UserOutputSchema', **self._model_attr)
