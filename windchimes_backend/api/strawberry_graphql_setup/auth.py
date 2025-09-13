from strawberry.extensions import FieldExtension

from windchimes_backend.api.reusable_schemas.errors import (
    UnauthorizedErrorGraphQL,
)


class AuthorizedOnlyExtension(FieldExtension):
    async def resolve_async(self, _next, root, info, *args, **kwargs):
        if info.context.current_user is not None:
            return await _next(root, info, *args, **kwargs)
        else:
            return UnauthorizedErrorGraphQL()
