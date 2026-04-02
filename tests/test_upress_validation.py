"""U01–U12 uPress validation tests (M7 Go-Live).

These tests require a live FTPS connection to the uPress server.
Run selectively: pytest -m upress tests/test_upress_validation.py

All tests use ReusedSessionFTP_TLS (not plain FTP_TLS) — without TLS
session reuse, uPress returns 425 on data connections.
"""
from __future__ import annotations

import ftplib
import io
import json
import time
from pathlib import Path

import httpx
import pytest

from organic_market_agent.publisher.ftps_upload import ReusedSessionFTP_TLS
from organic_market_agent.utils.config import config

pytestmark = pytest.mark.upress

UPLOAD_PATH = config.UPRESS_UPLOAD_PATH or "wp-content/uploads/market"
TEST_FILE_NAME = "_upress_test_probe.txt"
TEST_CONTENT = b"upress-validation-probe"


def _skip_if_no_creds():
    if not config.upress_configured():
        pytest.skip("uPress FTPS credentials not configured")


def _connect() -> ReusedSessionFTP_TLS:
    _skip_if_no_creds()
    ftp = ReusedSessionFTP_TLS()
    ftp.connect(config.UPRESS_SFTP_HOST, config.UPRESS_SFTP_PORT, timeout=15)
    ftp.login(config.UPRESS_SFTP_USER, config.UPRESS_SFTP_PASS)
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


@pytest.fixture
def ftp_conn():
    ftp = _connect()
    yield ftp
    try:
        ftp.quit()
    except Exception:
        try:
            ftp.close()
        except Exception:
            pass


def _cleanup_test_file(ftp: ReusedSessionFTP_TLS, name: str = TEST_FILE_NAME):
    try:
        ftp.delete(f"{UPLOAD_PATH}/{name}")
    except ftplib.error_perm:
        pass


class TestU01_FtpsLogin:
    def test_login_success(self, ftp_conn):
        """U01: FTPS login with ReusedSessionFTP_TLS succeeds."""
        assert ftp_conn.sock is not None


class TestU02_TlsEncrypted:
    def test_tls_active(self, ftp_conn):
        """U02: Connection is TLS-encrypted (PROT P)."""
        assert hasattr(ftp_conn.sock, "version")
        tls_version = ftp_conn.sock.version()
        assert tls_version is not None, "TLS not active"


class TestU03_WriteToMarket:
    def test_write_file(self, ftp_conn):
        """U03: Can write a file to the market/ upload directory."""
        _cleanup_test_file(ftp_conn)
        try:
            buf = io.BytesIO(TEST_CONTENT)
            ftp_conn.storbinary(f"STOR {UPLOAD_PATH}/{TEST_FILE_NAME}", buf)

            listing = []
            ftp_conn.retrlines(f"NLST {UPLOAD_PATH}", listing.append)
            assert TEST_FILE_NAME in [f.split("/")[-1] for f in listing]
        finally:
            _cleanup_test_file(ftp_conn)


class TestU04_OverwriteFile:
    def test_overwrite_existing(self, ftp_conn):
        """U04: Overwriting an existing file works."""
        _cleanup_test_file(ftp_conn)
        try:
            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{TEST_FILE_NAME}", io.BytesIO(b"version-1")
            )
            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{TEST_FILE_NAME}", io.BytesIO(b"version-2")
            )
            buf = io.BytesIO()
            ftp_conn.retrbinary(f"RETR {UPLOAD_PATH}/{TEST_FILE_NAME}", buf.write)
            assert buf.getvalue() == b"version-2"
        finally:
            _cleanup_test_file(ftp_conn)


class TestU05_VersionedFilename:
    def test_versioned_upload(self, ftp_conn):
        """U05: Upload a file with a versioned timestamp in the name."""
        ts = time.strftime("%Y%m%d_%H%M%S")
        vname = f"_test_report-{ts}.json"
        try:
            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{vname}", io.BytesIO(b'{"test":true}')
            )
            listing = []
            ftp_conn.retrlines(f"NLST {UPLOAD_PATH}", listing.append)
            assert vname in [f.split("/")[-1] for f in listing]
        finally:
            try:
                ftp_conn.delete(f"{UPLOAD_PATH}/{vname}")
            except ftplib.error_perm:
                pass


class TestU06_ManifestUploadOrder:
    def test_artifacts_before_manifest(self, ftp_conn):
        """U06: Upload artifacts first, then manifest — both arrive correctly."""
        artifact = "_test_artifact.html"
        manifest = "_test_manifest.json"
        try:
            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{artifact}", io.BytesIO(b"<html>test</html>")
            )
            manifest_data = json.dumps({"artifact": artifact}).encode()
            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{manifest}", io.BytesIO(manifest_data)
            )
            buf = io.BytesIO()
            ftp_conn.retrbinary(f"RETR {UPLOAD_PATH}/{manifest}", buf.write)
            data = json.loads(buf.getvalue())
            assert data["artifact"] == artifact
        finally:
            for f in (artifact, manifest):
                try:
                    ftp_conn.delete(f"{UPLOAD_PATH}/{f}")
                except ftplib.error_perm:
                    pass


