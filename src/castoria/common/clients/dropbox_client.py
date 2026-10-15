import os
from typing import Final

import dropbox  # pyright: ignore[reportMissingTypeStubs]


class DropboxClient:
    def __init__(self) -> None:
        app_key = os.getenv("CASTORIA_DROPBOX_APP_KEY")
        app_secret = os.getenv("CASTORIA_DROPBOX_APP_SECRET")
        refresh_token = os.getenv("CASTORIA_DROPBOX_REFRESH_TOKEN")

        if not all((app_key, app_secret, refresh_token)):
            raise ValueError("Dropbox credentials are not configured.")

        self._client: Final[dropbox.Dropbox] = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token,
            app_key=app_key,
            app_secret=app_secret,
        )

    @property
    def client(self) -> dropbox.Dropbox:
        return self._client

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "DropboxClient":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()
