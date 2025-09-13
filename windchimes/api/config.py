from pydantic import BaseModel


class ApiSettings(BaseModel):
    cors_allowed_origins: list[str]
    port: int = 8000
