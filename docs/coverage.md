# Coverage snapshot

## Stable 0.1.0 audit

Measured 2026-10-04 on macOS CPython 3.14.7 with coverage.py 7.16.2 after adding
the FTPS suite and TLS shutdown fix: **4,980 / 5,368 statements (92.77%)**,
**1,236 / 1,436 branches (86.07%)**, **91.36% combined**. The suite passed
2,757 tests with 30 skips and 10 third-party warnings. Scope and exclusions
remain unchanged. See [release audit](release-0.1.0.md).

## Earlier development snapshot

Follow-up development measurement (2026-10-04, macOS CPython 3.14.7,
coverage.py 7.16.2): **4,972 / 5,358 statements (92.80%)** and
**1,235 / 1,436 branches (86.00%)**, combined **91.36%**. The suite passed
2,667 tests with 29 skips and 7 third-party warnings. Scope and exclusions are
unchanged; see [test review](test-review.md) for the added regressions. The
per-module table below remains the original release baseline.

## Published 0.1.0a1 baseline

Measured 2026-10-03 against `b7f6278da8ff9589d6a27c132cefb439cf8279b7` (0.1.0a1).

- Environment: macOS arm64, CPython 3.14.7, coverage.py 7.16.2.
- Suite: 2,661 passed, 29 skipped, 38 warnings; finalizer/thread warnings treated as errors.
- Statement coverage: **4,975 / 5,361 = 92.80%**.
- Branch coverage: **1,232 / 1,434 = 85.91%**.
- Combined coverage.py score: **6,207 / 6,795 = 91.35%**.
- Scope: `fs/`, excluding `fs/test.py`. Existing coverage rules exclude 91 lines.
- Single-platform run; subprocess-only execution is not collected.

These figures measure test execution, not newly implemented functionality or
upstream API compatibility. Most tested implementation and tests are inherited
from [PyFilesystem2](https://github.com/PyFilesystem/pyfilesystem2).

## Per-module results

Combined scores count statements and branch destinations, as coverage.py does.
Low scores in legacy compatibility modules and platform-specific paths remain
visible; they have not been removed from the denominator.

| Module | Statements covered / total | Branches covered / total | Combined |
| --- | ---: | ---: | ---: |
| `fs/__init__.py` | 8 / 8 | 0 / 0 | 100.00% |
| `fs/_bulk.py` | 84 / 90 | 23 / 24 | 93.86% |
| `fs/_fscompat.py` | 5 / 21 | 0 / 6 | 18.52% |
| `fs/_ftp_parse.py` | 78 / 80 | 18 / 20 | 96.00% |
| `fs/_pathcompat.py` | 2 / 27 | 0 / 8 | 5.71% |
| `fs/_repr.py` | 7 / 8 | 1 / 2 | 80.00% |
| `fs/_typing.py` | 7 / 7 | 0 / 0 | 100.00% |
| `fs/_tzcompat.py` | 9 / 12 | 0 / 0 | 75.00% |
| `fs/_url_tools.py` | 16 / 17 | 5 / 6 | 91.30% |
| `fs/_version.py` | 1 / 1 | 0 / 0 | 100.00% |
| `fs/appfs.py` | 35 / 36 | 1 / 2 | 94.74% |
| `fs/base.py` | 387 / 412 | 91 / 102 | 93.00% |
| `fs/compress.py` | 76 / 81 | 28 / 32 | 92.04% |
| `fs/constants.py` | 3 / 3 | 0 / 0 | 100.00% |
| `fs/copy.py` | 111 / 117 | 35 / 40 | 92.99% |
| `fs/enums.py` | 18 / 18 | 0 / 0 | 100.00% |
| `fs/error_tools.py` | 42 / 46 | 6 / 8 | 88.89% |
| `fs/errors.py` | 137 / 143 | 1 / 2 | 95.17% |
| `fs/filesize.py` | 24 / 25 | 8 / 10 | 91.43% |
| `fs/ftpfs.py` | 552 / 575 | 154 / 176 | 94.01% |
| `fs/glob.py` | 150 / 172 | 61 / 74 | 85.77% |
| `fs/info.py` | 135 / 140 | 15 / 16 | 96.15% |
| `fs/iotools.py` | 116 / 126 | 26 / 30 | 91.03% |
| `fs/lrucache.py` | 20 / 20 | 3 / 4 | 95.83% |
| `fs/memoryfs.py` | 377 / 392 | 117 / 126 | 95.37% |
| `fs/mirror.py` | 56 / 59 | 23 / 26 | 92.94% |
| `fs/mode.py` | 79 / 80 | 19 / 20 | 98.00% |
| `fs/mountfs.py` | 153 / 159 | 25 / 26 | 96.22% |
| `fs/move.py` | 45 / 48 | 8 / 14 | 85.48% |
| `fs/multifs.py` | 206 / 212 | 50 / 52 | 96.97% |
| `fs/opener/__init__.py` | 10 / 10 | 0 / 0 | 100.00% |
| `fs/opener/appfs.py` | 29 / 34 | 10 / 12 | 84.78% |
| `fs/opener/base.py` | 10 / 14 | 1 / 2 | 68.75% |
| `fs/opener/errors.py` | 5 / 5 | 0 / 0 | 100.00% |
| `fs/opener/ftpfs.py` | 26 / 30 | 5 / 6 | 86.11% |
| `fs/opener/memoryfs.py` | 12 / 15 | 1 / 2 | 76.47% |
| `fs/opener/osfs.py` | 15 / 18 | 1 / 2 | 80.00% |
| `fs/opener/parse.py` | 30 / 31 | 7 / 8 | 94.87% |
| `fs/opener/registry.py` | 82 / 85 | 24 / 26 | 95.50% |
| `fs/opener/tarfs.py` | 15 / 18 | 3 / 4 | 81.82% |
| `fs/opener/tempfs.py` | 12 / 15 | 1 / 2 | 76.47% |
| `fs/opener/zipfs.py` | 15 / 18 | 3 / 4 | 81.82% |
| `fs/osfs.py` | 295 / 362 | 73 / 110 | 77.97% |
| `fs/path.py` | 134 / 135 | 55 / 56 | 98.95% |
| `fs/permissions.py` | 135 / 136 | 41 / 42 | 98.88% |
| `fs/subfs.py` | 25 / 27 | 1 / 2 | 89.66% |
| `fs/tarfs.py` | 189 / 206 | 49 / 56 | 90.84% |
| `fs/tempfs.py` | 35 / 36 | 6 / 8 | 93.18% |
| `fs/time.py` | 12 / 16 | 2 / 4 | 70.00% |
| `fs/tools.py` | 34 / 36 | 8 / 10 | 91.30% |
| `fs/tree.py` | 69 / 72 | 22 / 24 | 94.79% |
| `fs/walk.py` | 194 / 199 | 77 / 80 | 97.13% |
| `fs/wildcard.py` | 66 / 67 | 31 / 32 | 97.98% |
| `fs/wrap.py` | 121 / 127 | 11 / 12 | 94.96% |
| `fs/wrapfs.py` | 291 / 302 | 28 / 30 | 96.08% |
| `fs/zipfs.py` | 175 / 212 | 54 / 74 | 80.07% |

## Reproduce

Use the commands in [README → Test coverage](../README.md#test-coverage).
For machine-readable output, follow them with:

```sh
python -m coverage json -o coverage.json
```

Source inventory was compared with upstream baseline
`77a8562785fc37cb2e30bdcd39c133097ba62dce`: 57 Python module paths retained,
8 modified, none removed. This is a file inventory, not a function-by-function
compatibility audit.
