# Error Code Catalogue

Reference for the current error codes emitted by Castoria's `youtube-music download` workflow and its shared storage providers.

**Agent policy:** Consult this file only when the CLI returns `success: false` and `error.retryable: true`. For `retryable: false`, return the CLI error to the user without troubleshooting or retrying. Never treat `retryable: true` as an instruction to retry automatically.

The `retryable` value in the **actual CLI response** is authoritative. Most errors default to `false` because `CastoriaError` defaults to `retryable=False`. The same error code can have different values depending on the failure path.

## Download errors

| Code | Current retryable | Meaning |
| --- | --- | --- |
| `DOWNLOAD_INVALID_URL` | false | Input is not an accepted YouTube URL. |
| `DOWNLOAD_INVALID_DIRECTORY` | false | Download working directory does not exist. |
| `DOWNLOAD_YTDLP_FAILED` | false | yt-dlp reported a download failure. |
| `DOWNLOAD_OUTPUT_MISSING` | true or false | No downloaded audio file was found (true), or more than one matching audio file was found (false). |

## Conversion errors

| Code | Current retryable | Meaning |
| --- | --- | --- |
| `CONVERT_UNSUPPORTED_FORMAT` | false | Requested conversion format is unsupported. |
| `CONVERT_SOURCE_NOT_FOUND` | false | Source audio file does not exist. |
| `CONVERT_OUTPUT_EXISTS` | false | Converted output already exists; Castoria will not overwrite it. |
| `CONVERT_DEPENDENCY_MISSING` | false | FFmpeg executable was not found. |
| `CONVERT_FAILED` | false | FFmpeg returned an error or could not be executed. |
| `CONVERT_OUTPUT_MISSING` | false | FFmpeg finished without producing the expected output file. |

## Storage errors

| Code | Current retryable | Meaning |
| --- | --- | --- |
| `STORAGE_SOURCE_NOT_FOUND` | false | Source file to store does not exist. |
| `STORAGE_INVALID_FILENAME` | false | Output filename stem is empty, `.`, `..`, or contains a path separator. |
| `STORAGE_INVALID_DIRECTORY` | false | Local destination directory does not exist. |
| `STORAGE_INVALID_DESTINATION` | false | S3 destination URI is invalid. |
| `STORAGE_OUTPUT_EXISTS` | false | Local destination file or S3 object already exists; overwrite is prohibited. |
| `STORAGE_SAVE_FAILED` | false | Local file I/O failed while saving or reading the source. |
| `STORAGE_UNSUPPORTED_PROVIDER` | false | Requested storage provider is not implemented (currently Dropbox and unknown providers). |
| `STORAGE_AWS_PROFILE_NOT_FOUND` | false | Configured AWS profile was not found. |
| `STORAGE_AUTH_FAILED` | false | boto3 reported missing or partial AWS credentials. |
| `STORAGE_ACCESS_DENIED` | false | S3 returned an access-denied error. |
| `STORAGE_UPLOAD_FAILED` | false | S3 upload failed for another boto3/botocore error. |

## CLI errors

| Code | Current retryable | Meaning |
| --- | --- | --- |
| `INTERNAL_ERROR` | false | An unexpected exception was caught by the command handler. |

## Retry guidance

### `DOWNLOAD_OUTPUT_MISSING` (only when `retryable: true`)

The downloader did not find an audio file after yt-dlp finished. One limited retry of the **same command** may help if the failure was transient.

1. Retry at most **once**, using the same arguments. Do not change the URL, destination, filename, or authentication settings.
2. If the retry fails, report the returned error to the user; do not attempt further diagnosis or retries.
3. If the retry succeeds, report the saved location from `data.destination`.

Do not retry if the actual response has `retryable: false`. Never bypass YouTube restrictions, overwrite existing outputs, or request secrets.

## Maintenance

Update this catalogue when adding, removing, or changing `CastoriaError` codes, their `retryable` behavior, or the `INTERNAL_ERROR` response. This catalogue reflects the source code at the time of writing; it does not guarantee that external services will behave as described.
