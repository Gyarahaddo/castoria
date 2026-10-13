import shutil
from pathlib import Path

from castoria.common.exceptions import CastoriaError


class LocalStorageProvider:
    def save(
        self,
        source: Path,
        destination: str,
        name: str,
    ) -> str:
        if not source.is_file():
            raise CastoriaError(
                "STORAGE_SOURCE_NOT_FOUND",
                f"Source file not found: {source}",
            )

        if not name or name in {".", ".."} or "/" in name or "\\" in name:
            raise CastoriaError(
                "STORAGE_INVALID_FILENAME",
                f"Invalid destination filename: {name}",
            )

        target_dir = Path(destination).expanduser()

        if not target_dir.is_dir():
            raise CastoriaError(
                "STORAGE_INVALID_DIRECTORY",
                f"Destination directory does not exist: {target_dir}",
            )

        target = target_dir / f"{name}{source.suffix}"

        try:
            with source.open("rb") as src, target.open("xb") as dst:
                shutil.copyfileobj(src, dst)

        except FileExistsError as error:
            raise CastoriaError(
                "STORAGE_OUTPUT_EXISTS",
                f"Destination file already exists: {target}",
            ) from error

        except OSError as error:
            raise CastoriaError(
                "STORAGE_SAVE_FAILED",
                f"Failed to save file: {error}",
            ) from error

        return str(target.resolve())
