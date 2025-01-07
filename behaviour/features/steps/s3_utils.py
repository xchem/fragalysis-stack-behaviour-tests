#!/usr/bin/env python
"""Utilities for interacting with S3,
relying on conventional AWS S3 environment variables"""
import os

import boto3

# Required config
_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
# Optional config
_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")
_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION")


def check_bucket(bucket: str) -> None:
    """Checks we can access the bucket (we simply check its location)"""
    if _SECRET_ACCESS_KEY is None or _SECRET_ACCESS_KEY == "":
        raise ValueError("AWS_SECRET_ACCESS_KEY is not set")
    if _ACCESS_KEY_ID is None or _ACCESS_KEY_ID == "":
        raise ValueError("AWS_ACCESS_KEY_ID is not set")

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


def get_object(bucket: str, key: str, destination_dir: str) -> None:
    """Get an object from an S3 bucket, placing it in the destination directory"""
    if _SECRET_ACCESS_KEY is None or _SECRET_ACCESS_KEY == "":
        raise ValueError("AWS_SECRET_ACCESS_KEY is not set")
    if _ACCESS_KEY_ID is None or _ACCESS_KEY_ID == "":
        raise ValueError("AWS_ACCESS_KEY_ID is not set")

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


if __name__ == "__main__":
    check_bucket("im-xchem-data")
    get_object("im-xchem-data", "lb32627-66_v2.2_upload_1_2024-12_09.tgz", "/tmp")
