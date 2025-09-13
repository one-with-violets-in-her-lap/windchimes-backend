import strawberry

from windchimes_backend.core.models.platform import Platform


@strawberry.type
class TrackReferenceToReadGraphQL:
    id: int
    platform_id: str
    platform: Platform
