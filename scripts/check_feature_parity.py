"""Emit deterministic behavior results from an installed fs distribution.

Run with python -I in separate upstream and FS Next environments, then compare
the JSON outputs. FTP/FTPS and platform-specific behavior have separate tests.
"""

import importlib
import json
import pkgutil
from pathlib import Path
from tempfile import TemporaryDirectory

import fs
from fs import open_fs
from fs.compress import write_tar, write_zip
from fs.copy import copy_fs
from fs.memoryfs import MemoryFS
from fs.mirror import mirror
from fs.mountfs import MountFS
from fs.move import move_file
from fs.multifs import MultiFS
from fs.opener import registry
from fs.permissions import Permissions
from fs.wrap import read_only


def contents(storage):
    return {
        path: storage.readbytes(path).hex() for path in sorted(storage.walk.files())
    }


def exercise(storage):
    storage.makedirs("docs/nested")
    storage.writetext("docs/한글.txt", "hello 한글")
    storage.writebytes("docs/nested/data.bin", b"\x00\xffpayload")
    with storage.openbin("docs/nested/data.bin", "r+") as stream:
        stream.seek(2)
        assert stream.read(3) == b"pay"
    storage.copy("docs/한글.txt", "docs/copied.txt")
    storage.move("docs/copied.txt", "docs/moved.txt")
    result = {
        "contents": contents(storage),
        "glob": sorted(match.path for match in storage.glob("**/*.txt")),
        "size": storage.getinfo("docs/nested/data.bin", ["details"]).size,
        "subfs": storage.opendir("docs").readtext("한글.txt"),
    }
    with read_only(storage) as readonly:
        try:
            readonly.writetext("forbidden", "no")
        except Exception as error:
            result["readonly_error"] = type(error).__name__
    return result


def main():
    assert "site-packages" in fs.__file__, fs.__file__
    # Import every upstream module, including helpers and extension APIs.
    modules = sorted(m.name for m in pkgutil.walk_packages(fs.__path__, "fs."))
    for module in modules:
        importlib.import_module(module)
    result = {"modules": modules, "protocols": sorted(registry.protocols)}
    with TemporaryDirectory() as directory:
        for name, url in (
            ("memory", "mem://"),
            ("temporary", "temp://"),
            ("disk", directory),
        ):
            with open_fs(url) as storage:
                result[name] = exercise(storage)
        with MemoryFS() as source:
            source.makedirs("nested")
            source.writetext("nested/한글.txt", "archive")
            source.writebytes("binary", b"\x00\xff")
            for kind, writer in (("zip", write_zip), ("tar", write_tar)):
                archive = str(Path(directory) / ("archive." + kind))
                writer(source, archive)
                with open_fs(kind + "://" + archive) as storage:
                    result[kind] = contents(storage)
            with MemoryFS() as destination:
                copy_fs(source, destination)
                result["copy"] = contents(destination)
                move_file(destination, "binary", destination, "moved")
                result["move"] = contents(destination)
                mirror(source, destination)
                result["mirror"] = contents(destination)
        with MountFS() as mounted:
            child = MemoryFS()
            child.writetext("file", "mounted")
            mounted.mount("child", child)
            result["mount"] = contents(mounted)
        with MultiFS() as combined:
            low, high = MemoryFS(), MemoryFS()
            low.writetext("shared", "low")
            high.writetext("shared", "high")
            combined.add_fs("low", low)
            combined.add_fs("high", high, write=True, priority=1)
            combined.writetext("new", "write target")
            result["multi"] = contents(combined)
            assert high.readtext("new") == "write target"
        result["permissions"] = Permissions(mode=0o754).dump()
        with MemoryFS() as storage:
            result["errors"] = []
            for operation in (
                lambda: storage.readbytes("missing"),
                lambda: storage.openbin("/"),
                lambda: storage.removedir("/"),
            ):
                try:
                    operation()
                except Exception as error:
                    result["errors"].append(type(error).__name__)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
