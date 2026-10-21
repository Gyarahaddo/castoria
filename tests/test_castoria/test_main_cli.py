import sys
from unittest.mock import Mock

import pytest

from castoria.cli import create_parser, main


@pytest.mark.parametrize("argv", [[], ["-h"], ["--help"]])
def test_main_prints_top_level_help(
    argv: list[str], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["castoria", *argv])
    handler = Mock()
    monkeypatch.setattr("castoria.cli.handle_download", handler)

    with pytest.raises(SystemExit) as exc:
        main()

    captured = capsys.readouterr()
    assert exc.value.code == 0
    assert captured.out == create_parser().format_help()
    assert captured.err == ""
    handler.assert_not_called()


@pytest.mark.parametrize(
    "argv, error",
    [
        (["unknown"], "invalid choice"),
        (["--unknown"], "required: skill"),
        (["youtube-music"], "required: action"),
        (["youtube-music", "download"], "required: --link, --dest"),
    ],
)
def test_main_preserves_argument_errors(
    argv: list[str], error: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["castoria", *argv])

    with pytest.raises(SystemExit) as exc:
        main()

    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert captured.out == ""
    assert error in captured.err


def test_main_dispatches_download_and_returns_handler_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys, "argv", ["castoria", "youtube-music", "download", "--link", "https://example.com", "--dest", "."]
    )
    handler = Mock(return_value=1)
    monkeypatch.setattr("castoria.cli.handle_download", handler)

    assert main() == 1
    handler.assert_called_once()
    args = handler.call_args.args[0]
    assert args.link == "https://example.com"
    assert args.dest == "."
