import ipaddress
import re
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


_S3_BUCKET_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")


def is_valid_s3_url(url: str) -> bool:
    """Validate an S3 URI such as s3://bucket-name/optional/key."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if (
        parsed.scheme != "s3"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return False

    bucket = parsed.netloc
    if (
        not _S3_BUCKET_PATTERN.fullmatch(bucket)
        or ".." in bucket
        or ".-" in bucket
        or "-." in bucket
    ):
        return False

    try:
        ipaddress.IPv4Address(bucket)
    except ipaddress.AddressValueError:
        return True
    return False
