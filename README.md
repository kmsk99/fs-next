# FS Next

A maintenance fork of [PyFilesystem2](https://github.com/PyFilesystem/pyfilesystem2)
for modern Python. **Alpha release; use a fresh environment for evaluation.**

FS Next retains the `fs` import and the upstream filesystem API. It is an
independent fork, not an official PyFilesystem release. The original authors'
MIT license and copyright notices are preserved in `LICENSE`.

## Current scope

- Python 3.10+ development target.
- Local, memory, temporary, ZIP, and loopback FTP filesystems are tested.
- Runtime no longer requires setuptools or `pkg_resources`.
- Openers are discovered through `importlib.metadata` using the existing
  `fs.opener` entry-point group. Namespace extensions use `pkgutil.extend_path`.
- FS URL paths preserve their format on Python 3.14.

See [development status](docs/fs-next-status.md) for checks actually run and
remaining work. A target version range is not a claim that every upstream
feature or third-party plugin has been validated.

## Install

```sh
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install fs-next==0.1.0a1
```

## Develop locally

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests -q
```

Use a new virtual environment. **Do not install `fs` and `fs-next` together:**
both distributions write the `fs` package. Installing `fs-next` does not satisfy
another distribution's `Requires-Dist: fs`; dependency migration must be handled
explicitly. Arbitrary third-party plugin compatibility has not been established.

## Example

```python
from fs import open_fs

with open_fs("mem://") as storage:
    storage.writetext("hello.txt", "Hello, FS Next")
    print(storage.readtext("hello.txt"))
```

## Build

```sh
python -m pip install build twine
python -m build
python -m twine check dist/*
```

This creates a wheel and source archive for `fs-next` version `0.1.0a1`.
GitHub release tags must match the version (`v0.1.0a1`). The release workflow
runs compatibility tests, builds artifacts, checks a fresh wheel installation,
and uploads through PyPI Trusted Publishing. See [release instructions](docs/releasing.md).

## Upstream and documentation

- Source baseline: `77a8562785fc37cb2e30bdcd39c133097ba62dce`.
- [Upstream README](docs/upstream-readme.md) retains project history and examples.
- Existing `docs/source/` describes upstream behavior and has not yet been fully
  adapted for this fork.
- [Contribution guide](CONTRIBUTING.md).
