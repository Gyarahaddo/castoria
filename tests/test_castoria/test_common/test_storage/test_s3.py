from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
    ProfileNotFound,
)

from castoria.common.exceptions import CastoriaError
from castoria.common.storage.s3 import S3StorageProvider


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "audio.m4a"
    path.write_bytes(b"audio content")
    return path


@pytest.fixture
def client() -> MagicMock:
    return MagicMock()


def assert_error(exc: pytest.ExceptionInfo[CastoriaError], code: str) -> None:
    assert exc.value.code == code


@pytest.mark.parametrize(
    ("destination", "expected_bucket", "expected_key"),
    [
        ("s3://my-bucket", "my-bucket", "song.m4a"),
        ("s3://my-bucket/", "my-bucket", "song.m4a"),
        ("s3://my-bucket/music", "my-bucket", "music/song.m4a"),
        ("s3://my-bucket/music/2026/", "my-bucket", "music/2026/song.m4a"),
    ],
)
def test_save_uploads_without_overwrite(
    source: Path,
    client: MagicMock,
    destination: str,
    expected_bucket: str,
    expected_key: str,
) -> None:
    with patch("castoria.common.storage.s3.create_s3_client", return_value=client):
        result = S3StorageProvider().save(source, destination, "song")
    assert result == f"s3://{expected_bucket}/{expected_key}"
    client.put_object.assert_called_once()
    kwargs = client.put_object.call_args.kwargs
    assert kwargs["Bucket"] == expected_bucket
    assert kwargs["Key"] == expected_key
    assert kwargs["IfNoneMatch"] == "*"
    assert kwargs["Body"].closed
    assert source.read_bytes() == b"audio content"


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", "a\\b"])
def test_invalid_name(source: Path, name: str) -> None:
    with pytest.raises(CastoriaError) as exc:
        S3StorageProvider().save(source, "s3://my-bucket/music", name)
    assert_error(exc, "STORAGE_INVALID_FILENAME")


@pytest.mark.parametrize(
    "destination", ["https://my-bucket/music", "s3://", "s3://UPPERCASE/music", "s3://my-bucket?x=1"]
)
def test_invalid_destination(source: Path, destination: str) -> None:
    with pytest.raises(CastoriaError) as exc:
        S3StorageProvider().save(source, destination, "song")
    assert_error(exc, "STORAGE_INVALID_DESTINATION")


def test_missing_source(tmp_path: Path) -> None:
    with pytest.raises(CastoriaError) as exc:
        S3StorageProvider().save(tmp_path / "missing.m4a", "s3://my-bucket", "song")
    assert_error(exc, "STORAGE_SOURCE_NOT_FOUND")


def s3_error(code: str, status: int) -> ClientError:
    return ClientError(
        {"Error": {"Code": code, "Message": "test"}, "ResponseMetadata": {"HTTPStatusCode": status}},
        "PutObject",
    )


@pytest.mark.parametrize(
    ("aws_error", "expected_code"),
    [
        (s3_error("PreconditionFailed", 412), "STORAGE_OUTPUT_EXISTS"),
        (s3_error("Unknown", 412), "STORAGE_OUTPUT_EXISTS"),
        (s3_error("AccessDenied", 403), "STORAGE_ACCESS_DENIED"),
        (s3_error("403", 403), "STORAGE_ACCESS_DENIED"),
        (s3_error("InternalError", 500), "STORAGE_UPLOAD_FAILED"),
        (s3_error("ConditionalRequestConflict", 409), "STORAGE_UPLOAD_FAILED"),
        (s3_error("Unknown", 400), "STORAGE_UPLOAD_FAILED"),
        (NoCredentialsError(), "STORAGE_AUTH_FAILED"),
        (PartialCredentialsError(provider="env", cred_var="AWS_SECRET_ACCESS_KEY"), "STORAGE_AUTH_FAILED"),
        (ProfileNotFound(profile="missing"), "STORAGE_AWS_PROFILE_NOT_FOUND"),
        (BotoCoreError(), "STORAGE_UPLOAD_FAILED"),
    ],
)
def test_aws_errors(source: Path, client: MagicMock, aws_error: Exception, expected_code: str) -> None:
    client.put_object.side_effect = aws_error
    with patch("castoria.common.storage.s3.create_s3_client", return_value=client):
        with pytest.raises(CastoriaError) as exc:
            S3StorageProvider().save(source, "s3://my-bucket/music", "song")
    assert_error(exc, expected_code)
    assert exc.value.__cause__ is aws_error


def test_profile_error_during_client_creation(source: Path) -> None:
    error = ProfileNotFound(profile="missing")
    with patch("castoria.common.storage.s3.create_s3_client", side_effect=error):
        with pytest.raises(CastoriaError) as exc:
            S3StorageProvider().save(source, "s3://my-bucket", "song")
    assert_error(exc, "STORAGE_AWS_PROFILE_NOT_FOUND")


def test_source_read_failure(source: Path, client: MagicMock) -> None:
    with (
        patch("castoria.common.storage.s3.create_s3_client", return_value=client),
        patch.object(Path, "open", side_effect=PermissionError("denied")),
        pytest.raises(CastoriaError) as exc,
    ):
        S3StorageProvider().save(source, "s3://my-bucket", "song")
    assert_error(exc, "STORAGE_SAVE_FAILED")
