import logging
import os
from typing import Literal, Optional

from pydantic import BaseModel, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from windchimes_backend.api.config import ApiSettings


ENV_FILE_PATH = os.environ.get("WINDCHIMES__ENV_FILE") or "./.env"

logger = logging.getLogger()


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
    fallback_client_id: str = ""
    """Fallback API key for Soundcloud API

    Used when scraping it automatically does not work
    """


class ImagekitApiSettings(BaseModel):
    private_key: str


class ProxySettings(BaseModel):
    url: Optional[str] = None


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="WINDCHIMES__",
        extra="ignore",
    )

    mode: Literal["DEV", "PROD"]

    database: DatabaseSettings

    api: ApiSettings

    auth0: Auth0Settings

    youtube_data_api: YoutubeDataApiSettings

    soundcloud_api: SoundcloudApiSettings = SoundcloudApiSettings()

    imagekit_api: ImagekitApiSettings

    proxy: ProxySettings = ProxySettings()

    @staticmethod
    def load_from_env():
        return AppConfig.model_validate({})


logger.info("Loading app config from '%s'", ENV_FILE_PATH)
app_config = AppConfig.load_from_env()
