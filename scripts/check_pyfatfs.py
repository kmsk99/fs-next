"""Exercise pyfatfs 1.1.0 installed with --no-deps in an isolated environment.

Its Requires-Dist: fs~=2.4 is intentionally unsatisfied: fs-next must not be
installed alongside fs. This probe checks API compatibility, not pip resolution.
"""

from importlib.metadata import PackageNotFoundError, distribution, version
from pathlib import Path
from tempfile import TemporaryDirectory

from fs import open_fs
from pyfatfs.PyFat import PyFat

try:
    distribution("fs")
except PackageNotFoundError:
    pass
else:
    raise RuntimeError("Run this probe without the upstream fs distribution")

with TemporaryDirectory() as directory:
    image = Path(directory) / "volume.img"
    image.touch()
    formatter = PyFat()
    formatter.mkfs(str(image), fat_type=PyFat.FAT_TYPE_FAT12, size=1440 * 1024)
    formatter.close()
    with open_fs("fat://" + str(image)) as storage:
        storage.makedir("documents")
        storage.writetext("documents/hello.txt", "FS Next / FAT round trip")
        assert storage.readtext("documents/hello.txt") == "FS Next / FAT round trip"
    with open_fs("fat://" + str(image)) as storage:
        assert storage.readtext("documents/hello.txt") == "FS Next / FAT round trip"
        storage.remove("documents/hello.txt")
        storage.removedir("documents")
        assert storage.listdir("/") == []

print(f"pyfatfs {version('pyfatfs')} opener and FAT round trip passed")
