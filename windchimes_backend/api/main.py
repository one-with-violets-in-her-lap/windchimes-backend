import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from windchimes_backend.logging_setup import root_logger
from windchimes_backend.core.config import app_config
from windchimes_backend.api.lifespan import lifespan
from windchimes_backend.api.strawberry_graphql_setup import graphql_router


root_logger.info("Launching uvicorn serving Graphql API")

app = FastAPI(lifespan=lifespan)
app.include_router(graphql_router, prefix="/graphql")
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.api.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, port=app_config.api.port, host="0.0.0.0")
