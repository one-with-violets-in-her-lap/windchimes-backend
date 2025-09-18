from strawberry.extensions import FieldExtension

from windchimes.api.reusable_schemas.errors import (
    UnauthorizedErrorGraphQL,
)
from windchimes.api.utils.graphql import GraphQLRequestInfo


class AuthorizedOnlyExtension(FieldExtension):
    async def resolve_async(
        self, _next, root, info: GraphQLRequestInfo, *args, **kwargs
    ):
        if info.context["current_user"] is not None:
            return await _next(root, info, *args, **kwargs)
        else:
            return UnauthorizedErrorGraphQL()
