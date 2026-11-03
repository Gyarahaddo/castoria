# Castoria

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Gyarahaddo/castoria/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/Gyarahaddo/castoria/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/Gyarahaddo/castoria/branch/dev/graph/badge.svg?token=XWFFU9UORG)](https://codecov.io/github/Gyarahaddo/castoria)

<p align="center">
  <img
    src="assets/castoria.png"
    alt="Castoria - Your Agent's Support Servant"
    width="350"
  />
</p>

<p align="center">
  <strong>Your Agent's Support Servant.</strong>
</p>

A collection of reusable skills designed to empower AI agents through a unified, machine-friendly CLI.

Each utility is designed to provide:
- **Agent-first design:** Tools are built with AI agent workflows in mind.
- **Structured responses:** Machine-readable JSON output for reliable integration.
- **Unified CLI:** A consistent interface for both AI agents and humans.

*Unified CLI Design*
```
castoria <utility> <action> [arguments]
```

## Available Skills

| Skill | Description |
| --- | --- |
| [youtube-music](agent-skills/youtube-music/) | Download audio from YouTube videos and save it to local storage, AWS S3, or Dropbox. |

## Setup

Some Castoria features require additional dependencies, credentials,
or external service configurations.

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- FFmpeg (required for audio conversion)

### Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/Gyarahaddo/castoria.git
cd castoria
uv sync
```

### Skill Installation (Codex)

After installing the CLI, paste the following prompt into a local Codex chat
(not your terminal) to install the Castoria skills:

```text
$skill-installer Install both skills from Gyarahaddo/castoria on the master branch:
- agent-skills/castoria
- agent-skills/youtube-music
```

The `castoria` skill lists available tools and points to their detailed skills.
The `youtube-music` skill provides audio download instructions.
Skill installation is separate from CLI installation; Castoria and FFmpeg
must be available in the environment where Codex runs commands.

In your next turn, ask Codex to use `$castoria` to list available tools, or
`$youtube-music` to download audio from a YouTube link to a local directory.
If the skills do not appear, restart Codex. Installation and downloads require
network access; allow Codex to request it when needed.

See the [Codex skills documentation](https://developers.openai.com/codex/skills/)
for details. For other agents, follow your agent's own skill installation
instructions using the skill folders in [`agent-skills/`](agent-skills/).

### External Services

Some storage providers require additional credentials or service configuration.

| Provider | Configuration | Setup Guide |
| --- | --- | --- |
| AWS S3 | AWS credentials and IAM permissions. | [AWS S3 Setup](docs/setup/aws-s3.md) |
| Dropbox | Dropbox application credentials and OAuth2 refresh token. | [Dropbox Setup](docs/setup/dropbox.md) |

## License & Disclaimer

Castoria is an independent, fan-inspired open-source project and is not
affiliated with, endorsed by, or sponsored by TYPE-MOON, Aniplex, Lasengle,
or any other rights holders of Fate/Grand Order.

The source code of this project is licensed under the [MIT License](LICENSE).

The project name and character-inspired artwork are references to
Artoria Caster from Fate/Grand Order. All related characters, trademarks, and original artwork remain the property of their respective owners.
