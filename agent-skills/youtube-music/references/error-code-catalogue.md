# Error Code Catalogue

Reference for error codes returned by Castoria's `youtube-music download` command.

## Download errors

| Code | Meaning |
| --- | --- |
| `DOWNLOAD_INVALID_URL` | Input is not an accepted YouTube URL. |
| `DOWNLOAD_INVALID_DIRECTORY` | Download working directory does not exist. |
| `DOWNLOAD_YTDLP_FAILED` | yt-dlp reported a download failure. |
| `DOWNLOAD_OUTPUT_MISSING` | No downloaded audio file was found, or more than one matching audio file was found. |

## Conversion errors

| Code | Meaning |
| --- | --- |
| `CONVERT_UNSUPPORTED_FORMAT` | Requested conversion format is unsupported. |
| `CONVERT_SOURCE_NOT_FOUND` | Source audio file does not exist. |
| `CONVERT_OUTPUT_EXISTS` | Converted output already exists; Castoria will not overwrite it. |
| `CONVERT_DEPENDENCY_MISSING` | FFmpeg executable was not found. |
| `CONVERT_FAILED` | FFmpeg returned an error or could not be executed. |
| `CONVERT_OUTPUT_MISSING` | FFmpeg finished without producing the expected output file. |

## Storage errors

| Code | Meaning |
| --- | --- |
| `STORAGE_SOURCE_NOT_FOUND` | Source file to store does not exist. |
| `STORAGE_INVALID_FILENAME` | Output filename stem is empty, `.`, `..`, or contains a path separator. |
| `STORAGE_INVALID_DIRECTORY` | Local destination directory does not exist. |
| `STORAGE_INVALID_DESTINATION` | Invalid S3 URI or Dropbox destination path, or a Dropbox path is not a directory. |
| `STORAGE_OUTPUT_EXISTS` | Destination file or object already exists; overwrite is prohibited. |
| `STORAGE_SAVE_FAILED` | Local file I/O failed while saving or reading the source. |
| `STORAGE_UNSUPPORTED_PROVIDER` | Requested storage provider is not supported. |
| `STORAGE_AWS_PROFILE_NOT_FOUND` | Configured AWS profile was not found. |
| `STORAGE_AUTH_FAILED` | AWS credentials are missing or incomplete, or Dropbox authentication failed. |
| `STORAGE_ACCESS_DENIED` | S3 returned an access-denied error. |
| `STORAGE_ACCESS_FAILED` | Unable to access a Dropbox directory. |
| `STORAGE_CREATE_DIRECTORY_FAILED` | Unable to create a Dropbox directory. |
| `STORAGE_UPLOAD_FAILED` | S3 or Dropbox upload failed. |

## CLI errors

| Code | Meaning |
| --- | --- |
| `INTERNAL_ERROR` | An unexpected exception was caught by the command handler. |

## Retry eligibility

Only `DOWNLOAD_OUTPUT_MISSING` permits a retry, and only when the actual CLI response has `error.retryable: true` (no downloaded audio file was found). Follow the retry limits in `SKILL.md`.

## Maintenance

Update this catalogue when adding, removing, or changing error codes. The actual CLI response determines whether an error is retryable.
