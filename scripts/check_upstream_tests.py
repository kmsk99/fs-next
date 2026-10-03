"""Run the published fs 2.4.16 regression suite against an installed FS Next.

Use CPython 3.10 with pytest, parameterized, pyftpdlib==1.5.10, psutil and
setuptools<81 (the last two are dependencies of the original test harness).
Pass the original PyPI sdist as the sole argument. No tests are deselected.
Four entry-point mock targets are adapted to the replacement discovery backend.
The multiprocessing fixture runs last and joins its closed pool before exiting:
the old FTP fixture otherwise kills Python's resource-tracker child process.
All assertions and original filesystem contract tests remain.
"""

import hashlib
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

import fs

SDIST_SHA256 = "ae97c7d51213f4b70b6a958292530289090de3a7e15841e108fbe144f069d313"


def main():
    if sys.version_info[:2] != (3, 10):
        raise SystemExit("Run the unchanged upstream harness on Python 3.10")
    assert "site-packages" in fs.__file__, fs.__file__
    archive = Path(sys.argv[1])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == SDIST_SHA256
    with TemporaryDirectory(prefix="fs-next-upstream-tests-") as directory:
        root = Path(directory)
        # Copy only regular test/config files, without extracting archive paths.
        with tarfile.open(archive) as source:
            for member in source.getmembers():
                path = PurePosixPath(member.name)
                relative = PurePosixPath(*path.parts[1:])
                if not member.isfile() or ".." in relative.parts:
                    continue
                if relative.parts[:1] == ("tests",) or str(relative) == "setup.cfg":
                    target = root / relative
                elif str(relative) == "fs/test.py":
                    target = root / "original_fs_test.py"
                else:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.extractfile(member).read())

        opener = root / "tests/test_opener.py"
        original = opener.read_text(encoding="utf-8")
        assert original.count('"pkg_resources.iter_entry_points"') == 3
        assert original.count('sys.modules["pkg_resources"], "iter_entry_points"') == 1
        adapted = original.replace(
            'mock.patch("pkg_resources.iter_entry_points", iter_entry_points)',
            'mock.patch.object(sys.modules["fs.opener.registry"], "entry_points", iter_entry_points)',
        ).replace(
            'sys.modules["pkg_resources"], "iter_entry_points"',
            'sys.modules["fs.opener.registry"], "entry_points"',
        )
        opener.write_text(adapted, encoding="utf-8")
        errors_test = root / "tests/test_errors.py"
        original_errors = errors_test.read_text(encoding="utf-8")
        assert original_errors.count("            pool.close()") == 1
        errors_test.write_text(
            original_errors.replace(
                "            pool.close()",
                "            pool.close()\n            pool.join()",
            ),
            encoding="utf-8",
        )
        (root / "conftest.py").write_text(
            "import fs, sys, importlib.util\n"
            "from pathlib import Path\n"
            'assert "site-packages" in fs.__file__, fs.__file__\n'
            'spec = importlib.util.spec_from_file_location("fs.test", '
            'Path(__file__).with_name("original_fs_test.py"))\n'
            "module = importlib.util.module_from_spec(spec)\n"
            'sys.modules["fs.test"] = module\n'
            "spec.loader.exec_module(module)\n"
            "fs.test = module\n"
            "def pytest_collection_modifyitems(items):\n"
            '    items.sort(key=lambda item: item.path.name == "test_errors.py")\n',
            encoding="utf-8",
        )
        print(
            "Original PyPI suite; four discovery mocks retargeted and pool joined; no assertions changed",
            flush=True,
        )
        subprocess.run(
            [
                sys.executable,
                "-I",
                "-m",
                "pytest",
                "-c",
                "setup.cfg",
                "tests",
                "-q",
                "-ra",
            ],
            cwd=root,
            check=True,
            timeout=300,
        )


if __name__ == "__main__":
    main()
