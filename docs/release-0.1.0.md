# FS Next 0.1.0 release audit

Audit date: 2026-10-04. This is the first stable FS Next release, following
0.1.0a1. The compatibility target is the PyFilesystem2 filesystem API on
CPython 3.10 and later. FS Next is an independent maintenance fork with the
original MIT license, source history and contributor credits retained.

## What was compared

Two separate reference points were checked:

- The published **PyPI `fs==2.4.16`** source archive, SHA-256
  `ae97c7d51213f4b70b6a958292530289090de3a7e15841e108fbe144f069d313`.
- The fork's upstream Git baseline
  `77a8562785fc37cb2e30bdcd39c133097ba62dce`, which also contains later upstream
  maintenance work. In particular, `Walker` already has the optional
  `filter_glob` and `exclude_glob` extensions in that Git baseline.

The reproducible source audit (`scripts/check_upstream_api.py`) found:

| Inventory | Result |
| --- | --- |
| Python module paths | 57 / 57 retained |
| Publicly named class/function/method definitions, plus constructors and context-manager methods | 730 / 730 retained; 745 in FS Next |
| Definitions excluding the reusable `fs/test.py` helper | 639 original definitions retained |
| Public assignment names, including class aliases/constants | 121 / 121 retained |
| Removed definitions or incompatible argument signatures | 0 |
| Extended signature | `Walker.__init__` adds two optional trailing parameters; existing calls remain valid |

This is a structural comparison, not a proof that every possible invocation has
identical behavior. It includes names in helper modules as well as documented
APIs; it is not presented as a count of independently implemented features.

## Installed-package behavior comparison

`scripts/check_feature_parity.py` was run with `python -I` in separate installed
upstream and candidate environments. The resulting JSON matched exactly for:

- Importing all 56 submodules (57 package/module files including `fs` itself).
- All 14 built-in opener protocols: `file`, `ftp`, `ftps`, `mem`, `osfs`,
  `siteconf`, `sitedata`, `tar`, `temp`, `usercache`, `userconf`, `userdata`,
  `userlog` and `zip`.
- MemoryFS, TempFS and OSFS text/binary/Unicode content, directory operations,
  stream seeking, copy/move, globbing, metadata and subfilesystem access.
- ZIP/TAR creation and reopening, recursive copy, move and mirror results.
- MountFS routing, MultiFS precedence and write targets, read-only wrappers,
  permission values and missing-file/directory/root-removal exception types.

AppFS's platform-specific path behavior, path/URL helpers, walkers, wrappers,
metadata and the remaining built-in methods are additionally exercised by the
inherited regression suites. All built-in implementation modules remain present.

## FTP and FTPS

The inherited loopback FTP tests cover authenticated/anonymous use and MLSD/LIST.
The release adds 88 FTPS contract tests, of which 87 pass and one correctly skips
unknown server case sensitivity. The server requires TLS for both control and
data channels and uses a temporary self-signed certificate.

This caught a real defect: worker uploads through FTPFile closed a TLS data
socket without the TLS shutdown used by `ftplib.FTP_TLS.storbinary`. The server
could fail to complete a transfer and the client timed out. Completing TLS
shutdown before waiting for the transfer response fixes workers=1/2/4 uploads.
Additional regressions verify shutdown order and closure of both sockets when
TLS shutdown raises. The encrypted round trip also checks reopening and Unicode.

The fixture validates encryption and filesystem behavior on loopback. It does
not certify public-server interoperability, certificate trust configuration,
firewall/NAT behavior or arbitrary server implementations.

## Release validation

- Local macOS CPython 3.14.7: **2,756 passed, 30 skipped, 10 third-party warnings**,
  plus three passing subtests. Project deprecations, unraisable exceptions and
  unhandled thread exceptions are errors. Python 3.10 FTP/FTPS checks also pass.
- Required release workflow: 15 full-suite OS/Python combinations
  (Linux/macOS/Windows × 3.10–3.14), five S3 migration probes, two pyfatfs probes
  and one upstream API/behavior comparison.
- Python 3.15 preview is tested separately on all three operating systems.
- Wheel/sdist metadata, fresh installed-wheel smoke and the full suite using
  installed package imports are checked before publishing.
- Adapted Sphinx documentation builds with warnings treated as errors.
- Coverage on macOS CPython 3.14.7: **92.80% statements** (4,978 / 5,364),
  **86.09% branches** (1,238 / 1,438), **91.38% combined**. The scope remains
  `fs/` excluding `fs/test.py`, with 91 existing excluded lines and no subprocess
  coverage. The additional skip is FTPS's unknown case sensitivity; see the
  [earlier skip review](test-review.md) for the other 29.

The [tagged release](https://github.com/kmsk99/fs-next/releases/tag/v0.1.0) and
[publish workflow](https://github.com/kmsk99/fs-next/actions/workflows/publish.yml)
provide the release-specific remote results. A workflow configuration alone is
not evidence of a successful run.

## Compatibility boundaries

No original built-in filesystem feature was intentionally removed. Known fixes
change erroneous behavior in date parsing, URL quoting, opener errors and FTP
cleanup/TLS shutdown. `fs.__version__` reports the FS Next version.

- Python 2 and Python below 3.10 are outside the supported runtime range.
- `fs` and `fs-next` cannot coexist in an environment. FS Next does not satisfy
  another package's dependency on the differently named `fs` distribution.
- S3 and SSH are external plugins, not built-in implementation modules in
  `fs==2.4.16`. S3 is tested with a locally migrated plugin and Moto; pyfatfs is
  an API-only probe. Live AWS, SSH and arbitrary third-party plugins are not
  certified. Follow the [migration guide](migration.md).
- Runtime setuptools/pkg_resources is intentionally removed. Namespace
  extension and the `fs.opener` entry-point group have regression coverage.

Stable status applies to this documented scope. It does not convert the above
external-service gaps into universal compatibility claims.
