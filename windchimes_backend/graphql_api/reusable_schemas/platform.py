import strawberry

from windchimes_backend.core.models.platform import Platform


PlatformGraphQL = strawberry.enum(Platform)
