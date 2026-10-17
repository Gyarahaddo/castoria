from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal

from castoria.common.clients.dropbox_client import DropboxClient
from castoria.common.exceptions import CastoriaError
from castoria.common.storage.dropbox import DropboxStorageProvider
from castoria.common.storage.local import LocalStorageProvider
from castoria.common.storage.models import StorageProvider
from castoria.common.storage.s3 import S3StorageProvider

type StorageType = Literal["local", "s3", "dropbox"]


class StorageProviderFactory:
    @staticmethod
    @contextmanager
    def open(storage_type: str) -> Iterator[StorageProvider]:
        """Create a storage provider and release owned resources on exit."""
        provider = StorageProviderFactory.create(storage_type)
        try:
            yield provider
        finally:
            if isinstance(provider, DropboxStorageProvider):
                provider.close()

    @staticmethod
    def create(storage_type: str) -> StorageProvider:
        match storage_type:
            case "local":
                return LocalStorageProvider()

            case "s3":
                return S3StorageProvider()

            case "dropbox":
                return DropboxStorageProvider(DropboxClient())

            case _:
                raise CastoriaError(
                    "STORAGE_UNSUPPORTED_PROVIDER",
                    f"Unsupported storage provider: {storage_type}",
                )
