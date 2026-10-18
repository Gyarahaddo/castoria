from pathlib import Path

import pytest

from castoria.common.exceptions import CastoriaError
from castoria.common.storage.local import LocalStorageProvider


@pytest.fixture
def provider() -> LocalStorageProvider:
    return LocalStorageProvider()


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "audio.webm"
    path.write_bytes(b"test audio")
    return path


def test_save_copies_file_and_returns_absolute_path(
    provider: LocalStorageProvider, source: Path, tmp_path: Path
) -> None:
    destination = tmp_path / "output"
    destination.mkdir()

    result = provider.save(source, str(destination), "recording")

    assert result == str((destination / "recording.webm").resolve())
    assert Path(result).read_bytes() == b"test audio"
    assert source.read_bytes() == b"test audio"


def test_save_does_not_overwrite(provider: LocalStorageProvider, source: Path, tmp_path: Path) -> None:
    target = tmp_path / "recording.webm"
    target.write_bytes(b"existing")

    with pytest.raises(CastoriaError) as exc:
        provider.save(source, str(tmp_path), "recording")

    assert exc.value.code == "STORAGE_OUTPUT_EXISTS"
    assert exc.value.retryable is False
    assert target.read_bytes() == b"existing"


@pytest.mark.parametrize("name", ["", ".", "..", "../escape", "a/b", r"a\\b"])
def test_save_rejects_invalid_name(provider: LocalStorageProvider, source: Path, tmp_path: Path, name: str) -> None:
    with pytest.raises(CastoriaError) as exc:
        provider.save(source, str(tmp_path), name)

    assert exc.value.code == "STORAGE_INVALID_FILENAME"


def test_save_rejects_missing_source(provider: LocalStorageProvider, tmp_path: Path) -> None:
    with pytest.raises(CastoriaError) as exc:
        provider.save(tmp_path / "missing.webm", str(tmp_path), "audio")

    assert exc.value.code == "STORAGE_SOURCE_NOT_FOUND"


def test_save_rejects_missing_destination(provider: LocalStorageProvider, source: Path, tmp_path: Path) -> None:
    with pytest.raises(CastoriaError) as exc:
        provider.save(source, str(tmp_path / "missing"), "audio")

    assert exc.value.code == "STORAGE_INVALID_DIRECTORY"
