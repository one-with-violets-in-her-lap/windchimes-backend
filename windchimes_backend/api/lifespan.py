from contextlib import asynccontextmanager

from fastapi import FastAPI

from windchimes_backend.core.database import database
from windchimes_backend.core.regular_tasks.scheduler import scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler.start()
    yield
    await database.close()
