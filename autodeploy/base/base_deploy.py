''' Base class for deploy driver service. '''
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from handlers import Handler, ModelException
from _schema import UserIn, UserOut


class BaseDriverService(ABC):
    def __init__(self, *args, **kwargs):
        ...

    def _setup_schema(self) -> Tuple[Any, Any]:
        '''
        a function to setup input and output schema for
        server.

        '''
        # create input and output schema for model endpoint api.
        output_model_schema = UserOut(
            self.user_config)
        input_model_schema = UserIn(
            self.user_config)
        return (input_model_schema, output_model_schema)

    @staticmethod
    def handler_setup(app):
        '''
        a simple helper function to overide handlers
        '''
        # create exception handlers for fastapi.
        handler = Handler()
        handler.overide_handlers(app)
        handler.create_handlers(app)

    def _app_include(self, routers, app):
        '''
        a simple helper function to register routers
        with the fastapi `app`.

        '''
        for route in routers:
            app.include_router(route)

    @abstractmethod
    def setup(self, *args, **kwargs):
        '''
        abstractmethod for setup to be implemeneted in child class
        for setup of monitor driver.

        '''
        raise NotImplementedError('setup function is not implemeneted.')
