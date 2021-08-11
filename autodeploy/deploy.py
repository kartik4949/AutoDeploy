""" A simple deploy service class  """
import asyncio
import traceback

import numpy as np
import uvicorn
import argparse
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

from config.config import Config
from handlers.handlers import Handler
from schema import schema
from loader import ModelLoader
from service.builder import InfereBuilder
from logger import AppLogger 

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
handler.create_handlers(app)

input_model_schema = schema.UserIn(
    user_config)
output_model_schema = schema.UserOut(
    user_config)

model_loader = ModelLoader(
    user_config.model.model_path, user_config.model.model_file_type)
model = model_loader.load()

infer = InfereBuilder(user_config, model)


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
async def structured_server(payload: input_model_schema.UserInputSchema):
  logger.debug('model predict request incoming.')
  try:
    model_output = infer.get_inference(payload)
  except:
    logger.error('uncaught exception: %s', traceback.format_exc())
  else:
    logger.debug('model predict successfull.')

  out_response = {'out': model_output[0],
                  'probablity': model_output[1], 'status': 200}
  return out_response

if __name__ == "__main__":
  uvicorn.run(app, port=user_config.server.port)
