import pytest

from castoria.cli import create_parser


def test_youtube_music_download_command() -> None:
    args = create_parser().parse_args(
        [
            "youtube-music",
            "download",
            "--link",
            "https://www.youtube.com/watch?v=example",
            "--dest",
            "/tmp",
        ]
    )

    assert args.skill == "youtube-music"
    assert args.action == "download"
    assert args.format == "m4a"
    assert args.storage == "local"


def test_old_youtube_audio_command_is_rejected() -> None:
    with pytest.raises(SystemExit) as exc:
        create_parser().parse_args(
            [
                "youtube-audio",
                "download",
                "--link",
                "https://www.youtube.com/watch?v=example",
                "--dest",
                "/tmp",
            ]
        )

    assert exc.value.code == 2
