"""Unit tests for organic_market_agent.publisher.ftps_upload (mocked FTP)."""
from __future__ import annotations

import ftplib
import ssl
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from organic_market_agent.publisher.ftps_upload import (
    BACKOFF_SECONDS,
    MAX_RETRIES,
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


class TestReusedSessionFTP_TLS:
    """AC-03: Verify the ReusedSessionFTP_TLS subclass wraps data socket with control session.

    This is the core fix for uPress 425 errors — the data connection must present
    the same TLS session ticket as the control connection.
    """

    def test_ntransfercmd_reuses_tls_session_when_prot_p(self):
        """When _prot_p is True, ntransfercmd wraps the data socket using the control session."""
        ftp = ReusedSessionFTP_TLS.__new__(ReusedSessionFTP_TLS)

        # Simulate the control connection TLS session
        mock_session = MagicMock(spec=ssl.SSLSession)
        mock_sock = MagicMock()
        mock_sock.session = mock_session
        ftp.sock = mock_sock
        ftp.host = "ftp.example.com"
        ftp._prot_p = True

        # The wrapped ssl socket that context.wrap_socket should return
        mock_ssl_conn = MagicMock()

        # context wraps the raw data socket
        mock_context = MagicMock(spec=ssl.SSLContext)
        mock_context.wrap_socket.return_value = mock_ssl_conn
        ftp.context = mock_context

        # Raw data connection returned by FTP.ntransfercmd
        mock_raw_conn = MagicMock()
        mock_raw_size = 0

        with patch("ftplib.FTP.ntransfercmd", return_value=(mock_raw_conn, mock_raw_size)):
            conn, size = ftp.ntransfercmd("RETR test.txt")

        # Must call wrap_socket with the control connection's session
        mock_context.wrap_socket.assert_called_once_with(
            mock_raw_conn,
            server_hostname="ftp.example.com",
            session=mock_session,
        )
        assert conn is mock_ssl_conn
        assert size == mock_raw_size

    def test_ntransfercmd_skips_wrap_when_not_prot_p(self):
        """When _prot_p is False (plain FTP data), no TLS wrapping is applied."""
        ftp = ReusedSessionFTP_TLS.__new__(ReusedSessionFTP_TLS)
        ftp._prot_p = False
        ftp.context = MagicMock(spec=ssl.SSLContext)

        mock_raw_conn = MagicMock()
        mock_raw_size = 1024

        with patch("ftplib.FTP.ntransfercmd", return_value=(mock_raw_conn, mock_raw_size)):
            conn, size = ftp.ntransfercmd("RETR test.txt")

        ftp.context.wrap_socket.assert_not_called()
        assert conn is mock_raw_conn
        assert size == mock_raw_size

    def test_is_subclass_of_ftp_tls(self):
        """ReusedSessionFTP_TLS must be a subclass of ftplib.FTP_TLS."""
        assert issubclass(ReusedSessionFTP_TLS, ftplib.FTP_TLS)


class TestRetryBackoff:
    """AC-03: Connection retry/backoff constants and behavior."""

    def test_constants_match_spec(self):
        """MAX_RETRIES=3, BACKOFF_SECONDS=(5, 10, 20) per LOD400 spec."""
        assert MAX_RETRIES == 3
        assert BACKOFF_SECONDS == (5, 10, 20)

    def test_retry_exhaustion_marks_file_failed(self, tmp_artifacts):
        """If all MAX_RETRIES attempts fail, the file is in files_failed."""
        patches = _apply_cfg_patches()
        sleep_calls = []
        try:
            with patch("organic_market_agent.publisher.ftps_upload.ReusedSessionFTP_TLS") as MockFTP:
                with patch("organic_market_agent.publisher.ftps_upload.time.sleep", side_effect=lambda s: sleep_calls.append(s)):
                    mock_ftp = _mock_ftp()
                    MockFTP.return_value = mock_ftp
                    mock_ftp.storbinary.side_effect = OSError("425 data connection failed")

                    result = upload_artifacts(tmp_artifacts, ["public_report.json"])

            assert result.success is False
            assert "public_report.json" in result.files_failed
            # Should sleep between retries: (MAX_RETRIES - 1) times
            assert len(sleep_calls) == MAX_RETRIES - 1
            assert sleep_calls[0] == BACKOFF_SECONDS[0]
            assert sleep_calls[1] == BACKOFF_SECONDS[1]
        finally:
            for p in patches:
                p.stop()


class TestFullArtifactUpload:
    """AC-03: Mock-based test for all four canonical publish artifacts."""

    def test_all_four_canonical_artifacts(self, tmp_artifacts):
        """Upload manifest.json + public_report.json + public_report.html + public_report_body.html."""
        patches = _apply_cfg_patches()
        try:
            with patch("organic_market_agent.publisher.ftps_upload.ReusedSessionFTP_TLS") as MockFTP:
                mock_ftp = _mock_ftp()
                MockFTP.return_value = mock_ftp

                canonical_files = [
                    "public_report.json",
                    "public_report.html",
                    "public_report_body.html",
                    "manifest.json",
                ]
                result = upload_artifacts(tmp_artifacts, canonical_files)

                assert result.success is True
                assert result.files_uploaded == canonical_files
                assert result.files_failed == []
                # One STOR call per file
                assert mock_ftp.storbinary.call_count == 4

                # Verify remote paths use the configured upload base
                stor_cmds = [c.args[0] for c in mock_ftp.storbinary.call_args_list]
                for fname in canonical_files:
                    expected = f"STOR wp-content/uploads/market/{fname}"
                    assert expected in stor_cmds, f"Missing STOR for {fname}"
        finally:
            for p in patches:
                p.stop()
