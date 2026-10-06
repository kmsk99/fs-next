# Migrating from PyFilesystem2

FS Next is an independent maintenance fork for Python 3.10+. Keep existing
`import fs`, `from fs import open_fs` and `fs.opener` entry points. Change the
**distribution dependency** from `fs` to `fs-next` and test your application.
The recipes below use the verified stable release **0.1.1**.

## 1. Check whether your dependency chain can migrate

Run these in the original project before changing its environment:

| Manager | Inspect installed or locked dependencies |
| --- | --- |
| pip | `python -m pip show fs` — read `Required-by`; also inspect your requirements files |
| uv | `uv tree --locked --invert --package fs` |
| Poetry | `poetry show --tree` — find packages whose dependencies contain `fs` |

Search your dependency declarations and lock files for `fs`, including optional
extras and development groups. A lock file entry alone does not tell you whether
it is a direct dependency; inspect its parents. For pip, `Required-by` describes
the installed environment, so also review dependencies enabled only in CI or
production.

- **Direct dependency only:** follow one recipe below.
- **A plugin or another library requires `fs`:** first migrate that package's
  dependency metadata. Installing `fs-next` alongside it will not solve this.
- **Python below 3.10:** upgrade the application runtime before switching.

Save the original dependency declarations and lock files in version control.
Keep the original environment available for rollback. Do not install both
packages in one environment: they write overlapping `fs/` files. Uninstalling
one can remove the other's files; rebuild any environment that has contained both.

## 2. Install into a new environment

Use a clean checkout or deactivate the original environment. Create a different
environment name; do not reuse `.venv` if it contains the original package:

```sh
python3.10 -m venv .venv-fsnext
. .venv-fsnext/bin/activate
```

Use any installed Python 3.10+ in place of `python3.10`. On Windows PowerShell:

```powershell
py -3.10 -m venv .venv-fsnext
.\.venv-fsnext\Scripts\Activate.ps1
```

Keep this new environment active for the chosen recipe. Preserve your project's
existing extras, dependency groups and private index configuration.

### pip / requirements.txt

Replace the direct dependency in the **source requirements file**:

```diff
-fs==2.4.16
+fs-next==0.1.1
```

Then install the complete project requirements:

```sh
python -m pip install -r requirements.txt
python -m pip check
```

If `requirements.txt` is generated from `requirements.in`, edit the latter and
regenerate with your existing lock generator first, for example
`pip-compile --generate-hashes requirements.in`. Do not hand-edit a generated
hash-locked file. For a package, update `pyproject.toml`, `setup.cfg` or
`setup.py` instead and reinstall the package. The import names stay unchanged.

### uv projects

From the directory containing `pyproject.toml`, with the new environment active:

```sh
uv remove fs --no-sync
uv add 'fs-next==0.1.1' --no-sync
uv sync --active --locked
uv pip check
```

The first two commands update the project declaration and `uv.lock` without
changing the old environment. `--active` makes sync use the new active virtual
environment. If the dependency is in an optional extra or a dependency group,
use the matching `--optional` / `--group` flags for both edits and select those
groups when syncing. Review and commit both `pyproject.toml` and `uv.lock`.
Run verification with the active `python`, or `uv run --active --locked ...`.

### Poetry 2.x projects

From the directory containing `pyproject.toml`, with the new environment active:

```sh
poetry remove fs --lock
poetry add 'fs-next==0.1.1' --lock
poetry sync
```

`--lock` updates the declaration and lock without installing into the old
environment. Poetry uses the activated virtual environment for `sync`.
Keep the existing group selection (`--with`, `--without`, `--only`) where needed.
Review and commit both `pyproject.toml` and `poetry.lock`. Run the checks below
with the active `python` or `poetry run python`.

## 3. Verify the installed result

First check distribution metadata; a successful `import fs` alone is not enough:

```sh
python -c "from importlib.metadata import version, PackageNotFoundError; print('fs-next', version('fs-next'))"
python -m pip show fs
python -m pip check
```

The second command **must report that `fs` is not installed** (a nonzero exit is
expected). A pure uv environment may not contain pip; use `uv pip show fs` and
`uv pip check` there instead. Then run a minimal round trip:

```python
from fs import open_fs

with open_fs("mem://") as storage:
    storage.writetext("hello.txt", "FS Next")
    assert storage.readtext("hello.txt") == "FS Next"
```

Run the application's own tests and a staging workload. Include the backends,
credentials/configuration, Unicode paths, file timestamps, permissions,
copy/move/overwrite behavior and error handling that the application actually
uses. S3/SSH integration requires the corresponding migrated plugin; a MemoryFS
check does not validate a remote backend. Deploy only after those checks pass.

## 4. Roll back if needed

Restore the original dependency declarations and lock files from your saved
revision. Switch back to the original environment, or build another clean
one from that revision. Run the same application tests before deploying it.
Do not try to roll back by installing `fs` over an environment containing
`fs-next`; overlapping files make that unreliable. Neither migration nor
rollback should modify application data by itself; use a staging copy for tests
that write to real storage.

## Verified plugin status

Checked 2026-10-06. “API probe” is not a supported normal installation path.

