''' A simple Exception handlers. '''
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, StarletteHTTPException
from fastapi.responses import JSONResponse, PlainTextResponse


class ModelException(Exception):
  ''' Custom ModelException class 
  Args:
    name (str): name of the exception.
  '''

  def __init__(self, name: str):
    self.name = name


async def model_exception_handler(request: Request, exception: ModelException):
  return JSONResponse(status_code=500, content={"message": "model failure."})


async def validation_exception_handler(request: Request, exc: RequestValidationError):
  return JSONResponse(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
  )


async def http_exception_handler(request, exc):
  return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


class Handler:
  ''' Setup Handler class to setup 
  and bind custom and overriden exceptions to fastapi
  application.

  '''

  def overide_handlers(self, app):
    ''' A helper function to overide default fastapi handlers.
    Args:
      app: fastapi application.
    '''
    _exc_app_request = app.exception_handler(RequestValidationError)
    _exc_app_starlette = app.exception_handler(StarletteHTTPException)

    _validation_exception_handler = _exc_app_request(
        validation_exception_handler)
    _starlette_exception_handler = _exc_app_starlette(
        http_exception_handler)

  def create_handlers(self, app):
    ''' A function to bind handlers to fastapi application.
    Args:
      app: fastapi application.
    '''
    _exc_app_model = app.exception_handler(ModelException)
    _exce_model_exception_handler = _exc_app_model(model_exception_handler)
