import argparse

from castoria.skills.youtube_music.cli import handle_download


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="castoria",
        description="Castoria - Agent-First Utilities Collection.",
    )

    skills = parser.add_subparsers(
        dest="skill",
        required=True,
    )

    youtube_audio = skills.add_parser(
        "youtube-audio",
        help="YouTube audio utilities.",
    )

    actions = youtube_audio.add_subparsers(
        dest="action",
        required=True,
    )

    download = actions.add_parser(
        "download",
        help="Download audio from YouTube.",
    )

    download.add_argument(
        "--link",
        required=True,
        help="YouTube video URL.",
    )

    download.add_argument(
        "--format",
        choices=("m4a", "original"),
        default="m4a",
        help="Audio format (default: m4a).",
    )

    download.add_argument(
        "--storage",
        choices=("local", "s3", "dropbox"),
        default="local",
        help="Storage provider (default: local).",
    )

    download.add_argument(
        "--dest",
        required=True,
        help="Destination path or storage location.",
    )

    download.add_argument(
        "--name",
        help="Custom output filename.",
    )

    download.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )

    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    match (args.skill, args.action):
        case ("youtube-audio", "download"):
            return handle_download(args)

        case _:
            parser.error("Unsupported command.")


if __name__ == "__main__":
    raise SystemExit(main())
