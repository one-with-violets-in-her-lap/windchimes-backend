from pydantic import BaseModel

from windchimes_backend.core.models.platform import Platform


class TrackReferenceSchema(BaseModel):
    id: int
    platform: Platform
    platform_id: str
