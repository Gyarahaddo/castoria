from __future__ import annotations

from pathlib import Path, PurePosixPath

from dropbox.exceptions import ApiError, AuthError, BadInputError  # pyright: ignore[reportMissingTypeStubs]
from dropbox.files import FolderMetadata, WriteMode  # pyright: ignore[reportMissingTypeStubs]

from castoria.common.clients.dropbox_client import DropboxClient
from castoria.common.exceptions import CastoriaError


class DropboxStorageProvider:
    def __init__(self, client: DropboxClient) -> None:
        self._client: DropboxClient = client

    @staticmethod
    def _normalize_directory(destination: str) -> str:
        """Validate and normalize a Dropbox App Folder path."""
        if not destination.startswith("/"):
            raise CastoriaError(
                code="STORAGE_INVALID_DESTINATION",
                message="Dropbox destination must start with '/'.",
            )

        parts = destination.split("/")

        if any(part in (".", "..") for part in parts):
            raise CastoriaError(
                code="STORAGE_INVALID_DESTINATION",
                message="Dropbox destination cannot contain '.' or '..'.",
            )

        return "/" + "/".join(part for part in parts if part)

    def _ensure_directory(self, directory: str) -> None:
        """Create missing Dropbox directories recursively."""
        if directory == "/":
            return

        current = ""

        for part in PurePosixPath(directory).parts:
            if part == "/":
                continue

            current += f"/{part}"

            try:
                # Dropbox SDK incorrectly annotates files_get_metadata() as returning None.
                # The actual return type is Metadata (FileMetadata or FolderMetadata).
                metadata = self._client.client.files_get_metadata(current)

                if not isinstance(metadata, FolderMetadata):  # pyright: ignore[reportUnnecessaryIsInstance]
                    raise CastoriaError(
                        code="STORAGE_INVALID_DESTINATION",
                        message=f"Dropbox path is not a directory: {current}",
                    )

            except ApiError as error:
                if not (error.error.is_path() and error.error.get_path().is_not_found()):
                    raise CastoriaError(
                        code="STORAGE_ACCESS_FAILED",
                        message=f"Unable to access Dropbox directory: {current}",
                    ) from error

                try:
                    self._client.client.files_create_folder_v2(current)

                except ApiError as create_error:
                    # Another process may have created the folder.
                    try:
                        metadata = self._client.client.files_get_metadata(current)

                        if isinstance(metadata, FolderMetadata):  # pyright: ignore[reportUnnecessaryIsInstance]
                            continue

                    except ApiError:
                        pass

                    raise CastoriaError(
                        code="STORAGE_CREATE_DIRECTORY_FAILED",
                        message=f"Unable to create Dropbox directory: {current}",
                    ) from create_error

    def save(
        self,
        source: Path,
        destination: str,
        name: str,
    ) -> str:
        """Save a local file to Dropbox without overwriting existing files."""
        if not source.is_file():
            raise CastoriaError(
                code="STORAGE_SOURCE_NOT_FOUND",
                message=f"Source file not found: {source}",
            )

        if not name or name in {".", ".."} or "/" in name or "\\" in name:
            raise CastoriaError(
                "STORAGE_INVALID_FILENAME",
                f"Invalid destination filename: {name}",
            )

        directory = self._normalize_directory(destination)
        target = f"{directory.rstrip('/')}/{name}"

        try:
            self._ensure_directory(directory)

            with source.open("rb") as file:
                metadata = self._client.client.files_upload(
                    file.read(),
                    target,
                    mode=WriteMode.add,
                    autorename=False,
                    strict_conflict=True,
                )

            # Dropbox SDK has incomplete type annotations for path_display.
            path = metadata.path_display  # pyright: ignore[reportAttributeAccessIssue, reportUnknownVariableType]
            return path if isinstance(path, str) and path else target

        except AuthError as error:
            raise CastoriaError(
                code="STORAGE_AUTH_FAILED",
                message="Dropbox authentication failed.",
            ) from error

        except BadInputError as error:
            raise CastoriaError(
                code="STORAGE_INVALID_DESTINATION",
                message=f"Invalid Dropbox destination: {target}",
            ) from error

        except ApiError as error:
            if error.error.is_path() and error.error.get_path().is_conflict():
                raise CastoriaError(
                    code="STORAGE_OUTPUT_EXISTS",
                    message=f"Destination already exists: {target}",
                ) from error

            raise CastoriaError(
                code="STORAGE_UPLOAD_FAILED",
                message=f"Dropbox upload failed: {target}",
            ) from error
