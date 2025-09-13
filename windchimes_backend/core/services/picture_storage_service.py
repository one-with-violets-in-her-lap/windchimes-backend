from windchimes_backend.external_api_clients.imagekit_api_client import (
    ImagekitApiClient,
    ImagekitApiError,
)


_MAX_PICTURE_SIZE_IN_BYTES = 3_000_000
_MAX_PICTURE_SIZE_IN_MEGABYTES = _MAX_PICTURE_SIZE_IN_BYTES / 1000 / 1000


class PictureTooLargeError(Exception):
    def __init__(self):
        super().__init__(
            f"File size size must not exceed {_MAX_PICTURE_SIZE_IN_MEGABYTES} MB"
        )


class PictureUploadError(Exception):
    pass


class PictureStorageService:
    def __init__(self, imagekit_api_client: ImagekitApiClient):
        self.imagekit_api_client = imagekit_api_client

    async def upload_picture(
        self,
        picture_data: bytes,
        filename: str,
        folder="/",
        append_unique_suffix_to_filename=True,
    ):
        """Uploads an image to an external storage

        Raises:
            PictureUploadError: if upload failed
            PictureTooLargeError: if picture size exceeds the maximum
                (see `_MAX_PICTURE_SIZE_IN_BYTES` constant)

        Returns:
            Uploaded picture url
        """

        if len(picture_data) > _MAX_PICTURE_SIZE_IN_BYTES:
            raise PictureTooLargeError()

        try:
            upload_response = await self.imagekit_api_client.upload_image(
                picture_data, filename, folder, append_unique_suffix_to_filename
            )

            return upload_response.url
        except ImagekitApiError as error:
            raise PictureUploadError(
                f"Upload failed. {str(error)}. Status code: {error.status_code or '-'}"
            ) from error
