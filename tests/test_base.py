"""Test (abstract) base FS class."""

from __future__ import unicode_literals

import unittest
import hashlib

from fs import errors
from fs.base import FS
from fs.memoryfs import MemoryFS


class DummyFS(FS):
    def getinfo(self, path, namespaces=None):
        pass

    def listdir(self, path):
        pass

    def makedir(self, path, permissions=None, recreate=False):
        pass

    def openbin(self, path, mode="r", buffering=-1, **options):
        pass

    def remove(self, path):
        pass

    def removedir(self, path):
        pass

    def setinfo(self, path, info):
        pass


class TestBase(unittest.TestCase):
    def setUp(self):
        self.fs = DummyFS()

    def test_hash_algorithms_and_aliases(self):
        with MemoryFS() as filesystem:
            filesystem.writebytes("data", b"abc")
            names = hashlib.algorithms_available | {"SHA256", "sha-256", "SHA2-256"}
            for name in sorted(names):
                with self.subTest(name=name):
                    try:
                        expected = hashlib.new(name, b"abc").hexdigest()
                    except (ValueError, TypeError):
                        # Availability depends on OpenSSL; XOF hashes require
                        # a digest length that the original FS.hash API lacks.
                        continue
                    self.assertEqual(filesystem.hash("data", name), expected)

    def test_hash_error_types(self):
        with MemoryFS() as filesystem:
            filesystem.writebytes("data", b"abc")
            with self.assertRaises(errors.UnsupportedHash):
                filesystem.hash("data", "nohash")
            with self.assertRaises(TypeError):
                filesystem.hash("data", None)
            with self.assertRaises(errors.ResourceNotFound):
                filesystem.hash("missing", "sha256")

    def test_validatepath(self):
        """Test validatepath method."""
        with self.assertRaises(TypeError):
            self.fs.validatepath(b"bytes")

        self.fs._meta["invalid_path_chars"] = "Z"
        with self.assertRaises(errors.InvalidCharsInPath):
            self.fs.validatepath("Time for some ZZZs")

        self.fs.validatepath("fine")
        self.fs.validatepath("good.fine")

        self.fs._meta["invalid_path_chars"] = ""
        self.fs.validatepath("Time for some ZZZs")

        def mock_getsyspath(path):
            return path

        self.fs.getsyspath = mock_getsyspath

        self.fs._meta["max_sys_path_length"] = 10

        self.fs.validatepath("0123456789")
        self.fs.validatepath("012345678")
        self.fs.validatepath("01234567")

        with self.assertRaises(errors.InvalidPath):
            self.fs.validatepath("0123456789A")
