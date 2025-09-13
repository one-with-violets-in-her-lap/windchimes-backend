import strawberry

from windchimes.api.strawberry_graphql_setup.context import (
    GraphQLRequestContext,
)


GraphQLRequestInfo = strawberry.Info[GraphQLRequestContext]
