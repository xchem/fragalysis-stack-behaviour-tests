#!/usr/bin/env python
"""Utilities for interacting with S3,
relying on AWS S3 environment variables with a BEHAVIOUR_ prefix."""
import os

import boto3
from config import (
    S3_ACCESS_KEY_ID,
    S3_DEFAULT_REGION,
    S3_ENDPOINT_URL,
    S3_SECRET_ACCESS_KEY,
    get_env_name,
)


def check_bucket(bucket: str) -> None:
    """Checks we can access the bucket (we simply check its location)"""
    _check_env()

    print(f"Creating S3 client (url={S3_ENDPOINT_URL})...")
    s3 = boto3.client(
        "s3",
        region_name=S3_DEFAULT_REGION,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        endpoint_url=S3_ENDPOINT_URL,
    )

    print("Checking bucket location...")
    resp = s3.get_bucket_location(Bucket=bucket)
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
    print("Success")


def get_object(bucket: str, key: str, destination_dir: str = ".") -> None:
    """Get an object from an S3 bucket, placing it in the destination directory"""
    _check_env()

    print(f"Creating S3 client (url={S3_ENDPOINT_URL})...")
    s3 = boto3.client(
        "s3",
        region_name=S3_DEFAULT_REGION,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        endpoint_url=S3_ENDPOINT_URL,
    )

    print(f"Downloading {bucket}/{key} to {destination_dir}...")
    destination_file: str = os.path.join(destination_dir, key)
    with open(destination_file, "wb") as f:
        s3.download_fileobj(bucket, key, f)
    print("Downloaded")


# Local functions


def _check_env() -> None:
    """Check that required environment variables are set"""
    if S3_SECRET_ACCESS_KEY is None or S3_SECRET_ACCESS_KEY == "":
        raise ValueError(get_env_name("S3_SECRET_ACCESS_KEY") + " is not set")
    if S3_ACCESS_KEY_ID is None or S3_ACCESS_KEY_ID == "":
        raise ValueError(get_env_name("S3_ACCESS_KEY_ID") + " is not set")


if __name__ == "__main__":
    check_bucket("im-xchem-data")
    get_object("im-xchem-data", "lb32627-66_v2.2_upload_1_2024-12_09.tgz")
