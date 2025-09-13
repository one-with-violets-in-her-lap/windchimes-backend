import strawberry

from windchimes_backend.api.queries.playlists.playlists_query import (
    playlists_query,
)
from windchimes_backend.api.queries.playlists.one_playlist_query import (
    playlist_query,
)
from windchimes_backend.api.queries.playlists.external_playlist_query import (
    external_playlist_linked_query,
)
from windchimes_backend.api.queries.tracks.track_audio_file_query import (
    track_audio_file_query,
)
from windchimes_backend.api.queries.tracks.loaded_tracks.queries import (
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

    external_playlist_linked = external_playlist_linked_query
