# FS Next

Independent maintenance fork of PyFilesystem2; see README.md and
docs/fs-next-status.md. Preserve upstream LICENSE and git history.

- Keep the `fs` import and `fs.opener` entry-point group compatible.
- Do not reintroduce a runtime setuptools/pkg_resources dependency.
- Python 3.10+ is the initial development target; report verified versions separately.
- Read and run existing regression tests before broad rewrites.
- Keep `fs` / `fs-next` distribution conflicts and plugin dependency migration explicit.
- Public publishing requires an actual release request and configured ownership.
- Do not store tokens in repository files.

