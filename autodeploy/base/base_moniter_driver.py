''' Base class for monitor driver service. '''
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from handlers import Handler, ModelException
from _schema import UserIn, UserOut


class BaseMonitorService(ABC):
    def __init__(self, *args, **kwargs):
        ...

    @abstractmethod
    def setup(self, *args, **kwargs):
        '''
        abstractmethod for setup to be implemeneted in child class
        for setup of monitor driver.

        '''
        raise NotImplementedError('setup function is not implemeneted.')

    def _setup_schema(self) -> Tuple[Any, Any]:
        '''
        a function to setup input and output schema for
        server.

        '''
        # create input and output schema for model endpoint api.
        input_model_schema = UserIn(
            self.user_config)
        output_model_schema = UserOut(
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
    def _load_monitor_algorithm(self, *args, **kwargs):
        '''
        abstractmethod for loading monitor algorithm which needs
        to be overriden in child class.
        '''

        raise NotImplementedError('load monitor function is not implemeneted.')
