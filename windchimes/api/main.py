import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from windchimes.api.audio_proxy import audio_proxy_router
from windchimes.logging_setup import root_logger
from windchimes.core.config import app_config
from windchimes.api.lifespan import lifespan
from windchimes.api.strawberry_graphql_setup import graphql_router


root_logger.info("Launching uvicorn serving Graphql API")

app = FastAPI(lifespan=lifespan)
app.include_router(graphql_router, prefix="/graphql")
app.include_router(audio_proxy_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.api.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        port=app_config.api.port,
        host="0.0.0.0",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
