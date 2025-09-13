import strawberry
from strawberry.fastapi import GraphQLRouter

from windchimes_backend.graphql_api.strawberry_graphql_setup.context import (
    GraphQLRequestContext,
)
from windchimes_backend.graphql_api.queries.playlists import (
    playlists_query,
    playlist_query,
)
from windchimes_backend.graphql_api.mutations.playlists import (
    create_playlist_mutation,
)


@strawberry.type
class Query:
    playlists = playlists_query
    playlist = playlist_query


@strawberry.type
class Mutation:
    create_playlist = create_playlist_mutation


__schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(__schema, context_getter=GraphQLRequestContext)
