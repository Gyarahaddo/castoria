from pathlib import Path
from urllib.parse import urlparse

from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
    ProfileNotFound,
)

from castoria.common.clients.s3_client import create_s3_client
from castoria.common.exceptions import CastoriaError
from castoria.common.validators import is_valid_s3_url


class S3StorageProvider:
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

        if not is_valid_s3_url(destination):
            raise CastoriaError(
                "STORAGE_INVALID_DESTINATION",
                f"Invalid S3 destination: {destination}",
            )

        parsed = urlparse(destination)
        bucket = parsed.netloc
        prefix = parsed.path.strip("/")

        filename = f"{name}{source.suffix}"
        object_key = f"{prefix}/{filename}" if prefix else filename

        try:
            client = create_s3_client()

            with source.open("rb") as file:
                client.put_object(
                    Bucket=bucket,
                    Key=object_key,
                    Body=file,
                    IfNoneMatch="*",
                )

        except ProfileNotFound as error:
            raise CastoriaError(
                "STORAGE_AWS_PROFILE_NOT_FOUND",
                str(error),
            ) from error

        except (NoCredentialsError, PartialCredentialsError) as error:
            raise CastoriaError(
                "STORAGE_AUTH_FAILED",
                str(error),
            ) from error

        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code", "Unknown")
            status_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)

            if status_code == 412 or error_code == "PreconditionFailed":
                raise CastoriaError(
                    "STORAGE_OUTPUT_EXISTS",
                    f"S3 object already exists: s3://{bucket}/{object_key}",
                ) from error

            if error_code in {"AccessDenied", "403"}:
                raise CastoriaError(
                    "STORAGE_ACCESS_DENIED",
                    f"Access denied to S3 object: s3://{bucket}/{object_key}",
                ) from error

            raise CastoriaError(
                "STORAGE_UPLOAD_FAILED",
                f"S3 upload failed: {error}",
            ) from error

        except BotoCoreError as error:
            raise CastoriaError(
                "STORAGE_UPLOAD_FAILED",
                f"S3 upload failed: {error}",
            ) from error

        except OSError as error:
            raise CastoriaError(
                "STORAGE_SAVE_FAILED",
                f"Failed to read source file: {error}",
            ) from error

        return f"s3://{bucket}/{object_key}"
