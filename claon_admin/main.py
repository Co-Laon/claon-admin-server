import asyncio
from os import environ

import nest_asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from starlette.middleware.sessions import SessionMiddleware

from claon_admin.common.error.handler import add_http_exception_handler
from claon_admin.common.util.db import db
from claon_admin.config.config import conf
from claon_admin.container import Container
from claon_admin.middleware.file import LimitUploadSize
from claon_admin.middleware.log import LoggerMiddleware
from claon_admin.router import center, auth, admin, user, index

nest_asyncio.apply()

""" Initialize Database """
if environ.get("API_ENV") != "test":
    asyncio.run(db.create_database())
else:
    asyncio.run(db.create_drop_database())


def create_app() -> FastAPI:
    claon_app = FastAPI()
    container = Container()

    """ Define Container """
    container.wire(modules=[auth, admin, center, user])
    claon_app.container = container

    """ Define Routers """
    api_version = "v1"
    api_prefix = "/api/" + api_version

    claon_app.include_router(index.router)
    claon_app.include_router(auth.router, prefix=api_prefix + "/auth")
    claon_app.include_router(center.router, prefix=api_prefix + "/centers")
    claon_app.include_router(admin.router, prefix=api_prefix + "/admin")
    claon_app.include_router(user.router, prefix=api_prefix + "/users")

    claon_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    claon_app.add_middleware(SessionMiddleware, secret_key=conf().SESSION_SECRET_KEY)
    claon_app.add_middleware(LoggerMiddleware)
    claon_app.add_middleware(LimitUploadSize)
    add_pagination(claon_app)

    add_http_exception_handler(claon_app)

    return claon_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
