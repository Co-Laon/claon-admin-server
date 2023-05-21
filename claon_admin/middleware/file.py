from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from claon_admin.common.error.exception import ErrorCode
from claon_admin.config.log import logger


class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.max_uploaded_size = 10_000_000  # 10MB

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "POST":
            request_headers = dict(request.headers)
            if request_headers.get('content-type') is not None \
                    and "multipart/form-data" in request_headers['content-type']:
                if 'content-length' not in request_headers:
                    logger.error("[REQUEST] [%s] path: %s [RESPONSE] code: %d",
                                 request.method, request.url.path, ErrorCode.LENGTH_REQUIRED.value)
                    return JSONResponse(status_code=status.HTTP_411_LENGTH_REQUIRED,
                                        content={"code": ErrorCode.LENGTH_REQUIRED.value,
                                                 "message": "파일 요청 형식이 올바르지 않습니다."})
                content_length = int(request_headers['content-length'])
                if content_length > self.max_uploaded_size:
                    logger.error("[REQUEST] [%s] path: %s [RESPONSE] code: %d",
                                 request.method, request.url.path, ErrorCode.REQUEST_ENTITY_TOO_LARGE.value)
                    return JSONResponse(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                        content={"code": ErrorCode.REQUEST_ENTITY_TOO_LARGE.value,
                                                 "message": "파일은 10MB 이하로 업로드 가능합니다."})
        return await call_next(request)
