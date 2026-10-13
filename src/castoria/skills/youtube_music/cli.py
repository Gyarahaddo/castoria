import argparse
import json
import sys
import traceback
from pathlib import Path
from tempfile import TemporaryDirectory

from castoria.common.exceptions import CastoriaError
from castoria.common.storage.factory import StorageProviderFactory
from castoria.skills.youtube_music.downloader import YouTubeAudioDownloader


def handle_download(args: argparse.Namespace) -> int:
    try:
        with TemporaryDirectory(prefix="castoria_") as temp_dir:
            downloader = YouTubeAudioDownloader()

            # Step 1: Download audio.
            result = downloader.download(
                url=args.link,
                workdir=Path(temp_dir),
                prefer_m4a=args.format == "m4a",
            )

            audio_path = result.file_path

            # Step 2: Convert audio if the downloaded format differs.
            if args.format != "original" and result.format != args.format:
                audio_path = downloader.convert(
                    source=audio_path,
                    target_format=args.format,
                )

            # Step 3: Store the final audio file.
            storage = StorageProviderFactory.create(args.storage)

            storage_result = storage.save(
                source=audio_path,
                destination=args.dest,
                name=args.name or result.title,
            )

            # Step 4: Return success response after storage completes.
            print(
                json.dumps(
                    {
                        "success": True,
                        "data": {
                            "title": result.title,
                            "video_id": result.video_id,
                            "format": audio_path.suffix.removeprefix("."),
                            "storage": args.storage,
                            "destination": storage_result,
                        },
                    },
                    ensure_ascii=False,
                )
            )

            return 0

    except CastoriaError as error:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": {
                        "code": error.code,
                        "message": str(error),
                        "retryable": error.retryable,
                    },
                },
                ensure_ascii=False,
            )
        )
        return 1

    except Exception:
        if args.verbose:
            traceback.print_exc(file=sys.stderr)

        print(
            json.dumps(
                {
                    "success": False,
                    "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "retryable": False},
                },
                ensure_ascii=False,
            )
        )
        return 1
