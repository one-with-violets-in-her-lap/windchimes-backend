import strawberry

from windchimes_backend.graphql_api.mutations.playlists import (
    create_playlist_mutation,
    delete_playlist_mutation,
    update_playlist_mutation,
)
from windchimes_backend.graphql_api.mutations.playlists.playlist_picture_mutations import (
    update_playlist_picture_mutation,
    delete_playlist_picture_mutation
)
from windchimes_backend.graphql_api.mutations.playlists.playlist_tracks import (
    delete_track_from_playlists_mutation,
    add_tracks_to_playlists_mutation,
)
from windchimes_backend.graphql_api.mutations.external_platform_import.tracks_import import (
    import_external_playlist_tracks_mutation,
)


@strawberry.type
class Mutation:
    create_playlist = create_playlist_mutation
    delete_playlist = delete_playlist_mutation
    update_playlist = update_playlist_mutation

    add_tracks_to_playlists = add_tracks_to_playlists_mutation
    delete_track_from_playlists = delete_track_from_playlists_mutation

    update_playlist_picture = update_playlist_picture_mutation
    delete_playlist_picture = delete_playlist_picture_mutation

    import_external_playlist_tracks = import_external_playlist_tracks_mutation
