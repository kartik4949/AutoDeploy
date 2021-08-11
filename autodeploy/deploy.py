""" A simple deploy service class  """
import logging
import asyncio

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

app = FastAPI()
Instrumentator().instrument(app).expose(app)

parser = argparse.ArgumentParser()


parser.add_argument("-o", "--mode", default='debug', type=str,
                    help="mode can be PRODUCTION or DEBUG")
parser.add_argument("-c", "--config", default='../configs/config.yaml', type=str,
                    help="mode can be PRODUCTION or DEBUG")

args = parser.parse_args()
if args.mode == 'debug':
  print('*****************Running Application in \'DEBUG\' mode.*****************')

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


@app.get('/model/', response_model=output_model_schema.UserOutputSchema)
async def model_details():
  try:
    out_response = {'model': user_config.model.model_name,
                    'version': user_config.model.version}
  except Exception as e:
    logging.error(e)
    raise HttpException(e)
  return out_response


@app.post(f'/{user_config.model.endpoint}', response_model=output_model_schema.UserOutputSchema)
async def structured_server(payload: input_model_schema.UserInputSchema):
  logging.debug("request incoming!!")
  await asyncio.sleep(5)
  model_output = infer.get_inference(payload)
  out_response = {'out': model_output[0],
                  'probablity': model_output[1], 'status': 200}
  return out_response

if __name__ == "__main__":
  uvicorn.run(app, port=user_config.server.port)
