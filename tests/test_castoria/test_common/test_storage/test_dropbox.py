from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dropbox.files import FolderMetadata

from castoria.common.exceptions import CastoriaError
from castoria.common.storage.dropbox import DropboxStorageProvider


@pytest.fixture
def source(tmp_path: Path) -> Path:
    file = tmp_path / "audio.m4a"
    file.write_bytes(b"audio")
    return file


@pytest.fixture
def client() -> MagicMock:
    wrapper = MagicMock()
    wrapper.client.files_upload.return_value.path_display = "/Music/song.m4a"
    return wrapper


def test_save_uploads_without_overwrite(source: Path, client: MagicMock) -> None:
    client.client.files_get_metadata.return_value = MagicMock(spec=FolderMetadata)

    result = DropboxStorageProvider(client).save(source, "/Music", "song")

    assert result == "/Music/song.m4a"
    args, kwargs = client.client.files_upload.call_args
    assert args == (b"audio", "/Music/song.m4a")
    assert kwargs["autorename"] is False
    assert kwargs["strict_conflict"] is True
    assert kwargs["mode"].is_add()


def test_save_at_root(source: Path, client: MagicMock) -> None:
    client.client.files_upload.return_value.path_display = None

    result = DropboxStorageProvider(client).save(source, "/", "song")

    assert result == "/song.m4a"
    client.client.files_get_metadata.assert_not_called()
    client.client.files_upload.assert_called_once()


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", "a\\b"])
def test_invalid_filename(source: Path, client: MagicMock, name: str) -> None:
    with pytest.raises(CastoriaError) as exc:
        DropboxStorageProvider(client).save(source, "/Music", name)

    assert exc.value.code == "STORAGE_INVALID_FILENAME"
    client.client.files_upload.assert_not_called()


@pytest.mark.parametrize("destination", ["Music", "/Music/../Other", "/Music/./Other"])
def test_invalid_destination(source: Path, client: MagicMock, destination: str) -> None:
    with pytest.raises(CastoriaError) as exc:
        DropboxStorageProvider(client).save(source, destination, "song")

    assert exc.value.code == "STORAGE_INVALID_DESTINATION"
    client.client.files_upload.assert_not_called()


def test_missing_source(tmp_path: Path, client: MagicMock) -> None:
    with pytest.raises(CastoriaError) as exc:
        DropboxStorageProvider(client).save(tmp_path / "missing.m4a", "/Music", "song")

    assert exc.value.code == "STORAGE_SOURCE_NOT_FOUND"


def test_existing_file_in_directory_is_rejected(source: Path, client: MagicMock) -> None:
    client.client.files_get_metadata.return_value = object()

    with pytest.raises(CastoriaError) as exc:
        DropboxStorageProvider(client).save(source, "/Music", "song")

    assert exc.value.code == "STORAGE_INVALID_DESTINATION"
    client.client.files_upload.assert_not_called()


def test_source_read_failure(source: Path, client: MagicMock) -> None:
    client.client.files_get_metadata.return_value = MagicMock(spec=FolderMetadata)

    with patch.object(Path, "open", side_effect=PermissionError("denied")):
        with pytest.raises(CastoriaError) as exc:
            DropboxStorageProvider(client).save(source, "/Music", "song")

    assert exc.value.code == "STORAGE_SAVE_FAILED"


def test_context_manager_closes_client(client: MagicMock) -> None:
    with DropboxStorageProvider(client) as provider:
        assert provider._client is client
        client.close.assert_not_called()

    client.close.assert_called_once_with()


def test_context_manager_closes_client_on_exception(client: MagicMock) -> None:
    with pytest.raises(RuntimeError, match="failure"):
        with DropboxStorageProvider(client):
            raise RuntimeError("failure")

    client.close.assert_called_once_with()
