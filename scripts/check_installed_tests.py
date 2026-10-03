"""Run the complete test suite against the installed package, outside the checkout.

Use python -I after installing the candidate wheel and tests/requirements.txt.
The copied test package remains importable by multiprocessing child processes.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import fs


def main():
    assert "site-packages" in fs.__file__, fs.__file__
    root = Path(__file__).resolve().parents[1]
    with TemporaryDirectory(prefix="fs-next-installed-tests-") as directory:
        sandbox = Path(directory)
        shutil.copytree(
            root / "tests",
            sandbox / "tests",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        shutil.copy2(root / "setup.cfg", sandbox / "setup.cfg")
        (sandbox / "conftest.py").write_text(
            "def pytest_sessionstart(session):\n"
            "    import fs\n"
            '    assert "site-packages" in fs.__file__, fs.__file__\n',
            encoding="utf-8",
        )
        subprocess.run(
            [
                sys.executable,
                "-I",
                "-m",
                "pytest",
                "tests",
                "-q",
                "-ra",
                "-W",
                "error::pytest.PytestUnraisableExceptionWarning",
                "-W",
                "error::pytest.PytestUnhandledThreadExceptionWarning",
            ],
            cwd=sandbox,
            check=True,
        )


if __name__ == "__main__":
    main()
