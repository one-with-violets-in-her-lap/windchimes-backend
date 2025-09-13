import strawberry
from strawberry.fastapi import GraphQLRouter

from windchimes_backend.graphql_api.queries.example import example_query
from windchimes_backend.graphql_api.mutations.example_create import (
    create_example_mutation,
)


@strawberry.type
class Query:
    example = example_query


@strawberry.type
class Mutation:
    create_example = create_example_mutation


__schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(__schema)
