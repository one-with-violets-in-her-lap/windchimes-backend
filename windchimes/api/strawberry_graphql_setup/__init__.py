import strawberry
from fastapi import UploadFile
from strawberry.extensions import MaskErrors, MaxAliasesLimiter, MaxTokensLimiter
from strawberry.fastapi import GraphQLRouter
from strawberry.file_uploads import Upload

from windchimes.api.mutations import Mutation
from windchimes.api.queries import Query
from windchimes.api.strawberry_graphql_setup.context import (
    get_graphql_context,
)
from windchimes.core.config import app_config

security_extensions = []
if app_config.mode == "PROD":
    security_extensions = [
        MaxAliasesLimiter(max_alias_count=15),
        MaxTokensLimiter(max_token_count=1000),
        MaskErrors(),
    ]

__schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=security_extensions,
    scalar_overrides={UploadFile: Upload},
)

graphql_router = GraphQLRouter(
    __schema,
    context_getter=get_graphql_context,
    graphql_ide="apollo-sandbox" if app_config.mode == "DEV" else None,
    multipart_uploads_enabled=True,
)
