import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from yt_dlp.utils import DownloadError

from castoria.common.exceptions import CastoriaError
from castoria.skills.youtube_music.downloader import YouTubeAudioDownloader


def test_download_rejects_missing_workdir(tmp_path: Path) -> None:
    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().download("https://www.youtube.com/watch?v=video123", tmp_path / "missing")

    assert exc.value.code == "DOWNLOAD_INVALID_DIRECTORY"


def test_download_returns_downloaded_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio = tmp_path / "video123.webm"
    audio.write_bytes(b"audio")
    context = MagicMock()
    context.__enter__.return_value.extract_info.return_value = {
        "id": "video123",
        "title": "Test song",
    }
    factory = MagicMock(return_value=context)
    monkeypatch.setattr("castoria.skills.youtube_music.downloader.YoutubeDL", factory)

    result = YouTubeAudioDownloader().download("https://www.youtube.com/watch?v=video123", tmp_path)

    assert result.title == "Test song"
    assert result.video_id == "video123"
    assert result.format == "webm"
    assert result.file_path == audio
    assert factory.call_args.args[0]["noplaylist"] is True


def test_download_missing_output_is_retryable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    context = MagicMock()
    context.__enter__.return_value.extract_info.return_value = {"id": "video123"}
    monkeypatch.setattr(
        "castoria.skills.youtube_music.downloader.YoutubeDL",
        MagicMock(return_value=context),
    )

    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().download("https://www.youtube.com/watch?v=video123", tmp_path)

    assert exc.value.code == "DOWNLOAD_OUTPUT_MISSING"
    assert exc.value.retryable is True


def test_download_wraps_ytdlp_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    context = MagicMock()
    context.__enter__.return_value.extract_info.side_effect = DownloadError("failed")
    monkeypatch.setattr(
        "castoria.skills.youtube_music.downloader.YoutubeDL",
        MagicMock(return_value=context),
    )

    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().download("https://www.youtube.com/watch?v=video123", tmp_path)

    assert exc.value.code == "DOWNLOAD_YTDLP_FAILED"


def test_convert_rejects_unsupported_format(tmp_path: Path) -> None:
    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().convert(tmp_path / "missing.webm", "mp3")

    assert exc.value.code == "CONVERT_UNSUPPORTED_FORMAT"


def test_convert_rejects_missing_source(tmp_path: Path) -> None:
    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().convert(tmp_path / "missing.webm")

    assert exc.value.code == "CONVERT_SOURCE_NOT_FOUND"


def test_convert_requires_ffmpeg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "song.webm"
    source.write_bytes(b"audio")
    monkeypatch.setattr("castoria.skills.youtube_music.downloader.shutil.which", lambda _: None)

    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().convert(source)

    assert exc.value.code == "CONVERT_DEPENDENCY_MISSING"


def test_convert_rejects_existing_output(tmp_path: Path) -> None:
    source = tmp_path / "song.webm"
    source.write_bytes(b"audio")
    (tmp_path / "song.m4a").write_bytes(b"existing")

    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().convert(source)

    assert exc.value.code == "CONVERT_OUTPUT_EXISTS"


def test_convert_invokes_ffmpeg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "song.webm"
    source.write_bytes(b"audio")
    monkeypatch.setattr("castoria.skills.youtube_music.downloader.shutil.which", lambda _: "/usr/bin/ffmpeg")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command[0] == "/usr/bin/ffmpeg"
        assert "-n" in command
        assert command[-1] == str(tmp_path / "song.m4a")
        Path(command[-1]).write_bytes(b"converted")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("castoria.skills.youtube_music.downloader.subprocess.run", fake_run)

    result = YouTubeAudioDownloader().convert(source)

    assert result == tmp_path / "song.m4a"
    assert result.read_bytes() == b"converted"


def test_convert_reports_ffmpeg_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "song.webm"
    source.write_bytes(b"audio")
    monkeypatch.setattr("castoria.skills.youtube_music.downloader.shutil.which", lambda _: "/usr/bin/ffmpeg")

    def fail(command: list[str], **kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, command, stderr="conversion error")

    monkeypatch.setattr("castoria.skills.youtube_music.downloader.subprocess.run", fail)

    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().convert(source)

    assert exc.value.code == "CONVERT_FAILED"


def test_download_rejects_invalid_youtube_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    factory = MagicMock()
    monkeypatch.setattr("castoria.skills.youtube_music.downloader.YoutubeDL", factory)

    with pytest.raises(CastoriaError) as exc:
        YouTubeAudioDownloader().download("https://example.com/watch?v=video123", tmp_path)

    assert exc.value.code == "DOWNLOAD_INVALID_URL"
    assert exc.value.retryable is False
    factory.assert_not_called()
