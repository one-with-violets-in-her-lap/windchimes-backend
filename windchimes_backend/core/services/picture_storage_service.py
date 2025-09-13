from windchimes_backend.api_clients.imagekit_api_client import (
    ImagekitApiClient,
    ImagekitApiError,
)


class PictureUploadError(Exception):
    pass


class PictureStorageService:
    def __init__(self, imagekit_api_client: ImagekitApiClient):
        self.imagekit_api_client = imagekit_api_client

    async def upload_picture(self, picture_data: bytes, filename: str, folder="/"):
        """Uploads an image to an external storage

        Raises:
            PictureUploadError: if upload failed

        Returns:
            Uploaded file path
        """

        try:
            upload_response = await self.imagekit_api_client.upload_image(
                picture_data, filename, folder
            )

            return upload_response.file_path
        except ImagekitApiError as error:
            raise PictureUploadError(
                f"Upload failed. {str(error)}. Status code: {error.status_code or '-'}"
            )
