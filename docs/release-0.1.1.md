# FS Next 0.1.1: published upstream compatibility audit

Audit date: 2026-10-04. The reference is the latest actual PyPI `fs` release,
**2.4.16**, checked through `https://pypi.org/pypi/fs/json`. Both published
artifacts were downloaded and their SHA-256 digests verified:

| Artifact | SHA-256 |
| --- | --- |
| `fs-2.4.16-py2.py3-none-any.whl` | `660064febbccda264ae0b6bace80a8d1be9e089e0a5eb2427b7d517f9a91545c` |
| `fs-2.4.16.tar.gz` | `ae97c7d51213f4b70b6a958292530289090de3a7e15841e108fbe144f069d313` |

All 57 Python files in the wheel match their sdist counterparts byte for byte.
FS Next retains all 57 module paths, all 730 publicly named definitions plus
constructors/context managers, and all 121 public assignment names. No original
argument signature is incompatible. The optional Walker glob arguments are an
upstream Git extension. The original `scandir` installation extra is retained;
on Python 3.10+ it needs no additional dependency because `os.scandir` is built in.

## Complete original regression suite

`scripts/check_upstream_tests.py` verifies the sdist digest, copies its entire
`tests/` tree and loads its original **`fs/test.py` contract helper**. Everything
else under `fs` comes from the installed candidate, outside the checkout.
The original suite is run on Python 3.10, which still supports its unittest and
FTP-server test dependencies. No test is deselected and no assertion is changed.

Two narrow test-harness adaptations are explicit:

- Four entry-point mock targets are redirected from `pkg_resources` to the
  replacement discovery function. The same protocol, load-error, type-error
  and constructor-error assertions are retained.
- The exception-pickling fixture runs last and joins its already-closed pool.
  The old FTP fixture otherwise mistakes Python's resource-tracker process
  for a leaked server child and terminates it. Its original exception assertions are retained.

The old harness needs setuptools, pyftpdlib 1.5.10 and psutil in its isolated
**test environment**. FS Next still has no runtime setuptools dependency.
The modern suite separately verifies discovery and namespace extension without
pkg_resources and uses public pyftpdlib APIs.

Local installed-candidate result: **2,400 passed, 29 capability/platform skips**.
The original suite is now also a required CI job on Linux, macOS and Windows.
The skips remain visible; see the [skip review](test-review.md#skipped-tests).

## Feature-to-test mapping

Every built-in family in the published package remains implemented:

| Original feature | Regression evidence |
| --- | --- |
| Base FS API, streams, modes, hashing, deprecated aliases | Original `fs.test`, `test_base`, `test_iotools`, `test_mode`, doctests; added hash error/alias checks |
| Local files, temporary files, application directories | `test_osfs`, `test_tempfs`, `test_appfs`, `test_encoding` |
| Memory filesystem | `test_memoryfs` plus original shared contract |
| FTP, authenticated/anonymous access, MLSD/LIST | Original `test_ftpfs`, modern FTP suite |
| FTP over TLS | Full encrypted `test_ftps` contract, worker transfer and seek regressions, invalid-hash connection reuse |
| ZIP and TAR, compression, archive opener | `test_zipfs`, `test_tarfs`, `test_compress`, `test_archives` |
| MountFS, MultiFS, SubFS | `test_mountfs`, `test_multifs`, `test_subfs` |
| WrapFS, read-only and other wrappers | `test_wrapfs`, `test_wrap` |
| Copy, move, mirror, bulk operations | `test_copy`, `test_move`, `test_mirror`, `test_bulk` |
| Walkers, globbing, wildcard matching | `test_walk`, `test_glob`, `test_wildcard` |
| Metadata, permissions, errors and exception pickling | `test_info`, `test_permissions`, `test_errors`, `test_error_tools` |
| Paths, URLs, encoding, time, tree, size and utilities | `test_path`, `test_url_tools`, `test_encoding`, `test_time`, `test_tree`, `test_filesize`, `test_tools`, `test_lrucache`, `test_enums`, `test_fscompat` |
| All 14 built-in URL protocols and external opener loading | `test_opener`, `test_imports`, installed upstream/candidate behavior comparison |
| Distribution data and install extra | Wheel metadata, `py.typed`, retained `scandir` extra, installed-wheel smoke/full suite |

The independent deterministic behavior probe also matches the installed original
for all 14 opener registrations, local/memory/temp operations, archives,
copy/move/mirror, mounts, multi-filesystems, wrappers and error types.

## Python 3.15 FTPS/hash fix

The 0.1.0 preview failure is resolved in FS Next. CPython 3.15's unsupported
hash-algorithm path can leave OpenSSL error state on the caller's thread;
a subsequent read on an existing TLS connection raises `[EVP] unsupported`.
The failure reproduces with the standard-library `ftplib.FTP_TLS` client alone.
The [CPython source](https://github.com/python/cpython/blob/v3.15.0rc2/Modules/_hashopenssl.c)
shows the unsupported-algorithm branches peeking at the error without clearing
it, unlike the common SSL error handler.

On Python 3.15+, FS Next constructs hashes in a short-lived worker thread, whose
OpenSSL error state is discarded on exit. File reads and hashing remain on the
caller thread. This preserves `hashlib` lookup, including aliases absent from
`algorithms_available`, and the original exception types. It adds a thread
creation cost to each `FS.hash` call on these interpreters. No algorithm
allowlist, disabled TLS validation or private OpenSSL API is used.

Regressions check available fixed-length algorithms, SHA-256 aliases, invalid
names, error types, and continued reads/NOOP on the **same** FTPS connection.
The full Python 3.15 preview workflow now gates publishing, alongside the
stable-version matrix; a failing preview can no longer be published by this
workflow.

## Validation before commit

- macOS CPython 3.10.20, 3.11.15, 3.12.14, 3.13.15, 3.14.7 and 3.15.0rc1:
  **2,760 passed, 30 skipped** per full-suite run, plus 25 passing subtests.
- Fresh installed wheel on 3.15rc1: the same full suite passes, as do the
  no-setuptools smoke test and original/candidate behavior JSON comparison.
- Complete original 2.4.16 suite on installed candidate, Python 3.10:
  **2,400 passed, 29 skipped**. Legacy harness/dependency warnings remain visible.
- Clean macOS 3.14 coverage: **4,985 / 5,373 statements (92.78%)**,
  **1,237 / 1,438 branches (86.02%)**, **91.35% combined**. This single-runtime
  measurement does not include the 3.15 branch; the real 3.15 suite exercises it.
- Wheel/sdist build and metadata validation, packaged-file audit, documentation
  build with warnings as errors, and original API inventory checks.

Remote release gates run the stable matrix, the original suite on three OSes,
plugin probes, the 3.15 preview matrix, documentation/build and the installed
wheel suite before PyPI upload. Local macOS results do not stand in for those
remote results. See the [release workflow](https://github.com/kmsk99/fs-next/actions/workflows/publish.yml)
and [tagged release](https://github.com/kmsk99/fs-next/releases/tag/v0.1.1).

## Scope

No built-in feature from the latest published original is intentionally omitted.
This is evidence from artifact comparison and complete regression suites, not a
proof for every possible input or deployment. Python below 3.10 remains outside
the agreed support range. `fs-next` retains `import fs` but cannot coexist with
`fs` or satisfy another distribution's `Requires-Dist: fs` without migration.
S3 and SSH are external plugins, not built-ins in the original package. The
existing S3 emulator and pyfatfs probes remain separate from claims about live
cloud accounts, arbitrary plugins or public FTP servers.