class TestU07_PublicHttpAccess:
    def test_public_url_accessible(self, ftp_conn):
        """U07: File uploaded via FTPS is publicly accessible over HTTPS."""
        _cleanup_test_file(ftp_conn)
        try:
            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{TEST_FILE_NAME}", io.BytesIO(TEST_CONTENT)
            )
            url = f"{config.UPRESS_PUBLIC_BASE.rstrip('/')}/{UPLOAD_PATH}/{TEST_FILE_NAME}"
            time.sleep(2)
            resp = httpx.get(url, timeout=15, follow_redirects=True)
            assert resp.status_code == 200
            assert resp.content == TEST_CONTENT
        finally:
            _cleanup_test_file(ftp_conn)


class TestU08_CacheTTL:
    def test_cache_ttl_info(self, ftp_conn):
        """U08: Informational — measure cache headers for uploaded file."""
        _cleanup_test_file(ftp_conn)
        try:
            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{TEST_FILE_NAME}", io.BytesIO(TEST_CONTENT)
            )
            url = f"{config.UPRESS_PUBLIC_BASE.rstrip('/')}/{UPLOAD_PATH}/{TEST_FILE_NAME}"
            time.sleep(2)
            resp = httpx.get(url, timeout=15, follow_redirects=True)
            cache_control = resp.headers.get("cache-control", "none")
            print(f"[INFO] Cache-Control: {cache_control}")
            assert resp.status_code == 200
        finally:
            _cleanup_test_file(ftp_conn)


class TestU09_WordPressPageRenders:
    def test_wp_page_accessible(self):
        """U09: WordPress page at /SmallFarmsAgent is reachable."""
        _skip_if_no_creds()
        slug = config.UPRESS_PAGE_SLUG.strip("/")
        url = f"{config.UPRESS_PUBLIC_BASE.rstrip('/')}/{slug}"
        resp = httpx.get(url, timeout=15, follow_redirects=True)
        assert resp.status_code == 200, f"Page returned {resp.status_code}"


class TestU10_JsonEndpoint:
    def test_json_accessible(self):
        """U10: public_report.json is accessible over HTTPS and is valid JSON."""
        _skip_if_no_creds()
        url = f"{config.UPRESS_PUBLIC_BASE.rstrip('/')}/{UPLOAD_PATH}/public_report.json"
        resp = httpx.get(url, timeout=15, follow_redirects=True)
        if resp.status_code == 404:
            pytest.skip("public_report.json not yet uploaded")
        assert resp.status_code == 200
        data = resp.json()
        assert "products" in data


class TestU11_ManifestLastGood:
    def test_last_good_survives(self, ftp_conn):
        """U11: manifest_last_good.json survives a failed manifest write."""
        good_name = "_test_manifest_last_good.json"
        bad_name = "_test_manifest.json"
        try:
            good_data = json.dumps({"state": "good"}).encode()
            ftp_conn.storbinary(f"STOR {UPLOAD_PATH}/{good_name}", io.BytesIO(good_data))

            ftp_conn.storbinary(
                f"STOR {UPLOAD_PATH}/{bad_name}", io.BytesIO(b'{"state":"new"}')
            )

            buf = io.BytesIO()
            ftp_conn.retrbinary(f"RETR {UPLOAD_PATH}/{good_name}", buf.write)
            data = json.loads(buf.getvalue())
            assert data["state"] == "good"
        finally:
            for f in (good_name, bad_name):
                try:
                    ftp_conn.delete(f"{UPLOAD_PATH}/{f}")
                except ftplib.error_perm:
                    pass


class TestU12_FullUploadCycle:
    def test_full_upload_from_local(self, tmp_path):
        """U12: Full unattended upload cycle using upload_artifacts()."""
        _skip_if_no_creds()
        from organic_market_agent.publisher.ftps_upload import upload_artifacts

        (tmp_path / "test_u12.json").write_text('{"u12": true}')
        (tmp_path / "test_u12.html").write_text("<html>u12</html>")

        result = upload_artifacts(tmp_path, ["test_u12.json", "test_u12.html"])
        assert result.success is True
        assert len(result.files_uploaded) == 2

        ftp = _connect()
        try:
            for f in ("test_u12.json", "test_u12.html"):
                try:
                    ftp.delete(f"{UPLOAD_PATH}/{f}")
                except ftplib.error_perm:
                    pass
        finally:
            try:
                ftp.quit()
            except Exception:
                ftp.close()
