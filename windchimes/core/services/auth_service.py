import logging

from auth0.authentication.async_token_verifier import AsyncTokenVerifier
from auth0.exceptions import TokenValidationError

from windchimes.core.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, token_verifier: AsyncTokenVerifier):
        self.token_verifier = token_verifier

    async def get_user_from_token(self, jwt_token: str):
        try:
            user = await self.token_verifier.verify(jwt_token)
            return User(**user)
        except TokenValidationError as error:
            logger.error("auth failed: %s", error)
            return None
