# FS Next alpha validation

## Follow-up development

The sections below describe the published 0.1.0a1 baseline. Subsequent work adds
Python 3.11/3.13 to required CI, Python 3.15 preview checks, FTP date and ZIP
fallback regressions, and an S3 plugin migration probe. See the
[support policy](support-policy.md), [migration guide](migration.md) and
[test review](test-review.md) for current development evidence. Python 3.10
remains supported. This follow-up is not a new published package release.

## Provenance

- Upstream: https://github.com/PyFilesystem/pyfilesystem2
- Baseline: `77a8562785fc37cb2e30bdcd39c133097ba62dce`.
- Original history and MIT LICENSE are retained.
- FS Next is an independent maintenance fork, with distribution name `fs-next`
  and import name `fs`. It is not an official PyFilesystem release.

## Changes in 0.1.0a1

- Remove runtime setuptools/pkg_resources dependency. Use `pkgutil.extend_path`
  for namespace extensions and `importlib.metadata` for opener entry points.
- Retain `fs.opener` discovery, including errors for invalid opener objects.
- Fix absolute FS URLs affected by Python 3.14's `pathname2url` change.
- Update removed unittest assertion aliases in upstream test helpers.
- Avoid network waits during FTP garbage collection, close failed opener
  connections, and prevent closing an unused filesystem from opening a connection.
  Python 3.12 CI exposed a reproducible server-thread stall during finalization.
- Modernize FTP integration tests to pyftpdlib 2's public server API, bound only
  to loopback. Join the server thread before teardown.
- Close stream wrappers before their underlying files in inherited I/O tests,
  removing three unraisable finalizer warnings without suppressing exceptions.

## Local checks

On macOS arm64:

- Python 3.14.7 full suite including FTP: **2,661 passed, 29 skipped**.
  Unraisable exceptions and unhandled thread exceptions are treated as errors.
  38 other warnings remain, chiefly inherited deprecated APIs, pyftpdlib UTC
  deprecations and anonymous write access in the loopback test server.
- Coverage baseline: **92.80% statements, 85.91% branches** on macOS/Python
  3.14.7; [scope and per-module results](coverage.md).
- Python 3.10.20 focused core suite: 545 passed, 7 skipped.
- Wheel and sdist build; `twine check` passes.
- Fresh wheel installation outside the checkout checks MemoryFS, OSFS, ZIP,
  Unicode filenames and imports without setuptools/pkg_resources.
- Regression fixtures test real `.dist-info` opener discovery and split namespace
  packages. These fixtures do not establish universal extension compatibility.

[Release workflow 37130432144](https://github.com/kmsk99/fs-next/actions/runs/37130432144)
passed all 9 OS/Python test jobs and both plugin probes.

GitHub Actions runs the full suite on Linux, macOS and Windows with Python 3.10,
3.12 and 3.14. Release publishing repeats that gate and verifies the installed
wheel before using PyPI Trusted Publishing. See Actions for each run's result.

## Third-party plugin probe

`pyfatfs==1.1.0` was installed in an isolated Python 3.14 environment with
`--no-deps`. Its real `fat://` entry point successfully created, wrote, reopened,
read and removed files on a FAT12 image. Reproduce with
`scripts/check_pyfatfs.py`; CI also probes Python 3.10.

This is an **API compatibility probe**, not a general installation solution.
pyfatfs declares `Requires-Dist: fs~=2.4`. Installing it normally brings in `fs`;
`fs-next` cannot satisfy a dependency on a differently named distribution.
Do not install both: they overwrite the same `fs` package. Downstream projects
must migrate their dependency metadata before ordinary resolver-based installs
can use FS Next cleanly. Other plugins are not yet validated.

## Release scope and limits

- Alpha: suitable for isolated evaluation; no blanket production-readiness claim.
- Local, memory, temporary, ZIP and loopback FTP behavior is covered; hosted FTP
  servers and other remote service backends are not independently certified.
- Python 3.10+ is the target; CI explicitly samples 3.10, 3.12 and 3.14.
- TestPyPI upload was not exercised; it uses separate account authentication.
  The release gate uses a fresh installed-wheel smoke test instead.
- Historical `docs/source/` pages and the upstream README may contain old package
  names, commands and support claims. Use the root README for this fork.

## References

- https://github.com/PyFilesystem/pyfilesystem2/issues/597
- https://github.com/PyFilesystem/pyfilesystem2/issues/598
- https://docs.python.org/3.14/library/urllib.request.html#urllib.request.pathname2url
- https://pyftpdlib.readthedocs.io/en/latest/api.html
- https://pypi.org/project/pyfatfs/1.1.0/
- https://docs.pypi.org/trusted-publishers/
