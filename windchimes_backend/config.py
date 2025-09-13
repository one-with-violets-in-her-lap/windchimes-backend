from typing import Optional
from pydantic import BaseModel, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from windchimes_backend.graphql_api.config import GraphQLApiSettings


class DatabaseSettings(BaseModel):
    url: AnyUrl
    echo: bool = True


class Auth0Settings(BaseModel):
    domain: str
    frontend_client_id: str
    client_id: str
    secret: str


class YoutubeDataApiSettings(BaseModel):
    key: str


class SoundcloudApiSettings(BaseModel):
    fallback_client_id: Optional[str] = None
    """Fallback API key for Soundcloud API

    Used when scraping it automatically does not work
    """


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=["./prod.env", "./.env"],
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="WINDCHIMES__",
        extra="ignore",
    )

    database: DatabaseSettings

    graphql_api: GraphQLApiSettings

    auth0: Auth0Settings

    youtube_data_api: YoutubeDataApiSettings

    soundcloud_api: SoundcloudApiSettings = SoundcloudApiSettings()

    @staticmethod
    def load_from_env():
        return AppConfig.model_validate({})


app_config = AppConfig.load_from_env()
