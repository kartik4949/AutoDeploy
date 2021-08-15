""" A simple deploy service class  """
import traceback
import argparse
import requests
from typing import List
from datetime import datetime

import uvicorn
import numpy as np
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Depends, FastAPI, Request, HTTPException
from sqlalchemy.orm import Session

from config.config import Config
from utils import utils
from handlers import Handler, ModelException
from schema import schema
from loader import ModelLoader
from service.builder import InfereBuilder
from logger import AppLogger 
from database import database, models



app = FastAPI()
Instrumentator().instrument(app).expose(app)

parser = argparse.ArgumentParser()


parser.add_argument("-o", "--mode", default='debug', type=str,
                    help="model for running deployment ,mode can be PRODUCTION or DEBUG")
parser.add_argument("-c", "--config", default='../configs/config.yaml', type=str,
                    help="a configuration yaml file path.")

args = parser.parse_args()

# __main__ (root) logger instance construction. 
applogger = AppLogger(__name__)
logger = applogger.get_logger()

# create database connection.
models.Base.metadata.create_all(bind=database.engine)

# user config for configuring model deployment.
user_config = Config(args.config).get_config()

# create exception handlers for fastapi.
handler = Handler()
handler.overide_handlers(app)
handler.create_handlers(app)

# create input and output schema for model endpoint api.
input_model_schema = schema.UserIn(
    user_config)
output_model_schema = schema.UserOut(
    user_config)

# create model loader instance.
model_loader = ModelLoader(
    user_config.model.model_path, user_config.model.model_file_type)
model = model_loader.load()

# inference model builder.
infer = InfereBuilder(user_config, model)

logger.debug('*****************Running Application in \'DEBUG\' mode.*****************')

@app.on_event('startup')
async def startup():
    logger.info('Connected to server...!!')

@app.middleware('http')
async def log_incoming_requests(request: Request, call_next):
  logger.info(f'incoming payload to server.')  
  response = await call_next(request)
  return response

@app.get('/model') 
async def model_details():
  logger.debug('model detail request incomming.')
  try:
    out_response = {'model': user_config.model.model_name,
                      'version': user_config.model.version}
  except KeyError as e:
    logger.error('Please define model name and version in config.')
  except:
    logger.error("Uncaught exception: %s", traceback.format_exc())
  return out_response

@app.post(f'/{user_config.model.endpoint}', response_model=output_model_schema.UserOutputSchema)
async def structured_server(payload: input_model_schema.UserInputSchema, db: Session = Depends(utils.get_db)):
  try:
    # model inference/prediction.
    model_output = infer.get_inference(payload)
  except:
    logger.error('uncaught exception: %s', traceback.format_exc())
    raise ModelException(name='structured_server')
  else:
    logger.debug('model predict successfull.')
  
  # store request data and model prediction in database.
  _time_stamp = datetime.now()
  _request_store = {'time_stamp': str(_time_stamp), 'prediction': model_output[0], 'is_drift': False} 
  _request_store.update(dict(payload))
  _request_store = models.Requests(**dict(_request_store))
  utils.store_request(db,_request_store) 
  
  # build output response json.
  out_response = {'out': model_output[0],
                  'probablity': model_output[1], 'status': 200}
  return out_response

if __name__ == "__main__":

  # run uvicorn server.
  uvicorn.run(app, port=user_config.server.port)
