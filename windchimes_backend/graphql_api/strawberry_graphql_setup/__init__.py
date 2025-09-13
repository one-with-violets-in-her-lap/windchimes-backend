import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import MaxAliasesLimiter, MaxTokensLimiter
from graphql import NoDeprecatedCustomRule, NoSchemaIntrospectionCustomRule

from windchimes_backend.config import app_config
from windchimes_backend.graphql_api.strawberry_graphql_setup.context import (
    GraphQLRequestContext,
)
from windchimes_backend.graphql_api.mutations import Mutation
from windchimes_backend.graphql_api.queries import Query

security_extensions = []
if app_config.mode == "PROD":
    security_extensions = [
        NoSchemaIntrospectionCustomRule,
        NoDeprecatedCustomRule,
        MaxAliasesLimiter(max_alias_count=15),
        MaxTokensLimiter(max_token_count=1000),
    ]

__schema = strawberry.Schema(
    query=Query, mutation=Mutation, extensions=security_extensions
)

graphql_router = GraphQLRouter(
    __schema,
    context_getter=GraphQLRequestContext,
    graphql_ide="graphiql" if app_config.mode == "DEV" else None,
)
