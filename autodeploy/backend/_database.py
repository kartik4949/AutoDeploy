''' A simple database class utility. '''
from database import database, models
from logger import AppLogger

applogger = AppLogger(__name__)
logger = applogger.get_logger()


class Database:
  '''
  A database class that creates and stores incoming requests
  in user define database with given schema.
  Args:
    config (Config): A configuration object which contains configuration
    for the deployment.

  Attributes:
    config (Config): internal configuration object for configurations.

  Example:
    >> with Database(config) as db:
    >> .... db.store_request(item)

  '''

  def __init__(self, config) -> None:
    self.config = config
    self.db = None

  @classmethod
  def bind(cls):
    models.Base.metadata.create_all(bind=database.engine)

  def setup(self):
    # create database engine and bind all.
    self.bind()
    self.db = database.SessionLocal()

  def close(self):
    self.db.close()

  def store_request(self, db_item) -> None:

    try:
      self.db.add(db_item)
      self.db.commit()
      self.db.refresh(db_item)
    except Exception as exc:
      logger.error(
          'Some error occured while storing request in database.')
      raise Exception(
          'Some error occured while storing request in database.')
    return db_item
