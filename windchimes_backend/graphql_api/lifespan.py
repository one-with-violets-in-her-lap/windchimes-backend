from contextlib import asynccontextmanager

from fastapi import FastAPI

from windchimes_backend.core.database import database


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await database.close()
