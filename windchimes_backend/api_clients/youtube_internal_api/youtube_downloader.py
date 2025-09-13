import asyncio
import json
import logging

from pydantic import BaseModel, ValidationError


class YtDlpVideoInfoOutput(BaseModel):
    class YtDlpFormat(BaseModel):
        url: str
        audio_ext: str

    requested_formats: list[YtDlpFormat]


logger = logging.getLogger()


class YoutubeDownloader:
    """Wrapper for yt-dlp command line tool"""

    async def get_audio_download_url(self, video_url: str):
        """
        Utilizes yt-dlp command line as subprocess to get url to download the
        youtube video. Formats with audio are prioritized
        """

        try:
            yt_dlp_process = await asyncio.create_subprocess_exec(
                "yt-dlp",
                video_url,
                "-j",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
            )

            yt_dlp_process_output = await yt_dlp_process.communicate()

            yt_dlp_output = yt_dlp_process_output[0].decode(encoding="utf-8")

            if len(yt_dlp_output) == "":
                return None

            logger.info(
                "yt-dlp finished execution. Stdout: %s, stderr: %s",
                yt_dlp_process_output[0],
                yt_dlp_process_output[1],
            )

            yt_dlp_output_dict = json.loads(yt_dlp_output)

            yt_dlp_video_info = YtDlpVideoInfoOutput.model_validate(yt_dlp_output_dict)

            suitable_formats_download_urls = [
                format.url
                for format in yt_dlp_video_info.requested_formats
                if format.audio_ext != "none"
            ]

            if len(suitable_formats_download_urls) == 0:
                return None

            return suitable_formats_download_urls[0]
        except (json.JSONDecodeError, ValidationError) as error:
            logger.error(error)
            return None
