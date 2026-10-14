from typing import Literal

from castoria.common.exceptions import CastoriaError
from castoria.common.storage.local import LocalStorageProvider
from castoria.common.storage.models import StorageProvider
from castoria.common.storage.s3 import S3StorageProvider

type StorageType = Literal["local", "s3", "dropbox"]


class StorageProviderFactory:
    @staticmethod
    def create(storage_type: str) -> StorageProvider:
        match storage_type:
            case "local":
                return LocalStorageProvider()

            case "s3":
                return S3StorageProvider()

            case _:
                raise CastoriaError(
                    "STORAGE_UNSUPPORTED_PROVIDER",
                    f"Unsupported storage provider: {storage_type}",
                )
