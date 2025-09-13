from pydantic import BaseModel, HttpUrl


class ApiSettings(BaseModel):
    cors_allowed_origins: list[str]
    public_base_url: HttpUrl
    port: int = 8000
