from typing import Union

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


def serve(port: int = 8080):
    uvicorn.run(app, host="0.0.0.0", port=port)
