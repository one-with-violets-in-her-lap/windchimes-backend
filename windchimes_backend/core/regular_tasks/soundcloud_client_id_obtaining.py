import logging

import aiohttp

from windchimes_backend.core.stores.soundcloud_api_client_id_store import (
    set_soundcloud_api_client_id,
)


MOBILE_SOUNDCLOUD_WEBSITE_URL = "https://m.soundcloud.com"
CLIENT_ID_OCCURRENCES = ['"clientId":"']


logger = logging.getLogger(__name__)


async def obtain_soundcloud_client_id():
    logger.info("Fetching soundcloud client id: sending http request to main page")

    async with aiohttp.ClientSession(
        base_url=MOBILE_SOUNDCLOUD_WEBSITE_URL
    ) as aiohttp_session:
        async with aiohttp_session.get("/") as response:
            if not response.ok:
                logger.error(
                    "Failed to fetch soundcloud client. Their mobile website page "
                    + 'request failed with status code "%s"',
                    response.status,
                )

            page_html = await response.text()

            for occurrence in CLIENT_ID_OCCURRENCES:
                # Going through each possible occurrence text (for now only one
                # `"client_id":` works) it searches this json property:
                # `clientId: "CLIENT_ID"`. Then it removes the name of the
                # property (`clientId`) and syntax garbage (quotes, colon)

                try:
                    client_id_occurrence_start = page_html.index(occurrence)

                    client_id_start = client_id_occurrence_start + len(occurrence)

                    client_id = page_html[
                        client_id_start : page_html.index('"', client_id_start)
                    ]

                    logger.info(
                        "Successfully scraped the soundcloud client id: %s", client_id
                    )

                    set_soundcloud_api_client_id(client_id)

                    # Finishes execution after client id was found
                    return
                except ValueError:
                    continue

            # If in all possible locations the client id could not be found,
            # logs and error

            logger.error(
                "Couldn't find the soundcloud client id in their mobile website's "
                + "html code"
            )
