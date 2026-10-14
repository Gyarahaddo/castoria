from urllib.parse import urlparse

_YOUTUBE_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
    }
)


def is_valid_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        return (
            parsed.scheme == "https"
            and parsed.hostname in _YOUTUBE_HOSTS
            and parsed.port is None
            and parsed.username is None
            and parsed.password is None
        )
    except ValueError:
        return False
