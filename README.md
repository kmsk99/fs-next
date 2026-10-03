# FS Next

**PyFilesystem2's filesystem API, maintained for modern Python.**

[![PyPI](https://img.shields.io/pypi/v/fs-next?include_prereleases)](https://pypi.org/project/fs-next/)
[![Compatibility](https://github.com/kmsk99/fs-next/actions/workflows/test.yml/badge.svg)](https://github.com/kmsk99/fs-next/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Install](#install) · [Feature coverage](#feature-coverage) · [Test coverage](#test-coverage) · [Roadmap](#roadmap) · [Original repository](https://github.com/PyFilesystem/pyfilesystem2)

> Built on **[PyFilesystem2](https://github.com/PyFilesystem/pyfilesystem2)** by
> Will McGugan and the PyFilesystem2 contributors. FS Next preserves their code,
> history and MIT license, and adds focused maintenance changes. This independent
> fork is not an official PyFilesystem release or a from-scratch reimplementation.

Work with local directories, memory, archives and FTP through the same `fs` API:

```python
from fs import open_fs

with open_fs("mem://") as storage:
    storage.writetext("hello.txt", "Hello, FS Next")
    print(storage.readtext("hello.txt"))
```

## At a glance

Snapshot: **0.1.0a1**, source [`b7f6278`](https://github.com/kmsk99/fs-next/commit/b7f6278da8ff9589d6a27c132cefb439cf8279b7), measured 2026-10-03.

| Measure | Current status | What it means |
| --- | --- | --- |
| Upstream source retained | **57 / 57 Python modules** | All upstream `fs/**/*.py` paths remain; 8 files have maintenance changes |
| Full suite | **2,661 passed · 29 skipped** | macOS / Python 3.14 snapshot; platform-specific counts can differ |
| Test coverage | **92.8% statements · 85.9% branches** | Measured execution coverage; scope and reproduction below |
| Compatibility matrix | **9 / 9 passing** | Linux, macOS, Windows × Python 3.10, 3.12, 3.14 |
| External plugin probe | **1 plugin / 2 Python versions** | pyfatfs 1.1.0, Python 3.10 and 3.14; dependency migration remains open |
| Roadmap checklist | **8 / 15 done (53%)** | Equal-weight tasks below, not effort or production readiness |
| Release | **Published alpha** | [PyPI](https://pypi.org/project/fs-next/0.1.0a1/) · [Release notes](https://github.com/kmsk99/fs-next/releases/tag/v0.1.0a1) |

## Install

Use a fresh **Python 3.10+** virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install fs-next==0.1.0a1
```

**Do not install `fs` and `fs-next` together.** Both distributions provide the
`fs` package and can overwrite each other's files. Existing imports stay
`from fs import ...`, but a package declaring `Requires-Dist: fs` will still ask
pip to install upstream `fs`. Downstream dependency metadata must be migrated.
This alpha is intended for isolated evaluation.

## Feature coverage

### What comes from upstream?

FS Next starts from the complete PyFilesystem2 source at
[`77a8562`](https://github.com/PyFilesystem/pyfilesystem2/tree/77a8562785fc37cb2e30bdcd39c133097ba62dce),
whose package version is 2.4.16. **57/57 retained modules means source retention,
not a claim of 100% behavioral compatibility.** Most functionality and tests
below were built by the upstream contributors and are inherited here.

| Upstream capability | Implementation in FS Next | Current evidence / limits |
| --- | --- | --- |
| Local, temporary and application directories | OSFS, TempFS, AppFS retained | Full inherited suites in the 9-job CI matrix |
| In-memory storage | MemoryFS retained | Full inherited suite |
| ZIP and TAR archives | ZipFS, TarFS retained | Archive suites; separate installed-wheel ZIP round trip |
| FTP | FTPFS retained; cleanup fixes added | Loopback authenticated/anonymous and MLSD/LIST tests; hosted services and FTPS not independently validated |
| Mounting and combining filesystems | MountFS, MultiFS, SubFS retained | Inherited mount, multi and subfilesystem suites |
| Wrappers and read-only views | WrapFS and wrapper helpers retained | Inherited wrapper suites |
| Copy, move, mirror, walk, glob and paths | Upstream utilities retained | Inherited utility suites |
| URL openers and namespace extensions | Same `fs.opener` group and `fs` namespace | Modern metadata discovery, invalid-opener and split-namespace regressions |
| External backends | Plugin mechanism retained | pyfatfs FAT12 round trip only; S3, SSH and other plugins still need validation |
| Legacy Python support | Deliberately narrowed to Python 3.10+ | Python 2 and Python <3.10 are outside this fork's support target |

### What FS Next changes

| Area | Upstream baseline | FS Next 0.1.0a1 |
| --- | --- | --- |
| Runtime packaging | `pkg_resources` and setuptools required | Standard-library `pkgutil` and `importlib.metadata`; no runtime setuptools |
| Absolute FS URLs | Uses `pathname2url` | Preserves FS URL paths across the Python 3.14 behavior change |
| FTP cleanup | Finalization can wait for a server response; unused close can connect | Nonblocking socket cleanup during finalization, explicit close handling, failed-opener cleanup |
| Test compatibility | Older unittest aliases and pyftpdlib test internals | Modern assertions and public pyftpdlib server API |
| Distribution | `fs` / `import fs` | `fs-next` / `import fs`; package dependency names still differ |

## Test coverage

**92.8% statement coverage (4,975 / 5,361) · 85.9% branch coverage (1,232 / 1,434).**

**Combined coverage.py score: 91.35%.**

Measured on macOS arm64, CPython 3.14.7 with coverage.py 7.16.2 against the
0.1.0a1 source. The full `tests/` suite includes loopback FTP. Measurement covers
`fs/`, excluding the reusable `fs/test.py` test helper, using the existing
coverage exclusions in [setup.cfg](setup.cfg). Subprocess-only execution is not
collected. This is a single-platform snapshot, not merged coverage across CI.

| Validation | Result | Evidence |
| --- | --- | --- |
| Full cross-platform suite | 9/9 jobs passed | [Release workflow](https://github.com/kmsk99/fs-next/actions/runs/37130432144) |
| Finalizer/thread errors | Treated as test failures | [CI configuration](.github/workflows/test.yml) |
| Third-party entry point | pyfatfs 1.1.0 passed on 3.10 / 3.14 | [Probe](scripts/check_pyfatfs.py); installed with `--no-deps`, not a resolver compatibility claim |
| Published wheel | Fresh PyPI installation passed without setuptools | [Smoke check](scripts/check_wheel.py): memory, disk, ZIP, Unicode paths |
| Coverage detail | Per-module results and totals | [Coverage snapshot](docs/coverage.md) |

Reproduce coverage from a checkout:

```sh
python -m pip install -e '.[test]' coverage==7.16.2
python -m coverage erase
python -m coverage run -m pytest tests -q \
  -W error::pytest.PytestUnraisableExceptionWarning \
  -W error::pytest.PytestUnhandledThreadExceptionWarning
python -m coverage combine
python -m coverage report
```

**Remaining gaps:** 29 tests are skipped in the macOS snapshot, deprecated API
warnings remain, and remote services, arbitrary plugins and production workloads
need further validation. See [validation notes](docs/fs-next-status.md).

## Roadmap

**`████████░░░░░░░` 8 / 15 tasks complete · 53%**

This is the initial maintenance roadmap, with future work proposed below and no
promised dates. Each checkbox counts once; tasks differ in size. The percentage
tracks this checklist, independently of inherited features and test coverage.

| Milestone | Progress | Status |
| --- | --- | --- |
| 1. Modern Python alpha | **6/6 · 100%** | ✅ Shipped in 0.1.0a1 |
| 2. Compatibility evidence | **2/5 · 40%** | 🟡 Next focus |
| 3. Stable release preparation | **0/4 · 0%** | ○ Planned |

### 1. Modern Python alpha — 6/6

- [x] Preserve upstream source, history, MIT notices and `fs` imports.
- [x] Remove runtime setuptools/pkg_resources and retain opener discovery.
- [x] Fix Python 3.14 URL behavior and modernize test dependencies.
- [x] Fix FTP cleanup stalls and failed-opener connection cleanup.
- [x] Pass the full suite on 3 operating systems × 3 Python versions.
- [x] Publish an alpha via Trusted Publishing and verify a fresh PyPI install.

### 2. Compatibility evidence — 2/5

- [x] Exercise a real external plugin and document its dependency-name conflict.
- [x] Publish a reproducible coverage baseline and capability matrix.
- [ ] Add Python 3.11 and 3.13 to CI and publish the complete support policy.
- [ ] Validate representative S3/SSH plugins and document clean dependency migration.
- [ ] Validate FTPS and representative external FTP servers beyond loopback tests.

### 3. Stable release preparation — 0/4

- [ ] Review skipped tests and uncovered branches; add regressions for identified gaps.
- [ ] Resolve remaining deprecated API use and review runtime dependencies.
- [ ] Adapt upstream API documentation and publish a migration guide with tested examples.
- [ ] Complete release-candidate validation, changelog and support policy before a stable release.

## Develop and contribute

```sh
git clone https://github.com/kmsk99/fs-next.git
cd fs-next
python -m pip install -e '.[test]'
python -m pytest tests -q
```

Use an activated virtual environment. Contributions that close a documented gap,
add a reproducible compatibility case or fix an upstream regression are welcome.
See [CONTRIBUTING.md](CONTRIBUTING.md) and [open an issue](https://github.com/kmsk99/fs-next/issues).

<details>
<summary>Build and release</summary>

```sh
python -m pip install build twine
python -m build
python -m twine check dist/*
```

A matching GitHub release tag triggers tests, artifact builds, a clean-wheel
check and PyPI Trusted Publishing. See [release instructions](docs/releasing.md).

</details>

## Upstream and acknowledgements

The filesystem abstractions, implementations, documentation and much of the
regression suite come from **PyFilesystem2**. Credit belongs to **Will McGugan,
Martin Larralde, Giampaolo Cimino, Geoff Jukes**, and the many
[upstream contributors](https://github.com/PyFilesystem/pyfilesystem2/graphs/contributors).
FS Next builds on that work with a narrower modern-Python maintenance focus.

- **[Original repository — PyFilesystem/pyfilesystem2](https://github.com/PyFilesystem/pyfilesystem2)**
- [Original package — `fs` on PyPI](https://pypi.org/project/fs/)
- [Upstream documentation](https://pyfilesystem2.readthedocs.io/en/latest/)
- [Preserved upstream README](docs/upstream-readme.md) · [Contributor credits](CONTRIBUTORS.md)
- [MIT license and original copyright notices](LICENSE), retained unchanged

Upstream documentation describes the original project and may contain its
package name and historical support policy. Use this README for FS Next's
installation, tested scope and roadmap. Neither the original maintainers'
endorsement nor official succession is implied.
