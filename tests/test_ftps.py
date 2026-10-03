"""Exercise the inherited FS contract over real loopback TLS control/data sockets."""

import ipaddress
import shutil
import ssl
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler

from fs import open_fs
from fs.errors import UnsupportedHash
from fs.test import FSTestCases

from .test_ftpfs import LocalFTPServer


class TestFTPS(FSTestCases, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="fs-next-ftps-")
        root = Path(cls.directory.name)
        cls.data = root / "data"
        cls.data.mkdir()
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
        now = datetime.now(timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=1))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                    ]
                ),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )
        pem = root / "test.pem"
        pem.write_bytes(
            certificate.public_bytes(serialization.Encoding.PEM)
            + key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )
        authorizer = DummyAuthorizer()
        authorizer.add_user("testing", "testing", str(cls.data), perm="elradfmwT")
        handler = type(
            "RequiredTLSHandler",
            (TLS_FTPHandler,),
            {
                "certfile": str(pem),
                "tls_control_required": True,
                "tls_data_required": True,
                "authorizer": authorizer,
            },
        )
        cls.server = LocalFTPServer(handler)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.directory.cleanup()

    def make_fs(self):
        return open_fs(
            "ftps://testing:testing@{}:{}".format(self.server.host, self.server.port)
        )

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data)
        self.data.mkdir()

    def test_tls_and_reopen(self):
        self.assertIsInstance(self.fs.ftp.sock, ssl.SSLSocket)
        self.fs.writetext("한글.txt", "encrypted round trip")
        with self.make_fs() as reopened:
            self.assertEqual(reopened.readtext("한글.txt"), "encrypted round trip")
            reopened.remove("한글.txt")
        self.assertEqual(self.fs.listdir("/"), [])

    def test_invalid_hash_preserves_tls_connection(self):
        self.fs.writebytes("hash.txt", b"abc")
        connection = self.fs.ftp
        for algorithm in ("nohash", "not-a-digest", ""):
            with self.assertRaises(UnsupportedHash):
                self.fs.hash("hash.txt", algorithm)
            self.assertEqual(self.fs.readbytes("hash.txt"), b"abc")
            self.assertEqual(connection.voidcmd("NOOP")[:3], "200")
            self.assertIs(self.fs.ftp, connection)
