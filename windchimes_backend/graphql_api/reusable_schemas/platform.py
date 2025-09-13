import strawberry

from windchimes_backend.core.models.platform import Platform


PlatformToRead = strawberry.enum(Platform)
