import base64
import json
import logging
from typing import Optional

import aiohttp
from pydantic import BaseModel

from windchimes_backend.utils.dictionaries import convert_keys_to_snake_case


_IMAGEKIT_API_BASE_URL = "https://upload.imagekit.io"


logger = logging.getLogger(__name__)


class ImagekitApiError(Exception):
    def __init__(self, explanation: str, status_code: Optional[int] = None) -> None:
        error_message = explanation
        if status_code is not None:
            error_message = f"Status code: {status_code}. {error_message}"

        self.status_code = status_code

        super().__init__(error_message)


class ImagekitUploadResponse(BaseModel):
    file_id: str
    file_path: str
    url: str


class ImagekitApiClient:
    def __init__(self, private_key: str):
        self.encoded_private_key = base64.b64encode(
            (private_key + ":").encode()
        ).decode("utf-8")

    async def upload_image(
        self,
        image_data: bytes,
        filename: str,
        folder="/",
        append_unique_suffix_to_filename=True,
    ):
        """Uploads an image to an external storage via Imagekit

        Raises:
            ImagekitApiError: if there is an error in API response (upload failed)
        """

        form_data = {
            "file": image_data,
            "fileName": filename,
            "folder": folder,
            "useUniqueFileName": str(append_unique_suffix_to_filename).lower(),
        }

        async with aiohttp.ClientSession(
            base_url=_IMAGEKIT_API_BASE_URL,
            headers={"Authorization": f"Basic {self.encoded_private_key}"},
        ) as aiohttp_session:
            async with aiohttp_session.post(
                "/api/v1/files/upload", data=form_data
            ) as response:
                try:
                    response_data = await response.json()
                except json.JSONDecodeError as error:
                    raise ImagekitApiError(
                        await response.text(), response.status
                    ) from error

                if response.status == 400:
                    logger.error(
                        "Invalid image uploaded. More info: %s",
                        response_data["message"],
                    )
                    raise ImagekitApiError(
                        f"Invalid image uploaded. More info: {response_data['message']}",
                        400,
                    )
                elif not response.ok:
                    logger.error(
                        "Image upload failed with status code %s", response.status
                    )

                    raise ImagekitApiError(
                        "Unexpected error occurred when uploading the image",
                        response.status,
                    )
                else:
                    response_data = convert_keys_to_snake_case(response_data)
                    return ImagekitUploadResponse.model_validate(response_data)
