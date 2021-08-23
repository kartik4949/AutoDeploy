""" A simple app logger utility. """
import logging
from os import path


class AppLogger:
  def __init__(self, __file_name) -> None:
    # Create a custom logger
    config_path = path.join(path.dirname(path.abspath(__file__)),
                            '../config/logging.conf')
    logging.config.fileConfig(config_path, disable_existing_loggers=False)
    self.__file_name = __file_name

  def get_logger(self):
    # get root logger
    logger = logging.getLogger(self.__file_name)
    return logger
