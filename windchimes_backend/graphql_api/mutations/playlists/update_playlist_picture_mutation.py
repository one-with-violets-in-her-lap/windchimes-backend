import strawberry
from fastapi import UploadFile

from windchimes_backend.graphql_api.reusable_schemas.errors import GraphQLApiError
from windchimes_backend.graphql_api.utils.graphql import GraphQLRequestInfo


@strawberry.type
class PlaylistNewPicture:
    url: str


async def _update_playlist_picture(
    info: GraphQLRequestInfo, picture: UploadFile
) -> PlaylistNewPicture | GraphQLApiError:
    picture_storage_service = info.context.picture_storage_service

    try:
        picture_data = await picture.read()

        uploaded_file_path = await picture_storage_service.upload_picture(
            picture_data, "image_534"
        )

        return PlaylistNewPicture(url=uploaded_file_path)
    except Exception as error:
        print(error)
        return GraphQLApiError(
            name="picture-upload-error",
            explanation="Failed to upload the pic",
            technical_explanation="Failed to upload the pic",
        )


update_playlist_picture_mutation = strawberry.mutation(
    resolver=_update_playlist_picture
)
