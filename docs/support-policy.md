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

The published 0.1.0a1 release passed 9 CI jobs (3.10, 3.12, 3.14 × three OSes).
The expanded workflow configuration does not retroactively establish 15 passing
release jobs. Local follow-up results and remaining gaps are recorded in
[test review](test-review.md); consult GitHub Actions for remote run results.

Raising the minimum version requires a separately documented project decision.
An upstream Python EOL does not automatically remove FS Next compatibility.
