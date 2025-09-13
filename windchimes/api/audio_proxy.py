import logging
import urllib.parse

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
import httpx

from windchimes.core.config import app_config


audio_proxy_router = APIRouter(prefix="/audio")


logger = logging.getLogger(__name__)


@audio_proxy_router.get("/")
async def fetch_audio_as_proxy(url: str, request: Request):
    """
    Route that acts like a proxy for bypassing CORS when fetching audio files

    Supports only Youtube HLS resources: m3u8 and seg.ts files

    If m3u8 file is passed in `url` param, it fetches it and replaces original segments
    (seg.ts) urls with proxied ones -
    https://youtube.com/seg.ts ->
    https://api.windchimes.com/youtube-hls-audio?url=https%3A//youtube.com/seg.ts
    (pseudo-example)

    If segment (seg.ts) file is passed, it just fetches it and streams it back
    """

    parsed_url = urllib.parse.urlparse(url)

    if parsed_url.hostname is None or not parsed_url.hostname.endswith(
        "googlevideo.com"
    ):
        raise HTTPException(
            status_code=400,
            detail="Url must point to Youtube CDN (googlevideo.com)",
        )

    async with httpx.AsyncClient(proxy=app_config.proxy.url) as client:
        logger.info("Fetching HLS resource: %s. Proxy: %s", url, app_config.proxy.url)

        response = await client.get(
            url,
            headers={
                "Accept": "*/*",
                "Accept-language": "en-US,en;q=0.9",
                "User-Agent": "Mozilla/5.0",
            },
        )

        if response.is_error:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Youtube CDN returned an error: {response.text}",
            )

        content_type = response.headers.get("Content-Type")

        logger.info("Fetched HLS resource, content type: %s", content_type)

        if "application/vnd.apple.mpegurl" in content_type:
            m3u8_data_with_proxied_urls = "\n".join(
                [
                    (
                        str(request.url.include_query_params(url=m3u8_line))
                        if not m3u8_line.startswith("#")
                        else m3u8_line
                    )
                    for m3u8_line in response.text.splitlines()
                ]
            )

            return Response(
                content=m3u8_data_with_proxied_urls,
                media_type="application/vnd.apple.mpegurl",
            )
        elif "application/octet-stream" in content_type:
            return StreamingResponse(
                response.iter_bytes(),
                media_type=content_type,
            )
        else:
            raise HTTPException(
                status_code=500, detail=f"Unexpected content type: {content_type}"
            )
