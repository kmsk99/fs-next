# Compatibility and regression review

Follow-up to the 0.1.0a1 baseline, 2026-10-04. These changes are not a new PyPI
release. [The baseline coverage report](coverage.md) remains a historical snapshot.

## Local verification

macOS arm64 full-suite results, with project deprecations, unraisable exceptions
and unhandled thread exceptions treated as errors:

| CPython | Passed | Skipped | Warnings |
| --- | ---: | ---: | ---: |
| 3.10.20 | 2,667 | 29 | 3 |
| 3.11.15 | 2,667 | 29 | 3 |
| 3.12.14 | 2,667 | 29 | 7 |
| 3.13.15 | 2,667 | 29 | 7 |
| 3.14.7 | 2,667 | 29 | 7 |
| 3.15.0rc1 (preview) | 2,667 | 29 | 7 |

Three parameterized subtests also passed in each run. The local preview is rc1,
not a claim of rc3 or final-release verification. CI installs the available
3.15 prerelease independently.

Wheel and sdist builds and `twine check` passed. A fresh Python 3.14 environment
ran the installed-wheel memory/disk/ZIP/Unicode smoke check without setuptools
or pkg_resources. The expanded remote matrix must be read from its Actions run;
these local results alone do not establish Linux/Windows success.

Reproduce the suite with:

```sh
python -m pip install -e '.[test]'
python -m pytest tests -q -ra -W error::DeprecationWarning:fs -W error::pytest.PytestUnraisableExceptionWarning -W error::pytest.PytestUnhandledThreadExceptionWarning
```

## Skipped tests

The macOS baseline had 29 skips. Each was reviewed:

| Count | Reason | Treatment |
| ---: | --- | --- |
| 17 | Backend/filesystem is case insensitive | Keep capability-based skip; case-sensitive backends and Linux exercise the corresponding behavior |
| 3 | Backend case sensitivity is unknown | Keep conservative skip; do not claim verified case-sensitive behavior for these backends |
| 3 | Invalid Unicode paths cannot be constructed on macOS | Keep platform condition; Linux/Windows CI remain necessary |
| 1 | Backend does not support Unicode paths | Keep capability condition |
| 5 | Pre-3.8 custom sendfile implementation is inactive | Retain the upstream legacy test as explicitly inactive; supported Python uses shutil.copy2 and existing copy/preserve-time tests |

No skip was removed merely to improve a percentage. Counts vary by OS and
backend capabilities. The old sendfile implementation is a future cleanup
candidate, not an active Python 3.10+ code path.

## Warnings and confirmed fixes

The macOS/Python 3.14 baseline emitted 38 warnings:

- 12 came from `utcnow()` in copy test fixtures: switched to aware UTC datetimes.
- 9 came from `utcfromtimestamp()` in FTP MFMT commands: replaced with
  `fromtimestamp(..., timezone.utc)`, preserving the wire timestamp format.
- 1 came from FTP LIST dates without a year: supply the inferred current year
  before parsing. A leap day now works in a leap year; invalid dates omit the
  optional modified timestamp instead of raising during a directory listing.
  Explicit year 1900 is preserved instead of being mistaken for a default year.
- 5 came from deprecated aliases in doctest setup, and 2 from an FTP test's
  `gettext`: use current names. Public deprecated aliases remain available.
- 2 deliberately exercise deprecated copy helpers: now assert that the warning
  occurs while preserving the read-only behavior check.
- 6 are emitted inside pyftpdlib's MFMT implementation and 1 warns about anonymous
  writes in the loopback FTP fixture. They remain visible. Python 3.10/3.11 also
  report asyncore/asynchat deprecations from the FTP test dependency.

The ZIP writer's missing-modification-time fallback also used `utcnow()` but was
not exercised by the baseline. A regression now checks a valid archive and a UTC
timestamp, with deprecations treated as errors. The production fallback uses an
aware UTC datetime.

CI treats deprecations originating in `fs` as errors, as well as unraisable
exceptions and unhandled thread exceptions. Intentional deprecation behavior is
asserted by tests; third-party warnings are not globally suppressed.

Python 3.15.0rc1 revealed a separate test harness failure: directly calling
`DocTestCase.runTest()` bypasses state initialized by `run()`. The wrapper now
uses the public unittest lifecycle and propagates errors, failures and skips.
Regression checks inject an example failure and a setup error, so a broken
example cannot silently pass. All existing doctests remain collected.

## Uncovered branches and dependencies

- `_fscompat` and `_pathcompat` primarily contain fallbacks for Python versions
  below the supported minimum. Their low coverage is retained in the report;
  executing them through artificial interpreter-version patches would not
  establish supported-runtime compatibility.
- `zipfs` includes a pre-3.7 seek implementation, and `osfs` contains old sendfile
  and scandir fallbacks plus platform-specific error handling. A macOS coverage
  run cannot validate every Windows/Linux branch. Existing cross-platform tests
  remain in CI; no blanket coverage claim is made.
- Added regressions target actual gaps: yearless leap dates, invalid listing
  dates, explicit 1900, ZIP metadata fallback and doctest error propagation.
- Runtime `six` and `appdirs` remain. `six` is used throughout the inherited
  implementation; replacing it is a separate broad cleanup. `AppFS` depends on
  AppDirs path conventions; swapping it needs path-compatibility tests. Neither
  requires setuptools at runtime, and the fresh installed-wheel check verifies
  operation without setuptools/pkg_resources.

## Plugin evidence

The locally adapted `fs-s3fs==1.1.1+fsnext.1` passed normal pip resolution and
`pip check` in fresh macOS Python 3.10 and 3.14 environments, with
`moto==5.2.3`, `boto3==1.43.108` and `botocore==1.43.108`. The real S3 opener
passed text/binary/Unicode, listing, reopen, deletion and missing-object checks.
The required workflow now repeats this on Linux Python 3.10 through 3.14.

See [migration instructions](migration.md) for exact commands and limitations.
SSH, FTPS, hosted FTP and live AWS are still separate unverified work; this
review does not mark the broader remote-backend roadmap items complete.
