# Migrating from PyFilesystem2

FS Next is an independent maintenance fork. Existing `import fs` and
`from fs import open_fs` statements and the `fs.opener` entry-point group remain
unchanged. Start in a **new virtual environment**: `fs` and `fs-next` install
overlapping files and must not coexist.

## Application without external plugins

Change the application's dependency from `fs` to `fs-next`, regenerate its lock
file, then install into a fresh environment. For the first stable release:

```sh
python -m venv .venv-fsnext
# POSIX; on Windows use .venv-fsnext\Scripts\activate
. .venv-fsnext/bin/activate
python -m pip install fs-next==0.1.0
python -m pip check
python -c 'from fs import open_fs; f = open_fs("mem://"); f.writetext("hello.txt", "hello"); assert f.readtext("hello.txt") == "hello"; f.close()'
```

Run your application's own filesystem and error-handling tests. See
[support policy](support-policy.md) for Python versions and
[release audit](release-0.1.0.md) for the published release's scope.

If both distributions were installed accidentally, rebuild the environment.
Uninstalling just one can remove files belonging to the other.

## Plugins need a dependency metadata change

`fs-next` cannot satisfy `Requires-Dist: fs`. A constraints file or installing
FS Next first does not rename dependencies. Every package in the dependency
chain that requires `fs` must migrate its metadata. Keep its import names and
`fs.opener` entry points unchanged.

The earlier pyfatfs `--no-deps` probe tests API behavior only and leaves an
unsatisfied dependency. Do not use it as a normal installation recipe.

### Reproducible S3 migration example

This example adapts [fs-s3fs 1.1.1](https://pypi.org/project/fs-s3fs/1.1.1/)
locally. Its original source, MIT license and credits remain intact. The helper
changes only `fs~=2.4` to `fs-next>=0.1.0a1,<0.2` and labels the result
`1.1.1+fsnext.1`. No upstream package has been changed or published.

From this checkout, in a fresh virtual environment with pip:

```sh
mkdir -p .local/plugin-source
python -m pip download --no-deps --no-binary=:all: fs-s3fs==1.1.1 -d .local/plugin-source
tar -xzf .local/plugin-source/fs-s3fs-1.1.1.tar.gz -C .local/plugin-source
python scripts/prepare_s3fs_probe.py .local/plugin-source/fs-s3fs-1.1.1
python -m pip install . ./.local/plugin-source/fs-s3fs-1.1.1 "moto[s3]==5.2.3"
python -m pip check
python scripts/check_s3fs.py
```

`--no-deps` above applies only to downloading the original source. Installation
uses normal dependency resolution. The probe rejects an installed `fs`
distribution and checks the migrated dependency metadata. Re-extract the original
archive before rerunning the preparation helper; it rejects already changed input.

The source archive SHA-256 used for verification is
`b57f8c7664460ff7b451b4b44ca2ea9623a374d74e1284c2d5e6df499dc7976c`.

The check creates a bucket in Moto's in-process emulator and exercises the real
`s3://` entry point: directories, Unicode text, binary data, listing, close and
reopen, removal and missing-object errors. It uses synthetic credentials and
needs no AWS account. This validates local plugin/API integration, not AWS IAM,
TLS, network failures, multipart behavior or hosted S3 service compatibility.

Keep the adapted package as a local/private build. A public plugin release needs
its own ownership, naming and release decision. For a real application, pin the
tested artifact and dependency set in your lock file; do not replace it with an
unmodified PyPI plugin during deployment. SSH and other plugins still need their
own migration and backend tests.
