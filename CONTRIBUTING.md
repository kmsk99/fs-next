# Contributing to FS Next

Start with the setup commands in README.md. Keep public filesystem behavior
compatible unless a change is explicitly documented. Include a regression test
for fixes, and retain upstream copyright notices.

Run `python -m pytest tests -q` after installing `.[test]`. FTP tests use a local
loopback server; no remote service credentials are needed. CI treats unraisable
exceptions and unhandled thread exceptions as errors.

Build artifacts with `python -m build`, check them with `python -m twine check
dist/*`, and test the installed wheel in a fresh environment outside the source
checkout. Do not use editable-install results as evidence that the wheel works.

See [release instructions](docs/releasing.md) for the tag and PyPI workflow.
