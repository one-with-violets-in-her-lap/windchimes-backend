import uvicorn
from fastapi import FastAPI

from windchimes_backend.logging_setup import root_logger
from windchimes_backend.config import app_config
from windchimes_backend.graphql_api.lifespan import lifespan
from windchimes_backend.graphql_api.graphql_setup import graphql_router


root_logger.info("Launching uvicorn serving Graphql API")

app = FastAPI(lifespan=lifespan)
app.include_router(graphql_router, prefix="/graphql")

uvicorn.run(app, port=app_config.graphql_api.port)
