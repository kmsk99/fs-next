"""Check a migrated fs-s3fs installation against Moto's in-process S3 emulator.

No AWS account, real credentials, or network S3 service is used. Install with
normal dependency resolution first and run pip check; see docs/migration.md.
"""

from importlib.metadata import PackageNotFoundError, distribution, version

import boto3
from moto import mock_aws

from fs import errors, open_fs


def main():
    try:
        distribution("fs")
    except PackageNotFoundError:
        pass
    else:
        raise RuntimeError("The conflicting upstream fs distribution is installed")
    assert version("fs-s3fs") == "1.1.1+fsnext.1"
    assert any(r.startswith("fs-next") for r in distribution("fs-s3fs").requires)
    with mock_aws():
        client = boto3.client(
            "s3",
            region_name="us-east-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        client.create_bucket(Bucket="fs-next-probe")
        url = "s3://testing:testing@fs-next-probe"
        with open_fs(url) as storage:
            storage.makedir("documents")
            storage.writetext("documents/한글.txt", "FS Next / S3 round trip")
            storage.writebytes("documents/data.bin", b"\x00\xffpayload")
            assert sorted(storage.listdir("documents")) == ["data.bin", "한글.txt"]
        with open_fs(url) as storage:
            assert storage.readtext("documents/한글.txt") == "FS Next / S3 round trip"
            assert storage.readbytes("documents/data.bin") == b"\x00\xffpayload"
            storage.remove("documents/한글.txt")
            storage.remove("documents/data.bin")
            storage.removedir("documents")
            assert storage.listdir("/") == []
            try:
                storage.readbytes("missing")
            except errors.ResourceNotFound:
                pass
            else:
                raise AssertionError("Missing object did not raise ResourceNotFound")
    print(
        "S3 opener, Unicode/binary round trip, reopen, deletion and missing-object checks passed"
    )
    for package in ("fs-next", "fs-s3fs", "moto", "boto3", "botocore"):
        print(f"{package}=={version(package)}")


if __name__ == "__main__":
    main()
