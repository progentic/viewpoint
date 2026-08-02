import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


@dataclass(frozen=True)
class TlsMaterial:
    root_certificate: Path
    root_private_key: Path
    server_certificate: Path
    server_private_key: Path
    metadata: Path


class PerInstallTlsProvisioner:
    def __init__(self, output: Path, hostname: str) -> None:
        self._output = output
        self._hostname = hostname

    def provision(self) -> TlsMaterial:
        self._output.mkdir(parents=True, exist_ok=True, mode=0o700)
        root_key, root_certificate = self._create_root()
        server_key, server_certificate = self._create_server(root_key, root_certificate)
        material = self._material_paths()
        self._write_material(material, root_key, root_certificate, server_key, server_certificate)
        self._write_metadata(material, root_certificate, server_certificate)
        return material

    def _create_root(self):
        key = ec.generate_private_key(ec.SECP256R1())
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Word Researcher Local Root")])
        certificate = self._base_certificate(subject, subject, key.public_key())
        certificate = certificate.add_extension(x509.BasicConstraints(ca=True, path_length=0), True)
        certificate = certificate.add_extension(self._root_key_usage(), True)
        return key, certificate.sign(key, hashes.SHA256())

    def _create_server(self, root_key, root_certificate):
        key = ec.generate_private_key(ec.SECP256R1())
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, self._hostname)])
        certificate = self._base_certificate(
            subject, root_certificate.subject, key.public_key()
        )
        certificate = certificate.add_extension(
            x509.BasicConstraints(ca=False, path_length=None), True
        )
        certificate = certificate.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(self._hostname)]), False
        )
        certificate = certificate.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), False
        )
        return key, certificate.sign(root_key, hashes.SHA256())

    def _base_certificate(self, subject, issuer, public_key):
        now = datetime.now(UTC)
        return (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=825))
        )

    def _root_key_usage(self) -> x509.KeyUsage:
        return x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False,
        )

    def _material_paths(self) -> TlsMaterial:
        return TlsMaterial(
            root_certificate=self._output / "root-ca.pem",
            root_private_key=self._output / "root-ca-key.pem",
            server_certificate=self._output / "server-cert.pem",
            server_private_key=self._output / "server-key.pem",
            metadata=self._output / "tls-metadata.json",
        )

    def _write_material(self, material, root_key, root_certificate, server_key, server_certificate):
        self._atomic_write(material.root_private_key, self._private_key_bytes(root_key), 0o600)
        self._atomic_write(material.server_private_key, self._private_key_bytes(server_key), 0o600)
        self._write_certificate(material.root_certificate, root_certificate)
        self._write_certificate(material.server_certificate, server_certificate)

    def _write_certificate(self, path: Path, certificate: x509.Certificate) -> None:
        self._atomic_write(path, certificate.public_bytes(serialization.Encoding.PEM), 0o644)

    def _write_metadata(self, material, root_certificate, server_certificate):
        metadata = {
            "hostname": self._hostname,
            "rootSha256": root_certificate.fingerprint(hashes.SHA256()).hex(),
            "serverSha256": server_certificate.fingerprint(hashes.SHA256()).hex(),
            "version": 1,
        }
        content = json.dumps(metadata, sort_keys=True, indent=2).encode() + b"\n"
        self._atomic_write(material.metadata, content, 0o600)

    def _private_key_bytes(self, key) -> bytes:
        return key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )

    def _atomic_write(self, target: Path, content: bytes, mode: int) -> None:
        descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
        try:
            os.fchmod(descriptor, mode)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
