from typing import Optional

from pydantic import BaseModel


class PlatformSpecificParams(BaseModel):
    soundcloud_secret_token: Optional[str] = None
