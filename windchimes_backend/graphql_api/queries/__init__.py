import strawberry

from windchimes_backend.graphql_api.queries.playlists.playlists_query import (
    playlists_query,
)
from windchimes_backend.graphql_api.queries.playlists.one_playlist_query import (
    playlist_query,
)
from windchimes_backend.graphql_api.queries.tracks.track_audio_file_query import (
    track_audio_file_query,
)
from windchimes_backend.graphql_api.queries.tracks.loaded_tracks_queries import (
    loaded_tracks_query,
    one_loaded_track_query,
)


@strawberry.type
class Query:
    playlists = playlists_query
    playlist = playlist_query

    track_audio_file = track_audio_file_query
    loaded_tracks = loaded_tracks_query
    loaded_track = one_loaded_track_query
