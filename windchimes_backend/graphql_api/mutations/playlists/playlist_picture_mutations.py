import logging
from typing import cast

import strawberry
from fastapi import UploadFile

from windchimes_backend.core.models.user import User
from windchimes_backend.core.services.picture_storage_service import (
    PictureTooLargeError,
    PictureUploadError,
)
from windchimes_backend.core.services.playlists import PlaylistUpdate
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
)
from windchimes_backend.graphql_api.strawberry_graphql_setup.auth import (
    AuthorizedOnlyExtension,
)
from windchimes_backend.graphql_api.utils.graphql import GraphQLRequestInfo


@strawberry.type
class PlaylistNewPicture:
    url: str


logger = logging.getLogger(__name__)

_SUPPORTED_PICTURE_MIME_TYPES = [
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/avif",
    "image/bmp",
]


async def _update_playlist_picture(
    info: GraphQLRequestInfo, playlist_id: int, picture: UploadFile
) -> PlaylistNewPicture | GraphQLApiError:
    current_user = cast(User, info.context.current_user)

    picture_storage_service = info.context.picture_storage_service
    playlists_access_management_service = (
        info.context.playlists_access_management_service
    )
    playlists_service = info.context.playlists_service

    user_owns_the_playlist = (
        await playlists_access_management_service.check_if_user_owns_the_playlists(
            [playlist_id]
        )
    )
    if not user_owns_the_playlist:
        return ForbiddenErrorGraphQL()

    if picture.content_type not in _SUPPORTED_PICTURE_MIME_TYPES:
        return GraphQLApiError(
            name="invalid-file-type-error",
            explanation="Invalid file type",
            technical_explanation=f"Uploaded file mime type `{picture.content_type}` "
            + "is not in the list of supported mime types",
        )

    try:
        picture_data = await picture.read()

        uploaded_picture_url = await picture_storage_service.upload_picture(
            picture_data=picture_data,
            filename=f"playlist_{playlist_id}",
            folder="/playlists",
            append_unique_suffix_to_filename=False,
        )

        await playlists_service.update_playlist(
            playlist_id,
            current_user.sub,
            PlaylistUpdate(picture_url=uploaded_picture_url),
        )

        return PlaylistNewPicture(url=uploaded_picture_url)
    except PictureTooLargeError as error:
        logger.error("%s", error)
        return GraphQLApiError(
            name="picture-too-large-error",
            explanation=str(error),
            technical_explanation=str(error),
        )
    except PictureUploadError as error:
        logger.error("%s", error)
        return GraphQLApiError(
            name="picture-upload-error",
            explanation="Failed to upload the pic",
            technical_explanation=str(error),
        )
    except Exception as error:
        logger.error("%s", error)
        return GraphQLApiError(
            name="picture-upload-error",
            explanation="Failed to upload the pic",
            technical_explanation="Failed to upload the pic",
        )


update_playlist_picture_mutation = strawberry.mutation(
    resolver=_update_playlist_picture, extensions=[AuthorizedOnlyExtension()]
)


async def _delete_playlist_picture(
    info: GraphQLRequestInfo, playlist_id: int
) -> None | GraphQLApiError:
    current_user = cast(User, info.context.current_user)

    playlists_access_management_service = (
        info.context.playlists_access_management_service
    )
    playlists_service = info.context.playlists_service

    user_owns_the_playlist = (
        await playlists_access_management_service.check_if_user_owns_the_playlists(
            [playlist_id]
        )
    )
    if not user_owns_the_playlist:
        return ForbiddenErrorGraphQL()

    await playlists_service.update_playlist(
        playlist_id, current_user.sub, PlaylistUpdate(picture_url=None)
    )


delete_playlist_picture_mutation = strawberry.mutation(
    resolver=_delete_playlist_picture, extensions=[AuthorizedOnlyExtension()]
)
