import uuid

from fastapi import Request
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import Message

from claon_admin.config.log import logger


async def set_body(request: Request):
    receive_ = await request._receive()

    async def receive() -> Message:
        return receive_

    request._receive = receive


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        idem = ''.join(str(uuid.uuid4()))
        request_headers = dict(request.headers)
        logger.info(f"[{idem}] [REQUEST] path: {request.url.path}")
        if not ("multipart/form-data" in request_headers['content-type']):
            await set_body(request)
            request_body = await request.body()
            if request_body and not ("multipart/form-data" in request_headers['content-type']):
                logger.info(f"[{idem}] [REQUEST] body: {request_body.decode('utf-8')}")

        response = await call_next(request)

        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))

        logger.info(f"[{idem}] [RESPONSE] status_code: {response.status_code}")
        logger.info(f"[{idem}] [RESPONSE] body: {response_body[0].decode('utf-8')}")

        return response
