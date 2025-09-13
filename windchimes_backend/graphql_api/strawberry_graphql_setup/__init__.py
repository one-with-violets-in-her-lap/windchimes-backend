import strawberry
from strawberry.fastapi import GraphQLRouter

from windchimes_backend.graphql_api.strawberry_graphql_setup.context import (
    GraphQLRequestContext,
)
from windchimes_backend.graphql_api.mutations import Mutation
from windchimes_backend.graphql_api.queries import Query


__schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(__schema, context_getter=GraphQLRequestContext)
