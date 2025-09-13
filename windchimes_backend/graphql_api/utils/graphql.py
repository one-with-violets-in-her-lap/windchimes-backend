import strawberry

from windchimes_backend.graphql_api.strawberry_graphql_setup.context import (
    GraphQLRequestContext,
)


GraphQLRequestInfo = strawberry.Info[GraphQLRequestContext]
