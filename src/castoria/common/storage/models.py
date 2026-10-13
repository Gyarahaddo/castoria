from pathlib import Path
from typing import Protocol


class StorageProvider(Protocol):
    def save(
        self,
        source: Path,
        destination: str,
        name: str,
    ) -> str:
        """Save a file and return its final location."""
        ...
