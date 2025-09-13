from windchimes_backend.core.config import app_config


_soundcloud_api_client_id = app_config.soundcloud_api.fallback_client_id
"""Variables stores API key to use for Soundcloud API access

It's utilized as `client_id` param for `SoundcloudApiClient` 

Scraped from soundcloud website regularly (check
`windchimes_backend.core.regular_tasks.soundcloud_client_id_obtaining`
module)
"""


def get_soundcloud_api_client_id():
    """Gets current value of soundcloud client id that is scraped regularly"""
    return _soundcloud_api_client_id


def set_soundcloud_api_client_id(new_client_id: str):
    global _soundcloud_api_client_id
    _soundcloud_api_client_id = new_client_id
