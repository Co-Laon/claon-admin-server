import asyncio

import nest_asyncio
import uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from claon_admin.config.consts import SESSION_SECRET_KEY
from claon_admin.container import Container, db

nest_asyncio.apply()

""" Initialize Database """
asyncio.run(db.create_database())


def create_app() -> FastAPI:
    app = FastAPI()
    container = Container()

    """ Define Container """
    container.wire()
    app.container = container

    """ Define Routers """
    api_version = "v1"
    api_prefix = "/api/" + api_version

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
