import strawberry

from windchimes_backend.graphql_api.mutations.playlists import (
    create_playlist_mutation,
    delete_playlist_mutation,
    update_playlist_mutation,
)
from windchimes_backend.graphql_api.mutations.playlists.playlist_tracks import (
    add_tracks_to_playlists_mutation,
)


@strawberry.type
class Mutation:
    create_playlist = create_playlist_mutation
    delete_playlist = delete_playlist_mutation
    update_playlist = update_playlist_mutation
    add_tracks_to_playlists = add_tracks_to_playlists_mutation
