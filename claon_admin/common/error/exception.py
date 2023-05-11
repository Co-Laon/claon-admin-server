from enum import Enum


class ErrorCode(Enum):
    # 400 Bad Request
    ROW_ALREADY_EXIST = 40000
    USER_ALREADY_SIGNED_UP = 40001
    DUPLICATED_NICKNAME = 40002
    INVALID_FORMAT = 40003
    WRONG_DATE_RANGE = 40004

    # 401 Unauthorized Error
    NOT_ACCESSIBLE = 40100
    INVALID_JWT = 40101
    NOT_SIGN_IN = 40102
    USER_DOES_NOT_EXIST = 40103
    NONE_ADMIN_ACCOUNT = 40104

    # 404 Not Found Error
    DATA_DOES_NOT_EXIST = 40400

    # 409 Conflict
    CONFLICT_STATE = 40900

    # 422
    UNPROCESSABLE_ENTITY = 42200

    # 500 Internal Server Error
    INTERNAL_SERVER_ERROR = 50000

    # 503 Service Unavailable
    SERVICE_UNAVAILABLE = 50300


class BaseRuntimeException(Exception):
    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message


class BadRequestException(BaseRuntimeException):
    pass


class UnauthorizedException(BaseRuntimeException):
    pass


class NotFoundException(BaseRuntimeException):
    pass


class ConflictException(BaseRuntimeException):
    pass


class UnprocessableEntityException(BaseRuntimeException):
    pass


class InternalServerException(BaseRuntimeException):
    pass


class ServiceUnavailableException(BaseRuntimeException):
    pass
