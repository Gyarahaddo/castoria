import shutil
import subprocess
from pathlib import Path
from typing import Literal

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from castoria.common.exceptions import CastoriaError
from castoria.skills.youtube_music.models import DownloadResult

type AudioFormat = Literal["m4a", "original"]


class YouTubeAudioDownloader:
    def download(
        self,
        url: str,
        workdir: Path,
        prefer_m4a: bool = True,
    ) -> DownloadResult:
        """Download the best available audio without conversion."""
        if not workdir.is_dir():
            raise CastoriaError(
                "DOWNLOAD_INVALID_DIRECTORY",
                f"Working directory does not exist: {workdir}",
            )

        options = {
            "format": "bestaudio[ext=m4a]/bestaudio" if prefer_m4a else "bestaudio",
            "outtmpl": str(workdir / "%(id)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "overwrites": False,
        }

        try:
            with YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)

        except DownloadError as error:
            raise CastoriaError(
                "DOWNLOAD_YTDLP_FAILED",
                str(error),
            ) from error

        video_id = str(info["id"])
        title = str(info.get("title", video_id))

        # Locate the downloaded audio file.
        audio_files = [
            path
            for path in workdir.glob(f"{video_id}.*")
            if path.is_file() and not path.name.endswith((".part", ".ytdl"))
        ]

        if not audio_files:
            raise CastoriaError(
                "DOWNLOAD_OUTPUT_MISSING",
                f"Downloaded audio file not found for video: {video_id}",
                retryable=True,
            )

        if len(audio_files) != 1:
            raise CastoriaError(
                "DOWNLOAD_OUTPUT_MISSING",
                f"Expected one downloaded audio file for video: {video_id}",
            )

        audio_path = audio_files[0]

        return DownloadResult(
            title=title,
            video_id=video_id,
            file_path=audio_path,
            format=audio_path.suffix.removeprefix("."),
        )

    def convert(
        self,
        source: Path,
        target_format: str = "m4a",
    ) -> Path:
        """Convert an existing audio file to the requested format."""

        if target_format != "m4a":
            raise CastoriaError(
                "CONVERT_UNSUPPORTED_FORMAT",
                f"Unsupported audio format: {target_format}",
            )

        if not source.is_file():
            raise CastoriaError(
                "CONVERT_SOURCE_NOT_FOUND",
                f"Source audio file not found: {source}",
            )

        destination = source.with_suffix(f".{target_format}")

        if destination.exists():
            raise CastoriaError(
                "CONVERT_OUTPUT_EXISTS",
                f"Destination file already exists: {destination}",
            )

        ffmpeg = shutil.which("ffmpeg")

        if ffmpeg is None:
            raise CastoriaError(
                "CONVERT_DEPENDENCY_MISSING",
                "FFmpeg is required for audio conversion.",
            )

        try:
            subprocess.run(
                [
                    ffmpeg,
                    "-nostdin",
                    "-n",
                    "-i",
                    str(source),
                    "-vn",
                    "-c:a",
                    "aac",
                    str(destination),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        except subprocess.CalledProcessError as error:
            raise CastoriaError(
                "CONVERT_FAILED",
                f"FFmpeg conversion failed: {error.stderr.strip()}",
            ) from error

        except OSError as error:
            raise CastoriaError(
                "CONVERT_FAILED",
                f"Unable to execute FFmpeg: {error}",
            ) from error

        if not destination.is_file():
            raise CastoriaError(
                "CONVERT_OUTPUT_MISSING",
                f"Converted audio file not found: {destination}",
            )

        return destination
