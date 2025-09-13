from contextlib import asynccontextmanager

from fastapi import FastAPI

from windchimes.core.database import database
from windchimes.core.regular_tasks.scheduler import scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler.start()
    yield
    await database.close()
