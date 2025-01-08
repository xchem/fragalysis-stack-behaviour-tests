#!/usr/bin/env python
"""Utilities for interacting with S3,
relying on AWS S3 environment variables with a BEHAVIOUR_ prefix."""
import os

import boto3

# Required config
# The key must provide read access to the chosen bucket
_ACCESS_KEY_ID = os.environ.get("BEHAVIOUR_AWS_ACCESS_KEY_ID")
_SECRET_ACCESS_KEY = os.environ.get("BEHAVIOUR_AWS_SECRET_ACCESS_KEY")
# Optional config
_DEFAULT_REGION = os.environ.get("BEHAVIOUR_AWS_DEFAULT_REGION")
_ENDPOINT_URL = os.environ.get("BEHAVIOUR_AWS_ENDPOINT_URL")


def check_bucket(bucket: str) -> None:
    """Checks we can access the bucket (we simply check its location)"""
    _check_env()

    print(f"Creating S3 client (url={_ENDPOINT_URL})...")
    s3 = boto3.client(
        "s3",
        region_name=_DEFAULT_REGION,
        aws_access_key_id=_ACCESS_KEY_ID,
        aws_secret_access_key=_SECRET_ACCESS_KEY,
        endpoint_url=_ENDPOINT_URL,
    )

    print("Checking bucket location...")
    resp = s3.get_bucket_location(Bucket=bucket)
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
    print("Success")


def get_object(bucket: str, key: str, destination_dir: str = ".") -> None:
    """Get an object from an S3 bucket, placing it in the destination directory"""
    _check_env()

    print(f"Creating S3 client (url={_ENDPOINT_URL})...")
    s3 = boto3.client(
        "s3",
        region_name=_DEFAULT_REGION,
        aws_access_key_id=_ACCESS_KEY_ID,
        aws_secret_access_key=_SECRET_ACCESS_KEY,
        endpoint_url=_ENDPOINT_URL,
    )

    print(f"Downloading {bucket}/{key} to {destination_dir}...")
    destination_file: str = os.path.join(destination_dir, key)
    with open(destination_file, "wb") as f:
        s3.download_fileobj(bucket, key, f)
    print("Downloaded")


# Local functions


def _check_env() -> None:
    """Check that required environment variables are set"""
    if _SECRET_ACCESS_KEY is None or _SECRET_ACCESS_KEY == "":
        raise ValueError("BEHAVIOUR_AWS_SECRET_ACCESS_KEY is not set")
    if _ACCESS_KEY_ID is None or _ACCESS_KEY_ID == "":
        raise ValueError("BEHAVIOUR_AWS_ACCESS_KEY_ID is not set")


if __name__ == "__main__":
    check_bucket("im-xchem-data")
    get_object("im-xchem-data", "lb32627-66_v2.2_upload_1_2024-12_09.tgz")
