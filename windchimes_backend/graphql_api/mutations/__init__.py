import strawberry

from windchimes_backend.graphql_api.mutations.playlists import (
    create_playlist_mutation,
    delete_playlist_mutation,
    update_playlist_mutation,
)


@strawberry.type
class Mutation:
    create_playlist = create_playlist_mutation
    delete_playlist = delete_playlist_mutation
    update_playlist = update_playlist_mutation
