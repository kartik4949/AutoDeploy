""" A simple app logger utility. """
import logging
from os import path

class AppLogger:
    ''' a simple logger class.
    logger class which takes configuration file and
    setups logging module.

    Args:
      file_name (str): name of file logger called from i.e `__name__`

    '''

    def __init__(self, __file_name) -> None:
        # Create a custom logger
        config_path = path.join(path.dirname(path.abspath(__file__)),
                                '../config/logging.conf')
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
        self.__file_name = __file_name

    def get_logger(self):
        '''
        a helper function to get logger with file name.

        '''
        # get root logger
        logger = logging.getLogger(self.__file_name)
        return logger
