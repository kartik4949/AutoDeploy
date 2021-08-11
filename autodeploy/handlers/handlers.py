from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, StarletteHTTPException
from fastapi.responses import JSONResponse, PlainTextResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
  return JSONResponse(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
  )


async def http_exception_handler(request, exc):
  return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


class Handler:
  def create_handlers(self, app):
    _exc_app_request = app.exception_handler(RequestValidationError)
    _exc_app_starlette = app.exception_handler(StarletteHTTPException)

    _validation_exception_handler = _exc_app_request(
        validation_exception_handler)
    _starlette_exception_handler = _exc_app_starlette(http_exception_handler)
