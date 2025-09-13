import strawberry

from windchimes_backend.graphql_api.queries.playlists import (
    playlists_query,
    playlist_query,
)


@strawberry.type
class Query:
    playlists = playlists_query
    playlist = playlist_query
