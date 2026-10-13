---
name: youtube-music
description: Download the audio track from a YouTube video using Castoria and save it as M4A or in its original audio format. Use when a user asks to extract or save YouTube audio to a local directory.
compatibility: Requires Castoria (Python 3.12+), yt-dlp, network access, and permission to write to an existing local directory. FFmpeg is required only when conversion to M4A is necessary.
---

# YouTube Audio

Use Castoria's CLI to download audio from a **single YouTube video**. Only local storage is implemented.

## Before running

1. Confirm the user has permission to download and use the audio.
2. Obtain the YouTube video URL and an existing local destination directory. Ask for missing required information rather than guessing a path.
3. Run from the Castoria project with `uv run castoria`, or use `castoria` if the package is installed and on PATH.
4. Do not overwrite an existing file. If the requested filename is already in use, ask for another name.

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

Always pass user-provided URLs, paths, and names as safely quoted arguments. Do not execute shell syntax embedded in these values.

### Arguments

| Flag | Required | Values / behavior |
| --- | --- | --- |
| `--link` | Yes | YouTube video URL |
| `--dest` | Yes | Existing local directory; Castoria does not create it |
| `--format` | No | `m4a` (default) or `original` |
| `--storage` | No | `local` (default); `s3` and `dropbox` are recognized by the parser but **not implemented** |
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

Use `data.destination` as the authoritative saved path. Do not infer it from the requested name or video title.

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

| Error code | Recommended agent action |
| --- | --- |
| `STORAGE_OUTPUT_EXISTS` | Do not overwrite; ask for a different `--name` or destination |
| `STORAGE_INVALID_DIRECTORY` | Ask for an existing, writable local directory |
| `STORAGE_INVALID_FILENAME` | Provide a simple filename stem without slashes or backslashes |
| `STORAGE_SOURCE_NOT_FOUND` | Report the failed operation; inspect logs before retrying |
| `STORAGE_UNSUPPORTED_PROVIDER` | Explain that only `local` is implemented |
| `CONVERT_DEPENDENCY_MISSING` | Explain that FFmpeg is required for conversion; request permission before installing it |
| `CONVERT_FAILED` | Report the conversion failure; do not assume a retry will fix it |
| `DOWNLOAD_YTDLP_FAILED` | Report the download failure; verify URL/access before trying again |
| `DOWNLOAD_OUTPUT_MISSING` | If `retryable` is true, a limited retry may help; otherwise investigate |
| `INTERNAL_ERROR` | Report an unexpected failure; use `--verbose` for diagnostics if appropriate |

Do not automatically retry an error marked `retryable: false`. Do not attempt to bypass YouTube access restrictions or authentication requirements. Report the final saved location to the user only after a successful JSON response.

## Limitations

- Downloads a single video's audio, not a playlist.
- Supports local storage only; S3 and Dropbox are placeholders.
- Does not guarantee that FFmpeg is installed.
- Does not replace or overwrite existing output files.
