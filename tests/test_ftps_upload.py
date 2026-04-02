"""Unit tests for organic_market_agent.publisher.ftps_upload (mocked FTP)."""
from __future__ import annotations

import ftplib
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from organic_market_agent.publisher.ftps_upload import (
    FtpsUploadResult,
    MissingCredentialsError,
    ReusedSessionFTP_TLS,
    upload_artifacts,
)


@pytest.fixture
def tmp_artifacts(tmp_path: Path) -> Path:
    """Create a temporary directory with fake publish artifacts."""
    (tmp_path / "public_report.json").write_text('{"test": true}')
    (tmp_path / "public_report.html").write_text("<html>test</html>")
    (tmp_path / "public_report_body.html").write_text("<div>body</div>")
    (tmp_path / "manifest.json").write_text('{"version": "1"}')
    return tmp_path


def _mock_ftp():
    """Return a MagicMock that behaves like ReusedSessionFTP_TLS."""
    mock = MagicMock(spec=ReusedSessionFTP_TLS)
    mock.connect.return_value = None
    mock.login.return_value = None
    mock.prot_p.return_value = None
    mock.set_pasv.return_value = None
    mock.mkd.side_effect = ftplib.error_perm("already exists")
    mock.storbinary.return_value = "226 Transfer complete"
    mock.quit.return_value = None
    return mock


_CFG_PATCH = {
    "organic_market_agent.publisher.ftps_upload.config.UPRESS_SFTP_HOST": "ftp.example.com",
    "organic_market_agent.publisher.ftps_upload.config.UPRESS_SFTP_PORT": 21,
    "organic_market_agent.publisher.ftps_upload.config.UPRESS_SFTP_USER": "testuser",
    "organic_market_agent.publisher.ftps_upload.config.UPRESS_SFTP_PASS": "testpass",
    "organic_market_agent.publisher.ftps_upload.config.UPRESS_UPLOAD_PATH": "wp-content/uploads/market",
}


def _apply_cfg_patches():
    """Return a list of active patch context managers for config attributes."""
    patches = []
    for attr, val in _CFG_PATCH.items():
        p = patch(attr, val)
        p.start()
        patches.append(p)
    return patches


class TestUploadArtifactsSuccess:
    def test_all_files_uploaded(self, tmp_artifacts):
        patches = _apply_cfg_patches()
        try:
            with patch("organic_market_agent.publisher.ftps_upload.ReusedSessionFTP_TLS") as MockFTP:
                mock_ftp = _mock_ftp()
                MockFTP.return_value = mock_ftp

                files = ["public_report.json", "public_report.html", "manifest.json"]
                result = upload_artifacts(tmp_artifacts, files)

                assert result.success is True
                assert result.files_uploaded == files
                assert result.files_failed == []
                assert result.error is None
                assert mock_ftp.storbinary.call_count == 3
        finally:
            for p in patches:
                p.stop()

    def test_connection_uses_tls(self, tmp_artifacts):
        patches = _apply_cfg_patches()
        try:
            with patch("organic_market_agent.publisher.ftps_upload.ReusedSessionFTP_TLS") as MockFTP:
                mock_ftp = _mock_ftp()
                MockFTP.return_value = mock_ftp

                upload_artifacts(tmp_artifacts, ["public_report.json"])

                mock_ftp.connect.assert_called_once_with("ftp.example.com", 21, timeout=15)
                mock_ftp.login.assert_called_once_with("testuser", "testpass")
                mock_ftp.prot_p.assert_called_once()
                mock_ftp.set_pasv.assert_called_once_with(True)
        finally:
            for p in patches:
                p.stop()


class TestUploadArtifactsFailure:
    def test_partial_failure(self, tmp_artifacts):
        patches = _apply_cfg_patches()
        try:
            with patch("organic_market_agent.publisher.ftps_upload.ReusedSessionFTP_TLS") as MockFTP:
                with patch("organic_market_agent.publisher.ftps_upload.time.sleep"):
                    mock_ftp = _mock_ftp()
                    MockFTP.return_value = mock_ftp

                    def storbinary_side_effect(cmd, fh):
                        if "manifest.json" in cmd:
                            raise OSError("connection reset")
                        return "226 Transfer complete"

                    mock_ftp.storbinary.side_effect = storbinary_side_effect

                    files = ["public_report.json", "manifest.json"]
                    result = upload_artifacts(tmp_artifacts, files)

                    assert result.success is False
                    assert "public_report.json" in result.files_uploaded
                    assert "manifest.json" in result.files_failed
        finally:
            for p in patches:
                p.stop()

    def test_total_connection_failure(self, tmp_artifacts):
        patches = _apply_cfg_patches()
        try:
            with patch("organic_market_agent.publisher.ftps_upload._connect") as mock_connect:
                mock_connect.side_effect = OSError("connection refused")
                result = upload_artifacts(tmp_artifacts, ["public_report.json"])

                assert result.success is False
                assert result.error is not None
                assert "connection refused" in result.error
        finally:
            for p in patches:
                p.stop()

    def test_missing_local_file(self, tmp_artifacts):
        patches = _apply_cfg_patches()
        try:
            with patch("organic_market_agent.publisher.ftps_upload.ReusedSessionFTP_TLS") as MockFTP:
                mock_ftp = _mock_ftp()
                MockFTP.return_value = mock_ftp

                result = upload_artifacts(tmp_artifacts, ["nonexistent.json"])

                assert result.success is False
                assert "nonexistent.json" in result.files_failed
        finally:
            for p in patches:
                p.stop()


class TestUploadArtifactsDryRun:
    def test_dry_run_no_connection(self, tmp_artifacts):
        patches = _apply_cfg_patches()
        try:
            result = upload_artifacts(tmp_artifacts, ["public_report.json"], dry_run=True)
            assert result.success is True
            assert result.files_uploaded == ["public_report.json"]
        finally:
            for p in patches:
                p.stop()


class TestMissingCredentials:
    def test_raises_environment_error(self, tmp_artifacts):
        empty_patches = []
        for attr in ("UPRESS_SFTP_HOST", "UPRESS_SFTP_USER", "UPRESS_SFTP_PASS"):
            p = patch(f"organic_market_agent.publisher.ftps_upload.config.{attr}", "")
            p.start()
            empty_patches.append(p)
        try:
            with pytest.raises(MissingCredentialsError, match="FTPS credentials not configured"):
                upload_artifacts(tmp_artifacts, ["public_report.json"])
        finally:
            for p in empty_patches:
                p.stop()


class TestFtpQuitCleanup:
    def test_quit_called_on_success(self, tmp_artifacts):
        patches = _apply_cfg_patches()
        try:
            with patch("organic_market_agent.publisher.ftps_upload.ReusedSessionFTP_TLS") as MockFTP:
                mock_ftp = _mock_ftp()
                MockFTP.return_value = mock_ftp

                upload_artifacts(tmp_artifacts, ["public_report.json"])

                mock_ftp.quit.assert_called_once()
        finally:
            for p in patches:
                p.stop()
