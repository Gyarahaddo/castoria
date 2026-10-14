import os

import boto3
from dotenv import load_dotenv
from mypy_boto3_s3 import S3Client

load_dotenv()


def create_s3_client() -> S3Client:
    profile = os.getenv("CASTORIA_AWS_PROFILE")

    session = boto3.Session(
        profile_name=profile or None,
    )

    return session.client("s3")
