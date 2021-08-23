""" A simple app logger utility. """
import logging


class AppLogger:
  def __init__(self, __file_name) -> None:
    # Create a custom logger
    logging.config.fileConfig(
        "./config/logging.conf",
        disable_existing_loggers=False)
    self.__file_name = __file_name

  def get_logger(self):
    # get root logger
    logger = logging.getLogger(self.__file_name)
    return logger
