from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import cast

from auth0.authentication.async_token_verifier import (
    AsyncAsymmetricSignatureVerifier,
    AsyncTokenVerifier,
)
from fastapi import FastAPI, Request

from windchimes.core.config import app_config
from windchimes.core.database import database
from windchimes.core.regular_tasks.scheduler import scheduler


@dataclass()
class LifespanState:
    token_verifier: AsyncTokenVerifier


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler.start()

    AUTH0_BASE_URL = "https://" + app_config.auth0.domain
    KEYS_URL = AUTH0_BASE_URL + "/.well-known/jwks.json"
    signature_verifier = AsyncAsymmetricSignatureVerifier(KEYS_URL)
    token_verifier = AsyncTokenVerifier(
        signature_verifier=signature_verifier,
        issuer=AUTH0_BASE_URL + "/",
        audience=app_config.auth0.frontend_client_id,
    )

    state = LifespanState(token_verifier=token_verifier)
    yield vars(state)

    await database.close()


def get_lifespan_state(request: Request) -> LifespanState:
    return cast(LifespanState, request.state)
