# Castoria

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<p align="center">
  <img
    src="assets/castoria-banner.png"
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

### External Services

Some storage providers require additional credentials or service configuration.

| Provider | Configuration | Setup Guide |
| --- | --- | --- |
| AWS S3 | AWS credentials and IAM permissions. | [AWS S3 Setup](docs/setup/aws-s3.md) |
| Dropbox | Dropbox application credentials and OAuth2 refresh token. | [Dropbox Setup](docs/setup/dropbox.md) |

## License

Castoria is licensed under the [MIT License](LICENSE).
