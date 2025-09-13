import logging

from auth0.authentication.token_verifier import (
    TokenVerifier,
    AsymmetricSignatureVerifier,
    TokenValidationError,
)

from windchimes.core.config import app_config
from windchimes.core.models.user import User


AUTH0_BASE_URL = "https://" + app_config.auth0.domain
KEYS_URL = AUTH0_BASE_URL + "/.well-known/jwks.json"

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        signature_verifier = AsymmetricSignatureVerifier(KEYS_URL)
        self.token_verifier = TokenVerifier(
            signature_verifier=signature_verifier,
            issuer=AUTH0_BASE_URL + "/",
            audience=app_config.auth0.frontend_client_id,
        )

    def get_user_from_token(self, jwt_token: str):
        try:
            user = self.token_verifier.verify(jwt_token)
            return User(**user)
        except TokenValidationError as error:
            logger.error("auth failed: %s", error)
            return None


auth_service = AuthService()
