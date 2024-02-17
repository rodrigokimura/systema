from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from .db import create_db_and_tables
from .project_manager.endpoints import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


def serve(port: int = 8080):
    uvicorn.run(app, host="0.0.0.0", port=port)
