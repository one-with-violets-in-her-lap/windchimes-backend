import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from windchimes_backend.logging_setup import root_logger
from windchimes_backend.core.config import app_config
from windchimes_backend.graphql_api.lifespan import lifespan
from windchimes_backend.graphql_api.strawberry_graphql_setup import graphql_router


root_logger.info("Launching uvicorn serving Graphql API")

app = FastAPI(lifespan=lifespan)
app.include_router(graphql_router, prefix="/graphql")
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.graphql_api.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

uvicorn.run(app, port=app_config.graphql_api.port)
