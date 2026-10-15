---
name: youtube-music
description: Download audio from a single YouTube video using Castoria and save it to local storage, AWS S3, or Dropbox. Use when a user requests YouTube audio downloading or extraction.
---

# YouTube Music

## Usage

Execute the following command:

```bash
castoria youtube-music download \
  --link "<youtube-url>" \
  --storage <provider> \
  --dest "<destination>" \
  [--format <format>] \
  [--name "<filename>"]
```

### Arguments

| Argument | Required | Default | Description |
| --- | --- | --- | --- |
| `--link` | Yes | — | YouTube video URL. |
| `--storage` | No | `local` | Storage provider: `local`, `s3`, or `dropbox`. |
| `--dest` | Yes | — | Destination directory, S3 URI, or Dropbox path. |
| `--format` | No | `m4a` | Audio format: `m4a` or `original`. |
| `--name` | No | Video title | Custom output filename without extension. |

The `original` format preserves the downloaded audio format without conversion.

## Workflow

1. Obtain the YouTube video URL from the user.
2. Determine the storage provider。
3. Obtain the destination from the user.
   - `local`: Local directory path (`~/Downloads/music`).
   - `s3`: S3 URI (`s3://bucket-name/optional/prefix`).
   TODO: Provide Dropbox path later after the implementation.
   - `dropbox`: Dropbox destination path.
4. Determine optional arguments:
   - `format`: `m4a` (default) or `original`.
   - `name`: Custom output filename without extension (default: video title).
5. Execute the CLI command using the collected arguments.
6. Process the JSON response according to the Handling section.

Ask the user for missing required information. Use default values for unspecified optional arguments.

## Samples

### Example 1: Download to local storage

```bash
castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --dest "/home/user/Music"
```

### Example 2: Download to AWS S3

```bash
castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --storage s3 \
  --dest "s3://my-bucket/music" \
  --format m4a \
  --name "my-audio"
```

### Example 3: Download to Dropbox

```bash
castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --storage dropbox \
  --dest "/Music" \
  --format original
```

## Responses

Castoria returns a JSON response on stdout.

- Exit code `0`: The operation completed successfully.
- Exit code `1`: The operation failed. Inspect the JSON error response.

### Success

```json
{
  "success": true,
  "data": {
    "title": "Example Video",
    "video_id": "VIDEO_ID",
    "format": "m4a",
    "storage": "s3",
    "destination": "s3://my-bucket/music/my-audio.m4a"
  }
}
```

### Failure

```json
{
  "success": false,
  "error": {
    "code": "STORAGE_OUTPUT_EXISTS",
    "message": "Destination file already exists.",
    "retryable": false
  }
}
```

## Handling

On success, report the downloaded audio title and saved location
using `data.title` and `data.destination`.

On failure, inspect `error.retryable`:

- If `false`, return `error.code` and `error.message` to the user.
- If `true`, follow the Retry policy below.

### Retry

When `retryable` is `true`, consult
[Error Code Catalogue](references/error-code-catalogue.md)
to determine whether retrying is appropriate.

- Retry only when the catalogue permits it.
- Retry at most once.
- If retrying is not recommended or the retry fails,
  return the error to the user.
