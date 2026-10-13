from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DownloadResult:
    title: str
    video_id: str
    format: str
    file_path: Path
