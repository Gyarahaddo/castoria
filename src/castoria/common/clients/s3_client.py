from __future__ import annotations

import os
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


def create_s3_client() -> S3Client:
    profile = os.getenv("CASTORIA_AWS_PROFILE")

    session = boto3.Session(
        profile_name=profile or None,
    )

    return session.client("s3")
