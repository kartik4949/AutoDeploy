""" A simple deploy service class  """
import traceback
from typing import List
from datetime import datetime

import numpy as np
import uvicorn
import argparse
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from fastapi import Request
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from config.config import Config
from handlers import Handler, ModelException
from schema import schema
from loader import ModelLoader
from service.builder import InfereBuilder
from logger import AppLogger 
from database import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
Instrumentator().instrument(app).expose(app)

parser = argparse.ArgumentParser()


parser.add_argument("-o", "--mode", default='debug', type=str,
                    help="mode can be PRODUCTION or DEBUG")
parser.add_argument("-c", "--config", default='../configs/config.yaml', type=str,
                    help="mode can be PRODUCTION or DEBUG")

args = parser.parse_args()

applogger = AppLogger(__name__)
logger = applogger.get_logger()

logger.debug('*****************Running Application in \'DEBUG\' mode.*****************')

user_config = Config(args.config).get_config()

handler = Handler()
handler.overide_handlers(app)
handler.create_handlers(app)

input_model_schema = schema.UserIn(
    user_config)
output_model_schema = schema.UserOut(
    user_config)

model_loader = ModelLoader(
    user_config.model.model_path, user_config.model.model_file_type)
model = model_loader.load()

infer = InfereBuilder(user_config, model)

def store_request(db, db_item):
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event('startup')
async def startup():
    logger.info('Connecting to server...!!')

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
  logger.info(f'incoming data')  
  response = await call_next(request)
  logger.info('request processed')
  return response

@app.get('/model') 
async def model_details():
  logger.debug('model detail request incomming.')
  try:
    out_response = {'model': user_config.model.model_name,
                      'version': user_config.model.version}
  except KeyError as e:
    logger.error('please define model name and version in config.')
  except:
    logger.error("uncaught exception: %s", traceback.format_exc())
  return out_response

@app.post(f'/{user_config.model.endpoint}', response_model=output_model_schema.UserOutputSchema)
async def structured_server(payload: input_model_schema.UserInputSchema, db :Session =  Depends(get_db)):
  _time_stamp = datetime.now()
  try:
    model_output = infer.get_inference(payload)
  except:
    logger.error('uncaught exception: %s', traceback.format_exc())
    raise ModelException(name='structured_server')
  else:
    logger.debug('model predict successfull.')

  _request_store = {'time_stamp': str(_time_stamp), 'prediction': model_output[0], 'is_drift': False} 
  _request_store.update(dict(payload))
  _request_store = models.Requests(**_request_store)
  store_request(db,_request_store) 

  out_response = {'out': model_output[0],
                  'probablity': model_output[1], 'status': 200}
  return out_response

if __name__ == "__main__":
  uvicorn.run(app, port=user_config.server.port)
