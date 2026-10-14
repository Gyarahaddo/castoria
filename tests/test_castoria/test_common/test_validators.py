import pytest

from castoria.common.validators import is_valid_youtube_url


@pytest.mark.parametrize(
    "url",
    [
        "https://youtube.com/watch?v=video123",
        "https://www.youtube.com/watch?v=video123",
        "https://m.youtube.com/watch?v=video123",
        "https://music.youtube.com/watch?v=video123",
        "https://youtu.be/video123",
        "https://www.youtube.com/shorts/video123",
    ],
)
def test_valid_youtube_urls(url: str) -> None:
    assert is_valid_youtube_url(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "https://example.com/watch?v=video123",
        "https://youtube.com.evil.com/watch?v=video123",
        "https://evil.com/?redirect=youtube.com",
        "http://www.youtube.com/watch?v=video123",
        "ftp://www.youtube.com/watch?v=video123",
        "https://www.youtube.com:8443/watch?v=video123",
        "https://user:password@www.youtube.com/watch?v=video123",
        "https://www.youtube.com:invalid/watch?v=video123",
        "https://[invalid",
    ],
)
def test_invalid_youtube_urls(url: str) -> None:
    assert is_valid_youtube_url(url) is False
