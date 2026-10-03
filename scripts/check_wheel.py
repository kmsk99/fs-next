"""Run with python -I after installing the wheel in a fresh environment."""

import importlib.util
from importlib.metadata import metadata, version
from pathlib import Path
from tempfile import TemporaryDirectory

import fs
from fs import open_fs
from fs.copy import copy_fs
from fs.zipfs import ZipFS

assert "site-packages" in fs.__file__, fs.__file__
assert importlib.util.find_spec("pkg_resources") is None
assert importlib.util.find_spec("setuptools") is None
assert version("fs-next") == fs.__version__
assert "scandir" in metadata("fs-next").get_all("Provides-Extra", [])
with TemporaryDirectory() as directory:
    with open_fs("mem://") as memory, open_fs(directory) as disk:
        memory.writetext("hello 한글.txt", "FS Next")
        copy_fs(memory, disk)
        assert disk.readtext("hello 한글.txt") == "FS Next"
    archive = str(Path(directory) / "test.zip")
    with ZipFS(archive, write=True) as storage:
        storage.writetext("hello 한글.txt", "zip round trip")
    with ZipFS(archive) as storage:
        assert storage.readtext("hello 한글.txt") == "zip round trip"
print(f"Installed fs-next {version('fs-next')} wheel smoke passed: {fs.__file__}")
