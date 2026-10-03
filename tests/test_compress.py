"""Regression coverage for archive entries without modification metadata."""

import io
import unittest
import warnings
import zipfile
from datetime import datetime, timezone
from unittest.mock import Mock

from fs.compress import write_zip
from fs.info import Info
from fs.memoryfs import MemoryFS


class TestZipMissingTime(unittest.TestCase):
    def test_missing_modified_uses_current_utc(self):
        walker = Mock()
        walker.info.return_value = [
            (
                "/hello.txt",
                Info(
                    {
                        "basic": {"name": "hello.txt", "is_dir": False},
                        "details": {"size": 5, "type": 2},
                    }
                ),
            )
        ]
        output = io.BytesIO()
        before = datetime.now(timezone.utc).replace(microsecond=0)
        with MemoryFS() as storage, warnings.catch_warnings():
            storage.writebytes("hello.txt", b"hello")
            warnings.simplefilter("error", DeprecationWarning)
            write_zip(storage, output, walker=walker)
        after = datetime.now(timezone.utc).replace(microsecond=0)
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.read("hello.txt"), b"hello")
            timestamp = datetime(
                *archive.getinfo("hello.txt").date_time, tzinfo=timezone.utc
            )
            # ZIP stores seconds at two-second resolution.
            self.assertGreaterEqual(timestamp.timestamp(), before.timestamp() - 1)
            self.assertLessEqual(timestamp, after)
