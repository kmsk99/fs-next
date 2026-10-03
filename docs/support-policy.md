# Python support policy

FS Next supports **CPython 3.10 and every later minor version** as the project
direction. Package metadata remains `Requires-Python: >=3.10`, without an upper
bound. Future compatibility is a maintenance commitment, not a claim that an
unreleased interpreter has already passed tests.

## Required checks

- The compatibility workflow covers CPython 3.10, 3.11, 3.12, 3.13 and 3.14 on
  Linux, macOS and Windows (15 full-suite jobs).
- Release publishing calls the same compatibility workflow, including plugin
  probes. New stable Python minors must be added to this required matrix.
- The separate Python preview workflow tests 3.15 on all three systems on
  pushes, pull requests and weekly. It allows prerelease interpreters and reports
  failures visibly; it is not part of the release publishing gate.
- When a new minor becomes stable, promote it to the required matrix and point
  the preview job at the next available development minor.
- PyPy, free-threaded builds and other implementations have no verification
  claim yet. Third-party plugins have their own Python and dependency limits.

## Interpreter lifecycle

CPython has no separate LTS designation. Python 3.10 reached upstream end of
life on 2026-10-01. FS Next deliberately retains compatibility with it; this
does not extend CPython's security maintenance. See the
[official version lifecycle](https://devguide.python.org/versions/).

As checked on 2026-10-03, Python 3.15 is still a release candidate, with the final
release scheduled for October 9 in [PEP 790](https://peps.python.org/pep-0790/).

## Evidence

The 0.1.0 release audit compares with the published `fs==2.4.16` package and
runs the expanded matrix, plugin probes and installed-wheel checks. See the
[release audit](release-0.1.0.md) and GitHub Actions for release-specific results.

Patch releases in the 0.1.x series aim to preserve documented API compatibility.
Any intentional incompatible change will be documented in a new minor version.
Third-party package dependencies still need their own migration from `fs`.

Raising the minimum version requires a separately documented project decision.
An upstream Python EOL does not automatically remove FS Next compatibility.

## Known preview issue for 0.1.0

CPython 3.15.0rc2 fails `TestFTPS.test_hash` on Linux, macOS and Windows:
a rejected `hashlib.new("nohash")` call is followed by an SSL `[EVP] unsupported`
error on the existing FTPS control connection. The same sequence reproduces
locally on 3.15.0rc1 with the standard-library `ftplib.FTP_TLS` client, without
FS Next filesystem operations. This narrows the issue to the runtime/TLS stack;
the exact upstream cause has not yet been established. The preview test remains
enabled and failing visibly. Full 3.15 compatibility is not yet verified.
Python 3.10–3.14 pass the same regression in the required matrix.

Evidence: [preview run](https://github.com/kmsk99/fs-next/actions/runs/37133094532)
and [required checks](https://github.com/kmsk99/fs-next/actions/runs/37133094550).
