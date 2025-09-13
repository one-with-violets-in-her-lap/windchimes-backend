import strawberry
from strawberry.fastapi import GraphQLRouter

from windchimes_backend.graphql_api.strawberry_graphql_setup.context import (
    GraphQLRequestContext,
)
from windchimes_backend.graphql_api.queries.example import example_query
from windchimes_backend.graphql_api.queries.playlists import (
    playlists_query,
    playlist_query,
)
from windchimes_backend.graphql_api.mutations.example_create import (
    create_example_mutation,
)


@strawberry.type
class Query:
    example = example_query
    playlists = playlists_query
    playlist = playlist_query


@strawberry.type
class Mutation:
    create_example = create_example_mutation


__schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(__schema, context_getter=GraphQLRequestContext)
