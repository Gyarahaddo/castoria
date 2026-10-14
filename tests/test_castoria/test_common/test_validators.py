import pytest

from castoria.common.validators import is_valid_s3_url, is_valid_youtube_url


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


@pytest.mark.parametrize(
    "url",
    [
        "s3://my-bucket",
        "s3://my-bucket/",
        "s3://my-bucket/audio/song.m4a",
        "s3://bucket.with.dots/folder/file.mp3",
        "s3://abc",
    ],
)
def test_valid_s3_urls(url: str) -> None:
    assert is_valid_s3_url(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "https://s3.amazonaws.com/my-bucket/key",
        "s3://",
        "s3://ab/key",
        "s3://MyBucket/key",
        "s3://bucket_name/key",
        "s3://bucket..name/key",
        "s3://bucket.-name/key",
        "s3://192.168.1.1/key",
        "s3://user:password@my-bucket/key",
        "s3://my-bucket/key?versionId=123",
        "s3://my-bucket/key#fragment",
        "s3://[invalid/key",
    ],
)
def test_invalid_s3_urls(url: str) -> None:
    assert is_valid_s3_url(url) is False
