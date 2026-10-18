from unittest.mock import patch

import pytest
from botocore.exceptions import ProfileNotFound

from castoria.common.clients.s3_client import create_s3_client


@pytest.mark.parametrize("profile", ["development", "production"])
def test_explicit_profile(profile: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CASTORIA_AWS_PROFILE", profile)
    with patch("castoria.common.clients.s3_client.boto3.Session") as session_factory:
        client = create_s3_client()
    session_factory.assert_called_once_with(profile_name=profile)
    session_factory.return_value.client.assert_called_once_with("s3")
    assert client is session_factory.return_value.client.return_value


@pytest.mark.parametrize("profile", [None, ""])
def test_default_credential_chain(profile: str | None, monkeypatch: pytest.MonkeyPatch) -> None:
    if profile is None:
        monkeypatch.delenv("CASTORIA_AWS_PROFILE", raising=False)
    else:
        monkeypatch.setenv("CASTORIA_AWS_PROFILE", profile)
    with patch("castoria.common.clients.s3_client.boto3.Session") as session_factory:
        create_s3_client()
    session_factory.assert_called_once_with(profile_name=None)


def test_missing_explicit_profile_does_not_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CASTORIA_AWS_PROFILE", "missing")
    with (
        patch(
            "castoria.common.clients.s3_client.boto3.Session", side_effect=ProfileNotFound(profile="missing")
        ) as factory,
        pytest.raises(ProfileNotFound),
    ):
        create_s3_client()
    factory.assert_called_once_with(profile_name="missing")
