# Releasing FS Next

1. Update `fs/_version.py` and the README install example. Document changes and
   remaining limitations. Commit and push; require passing Compatibility and
   Build distributions checks.
2. Create a GitHub release whose tag is `v` followed by the exact version.
   Mark alpha/beta/RC versions as prereleases. Use reviewed release notes.
3. `publish.yml` tests the tagged source on Linux/macOS/Windows, builds the wheel
   and sdist, validates metadata and checks a fresh installed wheel without
   setuptools, runs the full suite against installed-wheel imports and builds
   the documentation with warnings treated as errors. The test gate also
   compares API/behavior with PyPI fs 2.4.16. Only then can `publish` upload to PyPI.
4. Verify the version on PyPI, install it into a new virtual environment and run
   `python -I scripts/check_wheel.py` against the published package.

## Trusted Publisher configuration

- PyPI project: `fs-next`
- GitHub owner/repository: `kmsk99/fs-next`
- Workflow: `publish.yml`
- GitHub environment: `pypi`

The publish job alone receives `id-token: write`. No long-lived PyPI token is
stored in this repository. PyPI account and GitHub ownership must be configured
before the first release. TestPyPI is a separate service and was not used for
the first alpha; the workflow's clean-wheel check provides installation testing.

PyPI versions cannot be overwritten. If a published package needs corrections,
prepare a new version and release rather than trying to replace its files.
