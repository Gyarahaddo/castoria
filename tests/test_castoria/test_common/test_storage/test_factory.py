import pytest

from castoria.common.exceptions import CastoriaError
from castoria.common.storage.factory import StorageProviderFactory
from castoria.common.storage.local import LocalStorageProvider
from castoria.common.storage.s3 import S3StorageProvider


def test_create_local_provider() -> None:
    assert isinstance(StorageProviderFactory.create("local"), LocalStorageProvider)


def test_create_s3_provider() -> None:
    assert isinstance(StorageProviderFactory.create("s3"), S3StorageProvider)


@pytest.mark.parametrize("provider_name", ["dropbox", "unknown", ""])
def test_create_unsupported_provider(provider_name: str) -> None:
    with pytest.raises(CastoriaError) as exc:
        StorageProviderFactory.create(provider_name)

    assert exc.value.code == "STORAGE_UNSUPPORTED_PROVIDER"
    assert exc.value.retryable is False
