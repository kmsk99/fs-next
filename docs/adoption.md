# Adoption work

Status checked 2026-10-06. This records completed work and external dependencies;
a proposed change is not counted as adoption.

## 1. Migration guide — completed

[Migration recipes](migration.md) cover pip, uv and Poetry, dependency inspection,
fresh environments, lock changes, verification and rollback. All three direct
migration recipes passed in disposable Python 3.14 projects. Documentation builds
with warnings treated as errors.

## 2. S3 normal installation — independent PyPI release available

[`fs-s3fs-next` 0.1.0](https://pypi.org/project/fs-s3fs-next/0.1.0/) provides
the normal PyPI installation route. It requires Python >=3.10 and depends on
`fs-next`, preserving `fs_s3fs` imports and the `s3://` opener. The original
MIT license and history are retained in the
[independent repository](https://github.com/kmsk99/fs-s3fs-next).

Wheel and sdist checks pass, and installed-package tests cover Python
3.10–3.15 preview on Linux/macOS/Windows with 180 tests per environment.
[Release CI](https://github.com/kmsk99/fs-s3fs-next/actions/runs/37426658536)
gates PyPI publishing on these checks. A fresh public PyPI install was verified
with dependency checks, the S3 opener and the same contract tests.

The [guide](migration.md#s3-install-the-independent-pypi-package) covers
installation, distribution conflicts and rollback. Moto tests do not certify
live AWS IAM or provider-specific behavior. Other packages that require the
original distribution names still need dependency metadata changes.

[Upstream PR #96](https://github.com/PyFilesystem/s3fs/pull/96) remains available
for review, but its acceptance is not required to install the independent
package. The original `fs-s3fs` PyPI distribution has not been replaced.

## 3. Downstream pilots — first tested proposal submitted

| Candidate | Evidence of need | Next validation / blocker |
| --- | --- | --- |
| [tilekiln](https://github.com/pnorman/tilekiln/issues/73) | Open migration issue; current pyproject requires Python >=3.10 and directly depends on fs | [Draft PR #77](https://github.com/pnorman/tilekiln/pull/77): dependency/lock change, 20 tests pass on Python 3.10 and 3.14; Linux CI and live database integration remain unverified |
| [pyctr](https://github.com/ihaveamac/pyctr/issues/48) | Wants a maintained compatible implementation; current pyproject requires Python >=3.12, fs and pyfatfs | pyfatfs still requires fs, so first prepare a normal-resolver pyfatfs migration; retain filesystem/image tests |
| [Open edX](https://github.com/openedx/openedx-platform/issues/38068) | Tracks setuptools constraint caused by fs/pkg_resources | Recheck current dependency closure and test infrastructure; an issue alone does not establish that a one-line replacement is sufficient |

Do not advertise any of these as users or successful migrations. Each needs its
own tested change and maintainer acceptance. The tilekiln proposal also verifies disk-backed config/SQL-template loading and
removes the setuptools runtime pin. Linux-targeted mypy passes; native macOS
CLI/mypy encounter the same existing `os.sched_getaffinity` issue before and
after migration. The fork did not create a GitHub Actions run for the push, so
the PR remains a draft pending Linux runtime verification. pyctr requires
plugin work first.

## 4. Community announcement — pending

After concrete downstream evidence, prepare a concise announcement for the
[existing replacement discussion](https://github.com/PyFilesystem/pyfilesystem2/issues/598).
Include independent-fork status, unchanged import paths, actual tested scope,
installation conflicts, plugin status and links to successful migrations.
No announcement has been posted as part of this work.
