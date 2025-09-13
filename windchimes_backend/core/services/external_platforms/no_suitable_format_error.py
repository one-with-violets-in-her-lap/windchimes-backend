class NoSuitableFormatError(Exception):
    def __init__(self):
        super().__init__("couldn't find suitable audio format (mp3)")
