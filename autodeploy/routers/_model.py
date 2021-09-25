''' a simple Model details router utilities. '''
import traceback

from fastapi import APIRouter
from fastapi import Request

from logger import AppLogger

router = APIRouter()

applogger = AppLogger(__name__)
logger = applogger.get_logger()


@router.on_event('startup')
async def startup():
    logger.info('Connected to server...!!')


class ModelDetailRouter:
    '''
    a `ModelDetailRouter` class which routes `\model`
    to fastapi application.
    model detail endpoint gives model related details
    example:
      model: name of model.
      version: model version details.

    Args:
      user_config (Config): configuration instance.

    '''

    def __init__(self, config) -> None:
        self.user_config = config

    def register_router(self):
        '''
        a method to register model router to fastapi router.

        '''
        @router.get('/model')
        async def model_details():
            nonlocal self
            logger.debug('model detail request incomming.')
            try:
                out_response = {'model': self.user_config.model.model_name,
                                'version': self.user_config.model.version}
            except KeyError as e:
                logger.error('Please define model name and version in config.')
            except BaseException:
                logger.error("Uncaught exception: %s", traceback.format_exc())
            return out_response
