import strawberry

from windchimes.core.models.platform import Platform


PlatformGraphQL = strawberry.enum(Platform)
