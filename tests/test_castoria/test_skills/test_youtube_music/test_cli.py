import argparse
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from castoria.common.exceptions import CastoriaError
from castoria.skills.youtube_music.cli import handle_download
from castoria.skills.youtube_music.models import DownloadResult


@pytest.fixture
def args(tmp_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        link="https://example.com/watch?v=video123",
        format="m4a",
        storage="local",
        dest=str(tmp_path),
        name="saved-audio",
        verbose=False,
    )


def test_handle_download_success(
    args: argparse.Namespace, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_download(url: str, workdir: Path, prefer_m4a: bool) -> DownloadResult:
        source = workdir / "video123.m4a"
        source.write_bytes(b"audio")
        return DownloadResult(title="Test song", video_id="video123", format="m4a", file_path=source)

    downloader = MagicMock()
    downloader.download.side_effect = fake_download
    monkeypatch.setattr("castoria.skills.youtube_music.cli.YouTubeAudioDownloader", lambda: downloader)

    status = handle_download(args)
    response = json.loads(capsys.readouterr().out)

    assert status == 0
    assert response["success"] is True
    assert response["data"]["format"] == "m4a"
    assert response["data"]["destination"] == str((tmp_path / "saved-audio.m4a").resolve())
    assert (tmp_path / "saved-audio.m4a").read_bytes() == b"audio"
    downloader.convert.assert_not_called()


def test_handle_download_converts_mismatched_format(
    args: argparse.Namespace, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_download(url: str, workdir: Path, prefer_m4a: bool) -> DownloadResult:
        source = workdir / "video123.webm"
        source.write_bytes(b"webm")
        return DownloadResult(title="Test song", video_id="video123", format="webm", file_path=source)

    def fake_convert(source: Path, target_format: str) -> Path:
        assert target_format == "m4a"
        output = source.with_suffix(".m4a")
        output.write_bytes(b"aac")
        return output

    downloader = MagicMock()
    downloader.download.side_effect = fake_download
    downloader.convert.side_effect = fake_convert
    monkeypatch.setattr("castoria.skills.youtube_music.cli.YouTubeAudioDownloader", lambda: downloader)

    status = handle_download(args)
    response = json.loads(capsys.readouterr().out)

    assert status == 0
    assert response["data"]["format"] == "m4a"
    assert (tmp_path / "saved-audio.m4a").read_bytes() == b"aac"
    downloader.convert.assert_called_once()


def test_handle_download_returns_structured_storage_error(
    args: argparse.Namespace, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_download(url: str, workdir: Path, prefer_m4a: bool) -> DownloadResult:
        source = workdir / "video123.m4a"
        source.write_bytes(b"audio")
        return DownloadResult(title="Test song", video_id="video123", format="m4a", file_path=source)

    downloader = MagicMock()
    downloader.download.side_effect = fake_download
    monkeypatch.setattr("castoria.skills.youtube_music.cli.YouTubeAudioDownloader", lambda: downloader)
    args.storage = "unknown"

    status = handle_download(args)
    response = json.loads(capsys.readouterr().out)

    assert status == 1
    assert response == {
        "success": False,
        "error": {
            "code": "STORAGE_UNSUPPORTED_PROVIDER",
            "message": "Unsupported storage provider: unknown",
            "retryable": False,
        },
    }


def test_handle_download_returns_structured_download_error(
    args: argparse.Namespace, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    downloader = MagicMock()
    downloader.download.side_effect = CastoriaError("DOWNLOAD_YTDLP_FAILED", "failed")
    monkeypatch.setattr("castoria.skills.youtube_music.cli.YouTubeAudioDownloader", lambda: downloader)

    status = handle_download(args)
    response = json.loads(capsys.readouterr().out)

    assert status == 1
    assert response["success"] is False
    assert response["error"]["code"] == "DOWNLOAD_YTDLP_FAILED"
    assert response["error"]["retryable"] is False
