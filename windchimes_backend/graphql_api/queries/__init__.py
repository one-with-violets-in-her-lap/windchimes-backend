import strawberry

from windchimes_backend.graphql_api.queries.playlists.playlists_query import (
    playlists_query,
)
from windchimes_backend.graphql_api.queries.playlists.one_playlist_query import (
    playlist_query,
)


@strawberry.type
class Query:
    playlists = playlists_query
    playlist = playlist_query
