class ExternalPlaylistNotFoundError(Exception):
    def __init__(self):
        super().__init__("External playlist with specified url/id cannot be found")


class ExternalPlatformAudioFetchingError(Exception):
    pass
