---
name: youtube-music
description: Download the audio track from a YouTube video using Castoria and save it as M4A or in its original audio format. Use when a user asks to extract or save YouTube audio to a local directory or AWS S3.
compatibility: Requires Castoria (Python 3.12+), yt-dlp, and network access. Local storage requires an existing writable directory; S3 requires AWS credentials with permission to upload to the target bucket. FFmpeg is required only when conversion to M4A is necessary.
---

# YouTube Audio

Use Castoria's CLI to download audio from a **single YouTube video**. Local and AWS S3 storage are implemented; Dropbox is not yet implemented.

## Before running

1. Confirm the user has permission to download and use the audio.
2. Obtain the YouTube video URL and destination: an existing local directory for `local`, or an S3 URI (`s3://bucket/optional/prefix`) for `s3`. Ask for missing required information rather than guessing a path or bucket.
3. Run from the Castoria project with `uv run castoria`, or use `castoria` if the package is installed and on PATH.
4. For S3, ensure AWS credentials are configured using the standard boto3 credential chain, or set `CASTORIA_AWS_PROFILE` to an existing AWS profile (which must work; Castoria will not fall back to another profile). Do not request or expose AWS access keys in command arguments.
5. Do not overwrite an existing local file or S3 object. If the requested filename is already in use, ask for another name.

## Download

```bash
uv run castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format m4a \
  --storage local \
  --dest "/path/to/existing/directory"
```

Optional custom basename (without extension):

```bash
uv run castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format original \
  --storage local \
  --dest "/path/to/existing/directory" \
  --name "my-audio"
```

For AWS S3, use a bucket with an optional key prefix:

```bash
uv run castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --format m4a \
  --storage s3 \
  --dest "s3://my-bucket/music" \
  --name "my-audio"
```

To select a configured AWS profile, set `CASTORIA_AWS_PROFILE` in the environment or project `.env` before running Castoria. When unset, boto3 uses its standard credential resolution chain (including IAM roles). S3 destinations are validated syntactically; bucket existence and permissions are checked by AWS during upload.

Always pass user-provided URLs, paths, and names as safely quoted arguments. Do not execute shell syntax embedded in these values.

### Arguments

| Flag | Required | Values / behavior |
| --- | --- | --- |
| `--link` | Yes | YouTube video URL |
| `--dest` | Yes | Existing local directory for `local` (not created automatically), or `s3://bucket/optional/prefix` for `s3` |
| `--format` | No | `m4a` (default) or `original` |
| `--storage` | No | `local` (default) or `s3`; `dropbox` is recognized but **not implemented** |
| `--name` | No | Filename stem, without extension; defaults to the video title |
| `--verbose` | No | Include unexpected-error traceback on stderr |

With `m4a`, Castoria prefers an available M4A stream; otherwise it downloads available audio and converts it using FFmpeg. With `original`, it downloads the best available audio without conversion. The output extension follows the resulting audio file.

## Interpret results

On success, the command exits with code `0` and writes a JSON object to stdout:

```json
{
  "success": true,
  "data": {
    "title": "Example video",
    "video_id": "VIDEO_ID",
    "format": "m4a",
    "storage": "local",
    "destination": "/path/to/existing/directory/Example video.m4a"
  }
}
```

For S3, `data.destination` is the full object URI (for example, `s3://my-bucket/music/my-audio.m4a`). Use `data.destination` as the authoritative saved path. Do not infer it from the requested name or video title.

Known application failures exit with code `1` and write JSON to stdout:

```json
{
  "success": false,
  "error": {
    "code": "STORAGE_OUTPUT_EXISTS",
    "message": "Destination file already exists: /path/to/file.m4a",
    "retryable": false
  }
}
```

Inspect `success`, `error.code`, and `error.retryable`; never assume that a nonzero exit has a JSON response. Invalid CLI arguments are rejected by `argparse` with text on stderr and exit code `2`.

## Error handling

Castoria returns structured JSON errors with `code`, `message`, and `retryable`.

- If `success` is `true`, report `data.destination` to the user.
- If `success` is `false` and `retryable` is `false`, return the error message to the user. **Do not troubleshoot or retry.**
- If `success` is `false` and `retryable` is `true`, read [Error Code Catalogue](references/error-code-catalogue.md) to decide whether a limited retry is appropriate. Follow its instructions; do not retry indefinitely.

Do not bypass YouTube access restrictions or authentication requirements. Do not overwrite existing files or S3 objects.

## Limitations

- Downloads a single video's audio, not a playlist.
- Supports local and AWS S3 storage; Dropbox is not implemented.
- S3 uses a conditional single-object PUT (`IfNoneMatch="*"`) to prevent overwriting an existing object.
- Does not guarantee that FFmpeg is installed.
- Does not replace or overwrite existing output files.
