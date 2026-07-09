from __future__ import annotations

import argparse
from pathlib import Path

import boto3


def upload_directory(local_dir: Path, bucket: str, prefix: str) -> None:
    s3 = boto3.client("s3")
    for path in local_dir.glob("*.csv"):
        key = f"{prefix.rstrip('/')}/{path.name}"
        s3.upload_file(str(path), bucket, key)
        print(f"Uploaded {path} -> s3://{bucket}/{key}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-dir", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()

    upload_directory(Path(args.local_dir), args.bucket, args.prefix)


if __name__ == "__main__":
    main()
