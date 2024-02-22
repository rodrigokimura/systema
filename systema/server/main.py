from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from systema.__version__ import VERSION
from systema.server.auth.endpoints import router as auth_router
from systema.server.db import create_db_and_tables
from systema.server.project_manager.endpoints.project import router as project_router
from systema.server.project_manager.endpoints.task import router as task_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, version=VERSION)

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def serve(port: int = 8080, dev: bool = False):
    uvicorn.run(
        "systema.server.main:app",
        host="0.0.0.0",
        port=port,
        reload=dev,
        loop="uvloop",
        http="httptools",
        ws="websockets",
    )
