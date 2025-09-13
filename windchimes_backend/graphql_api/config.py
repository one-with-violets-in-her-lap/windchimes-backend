from pydantic import BaseModel


class GraphQLApiSettings(BaseModel):
    cors_allowed_origins: list[str]
    port: int = 8000
