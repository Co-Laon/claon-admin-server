from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from claon_admin.config.log import logger

from claon_admin.common.error.exception import (
    BadRequestException,
    UnauthorizedException,
    NotFoundException,
    ConflictException,
    UnprocessableEntityException,
    InternalServerException,
    ServiceUnavailableException, ErrorCode
)


def add_http_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(BadRequestException)
    async def bad_request_exception_handler(request: Request, exc: BadRequestException):
        logger.error(exc.message)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"code": exc.code.value, "message": exc.message})

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
        logger.error(exc.message)
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"code": exc.code.value, "message": exc.message})

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        logger.error(exc.message)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"code": exc.code.value, "message": exc.message})

    @app.exception_handler(ConflictException)
    async def conflict_exception_handler(request: Request, exc: ConflictException):
        logger.error(exc.message)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"code": exc.code.value, "message": exc.message})

    @app.exception_handler(UnprocessableEntityException)
    async def conflict_exception_handler(request: Request, exc: UnprocessableEntityException):
        logger.error(exc.message)
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content={"code": exc.code.value, "message": exc.message})

    @app.exception_handler(RequestValidationError)
    async def conflict_exception_handler(request: Request, exc: RequestValidationError):
        details = exc.errors()
        message = [{"loc": error["loc"], "message": error["msg"], "type": error["type"]} for error in details]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": ErrorCode.UNPROCESSABLE_ENTITY.value, "message": message}
        )

    @app.exception_handler(InternalServerException)
    async def internal_server_exception(request: Request, exc: InternalServerException):
        logger.error(exc.message)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"code": exc.code.value, "message": exc.message})

    @app.exception_handler(ServiceUnavailableException)
    async def service_unavailable_exception(request: Request, exc: ServiceUnavailableException):
        logger.error(exc.message)
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            content={"code": exc.code.value, "message": exc.message})