| Distribution | Tested version | Current migration status |
| --- | --- | --- |
| Built-in memory/local/temp/AppFS/ZIP/TAR/FTP/FTPS | fs-next 0.1.1 | No external plugin needed; original and modern regression suites pass |
| `fs-s3fs` | Fork commit `49ecaab` | Normal pip installation and 177 emulator/metadata tests pass; [upstream PR #96](https://github.com/PyFilesystem/s3fs/pull/96) is awaiting review; PyPI 1.1.1 still requires `fs` |
| `pyfatfs` | 1.1.0 | FAT API probe passes; public package still requires `fs~=2.4` |
| `fs.sshfs` | 1.0.2 | Public package requires `fs~=2.2`; migration and SSH integration not yet verified |

See the [support policy](support-policy.md) and
[0.1.1 release audit](release-0.1.1.md) for the tested runtime and feature scope.

## Plugins need a dependency metadata change

`fs-next` cannot satisfy `Requires-Dist: fs`. A constraints file or installing
FS Next first does not rename dependencies. Every package in the dependency
chain that requires `fs` must migrate its metadata. Keep its import names and
`fs.opener` entry points unchanged.

The earlier pyfatfs `--no-deps` probe tests API behavior only and leaves an
unsatisfied dependency. Do not use it as a normal installation recipe.

### S3: install the verified migration candidate

The proposed change is [upstream PR #96](https://github.com/PyFilesystem/s3fs/pull/96).
Until it is accepted and released, the public PyPI `fs-s3fs==1.1.1` is **not**
the migrated package. A tested candidate is available from the independent fork
at the immutable commit below. Git must be installed for this VCS requirement.

In a fresh Python 3.10+ environment:

```sh
python -m pip install "fs-s3fs @ git+https://github.com/kmsk99/s3fs.git@49ecaabce3e1dc8c6c6bc4eb1f9353e4db4f2885"
python -m pip check
python -c "from importlib.metadata import version; print(version('fs-next'))"
python -m pip show fs
```

The last command should report that `fs` is absent. This uses normal dependency
resolution, with no `--no-deps` workaround. Keep the **full VCS requirement** in
your dependency declaration and lock; replacing it with `fs-s3fs==1.1.1` selects
the unmigrated PyPI build. In the clean environment, uv accepts the named
requirement; Poetry takes the Git URL directly:

```sh
uv add "fs-s3fs @ git+https://github.com/kmsk99/s3fs.git@49ecaabce3e1dc8c6c6bc4eb1f9353e4db4f2885"
# Or, for a Poetry project:
poetry add "git+https://github.com/kmsk99/s3fs.git@49ecaabce3e1dc8c6c6bc4eb1f9353e4db4f2885"
```

Inspect and commit the resulting declaration and lock file.
The fork retains the upstream version string; the commit/direct URL identifies
the tested candidate, not the version number alone.

The candidate fixes copy/move `preserve_time` argument handling, safe same-path
operations, and binary stream `mode` / `readinto`. S3 controls LastModified;
timestamp preservation remains best effort. CI passes Linux/macOS/Windows ×
Python 3.10/3.14/3.15 preview, with **177 tests per job** covering roots, prefixes
and dependency markers. A fresh public VCS installation passes the same suite.
See [CI evidence](https://github.com/kmsk99/s3fs/actions/runs/37420836208).

This is an upstream review candidate, not an official fs-s3fs release. Moto
validates emulated S3 behavior; run your application's staging tests against
its actual service before deploying. Python below 3.10 retains the original
`fs` dependency through environment markers, but those old runtimes are not
newly certified by this matrix.

### Earlier local S3 metadata probe

The following older probe only changed metadata and exercised basic operations.
Use the tested candidate above for the copy/move and stream compatibility fixes.


This example adapts [fs-s3fs 1.1.1](https://pypi.org/project/fs-s3fs/1.1.1/)
locally. Its original source, MIT license and credits remain intact. The helper
changes only `fs~=2.4` to `fs-next>=0.1.0a1,<0.2` and labels the result
`1.1.1+fsnext.1`. No upstream package has been changed or published.

From this checkout, in a fresh virtual environment with pip:

```sh
mkdir -p .local/plugin-source
python -m pip download --no-deps --no-binary=:all: fs-s3fs==1.1.1 -d .local/plugin-source
tar -xzf .local/plugin-source/fs-s3fs-1.1.1.tar.gz -C .local/plugin-source
python scripts/prepare_s3fs_probe.py .local/plugin-source/fs-s3fs-1.1.1
python -m pip install . ./.local/plugin-source/fs-s3fs-1.1.1 "moto[s3]==5.2.3"
python -m pip check
python scripts/check_s3fs.py
```

`--no-deps` above applies only to downloading the original source. Installation
uses normal dependency resolution. The probe rejects an installed `fs`
distribution and checks the migrated dependency metadata. Re-extract the original
archive before rerunning the preparation helper; it rejects already changed input.

The source archive SHA-256 used for verification is
`b57f8c7664460ff7b451b4b44ca2ea9623a374d74e1284c2d5e6df499dc7976c`.

The check creates a bucket in Moto's in-process emulator and exercises the real
`s3://` entry point: directories, Unicode text, binary data, listing, close and
reopen, removal and missing-object errors. It uses synthetic credentials and
needs no AWS account. This validates local plugin/API integration, not AWS IAM,
TLS, network failures, multipart behavior or hosted S3 service compatibility.

Keep the adapted package as a local/private build. A public plugin release needs
its own ownership, naming and release decision. For a real application, pin the
tested artifact and dependency set in your lock file; do not replace it with an
unmodified PyPI plugin during deployment. SSH and other plugins still need their
own migration and backend tests.

## Recipe verification and references

The direct-dependency recipes were exercised in disposable projects with
Python 3.14, pip, uv 0.12.5 and Poetry 2.5.1. Checks cover updated declarations,
lock regeneration, clean installation, absence of the `fs` distribution and an
unchanged `from fs import open_fs` round trip. This verifies the recipe, not
an arbitrary application's dependency closure or production workload.

- [uv command reference](https://docs.astral.sh/uv/reference/cli/)
- [Poetry command reference](https://python-poetry.org/docs/cli/)
- [Distribution names versus import names](https://packaging.python.org/en/latest/discussions/distribution-package-vs-import-package/)
