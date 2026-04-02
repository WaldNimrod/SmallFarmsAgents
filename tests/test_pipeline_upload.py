"""Integration test: pipeline FTPS upload phase (mocked FTP, real pipeline logic)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from organic_market_agent.publisher.ftps_upload import FtpsUploadResult


class TestPipelineUploadIntegration:
    """Verify the pipeline correctly calls upload_artifacts when upload is enabled."""

    @patch("organic_market_agent.scheduler.pipeline.upload_artifacts")
    def test_upload_called_when_enabled(self, mock_upload):
        """When publish succeeds and upload_enabled=True, upload_artifacts is invoked."""
        mock_upload.return_value = FtpsUploadResult(
            success=True,
            files_uploaded=["public_report.json", "manifest.json"],
            files_failed=[],
            remote_base="wp-content/uploads/market",
        )

        from organic_market_agent.scheduler.pipeline import run_pipeline

        publish_summary = {
            "output_dir": "/tmp/test_output",
            "files": ["public_report.json", "manifest.json"],
            "artifact_version": "20260402_120000",
        }

        with (
            patch("organic_market_agent.scheduler.pipeline.SessionFactory") as MockSF,
            patch("organic_market_agent.scheduler.pipeline.config") as mock_config,
            patch("organic_market_agent.scheduler.pipeline.PublishEngine") as MockPE,
            patch("organic_market_agent.scheduler.pipeline._get_active_sources_with_profiles") as mock_sources,
            patch("organic_market_agent.scheduler.pipeline.execute_ingestion_for_run"),
            patch("organic_market_agent.scheduler.pipeline.NormalizerEngine"),
            patch("organic_market_agent.scheduler.pipeline.AggregatorEngine"),
            patch("organic_market_agent.scheduler.pipeline.register_pipeline_run"),
            patch("organic_market_agent.scheduler.pipeline.unregister_pipeline_run"),
            patch("organic_market_agent.scheduler.pipeline.merge_run_progress"),
            patch("organic_market_agent.scheduler.pipeline.persist_log"),
            patch("organic_market_agent.scheduler.pipeline.persist_error_log"),
        ):
            mock_config.ensure_dirs.return_value = None
            mock_config.upress_configured.return_value = True

            mock_session = MagicMock()
            MockSF.return_value.__enter__ = MagicMock(return_value=mock_session)
            MockSF.return_value.__exit__ = MagicMock(return_value=False)

            mock_run = MagicMock()
            mock_run.status = "running"
            mock_run.sources_failed = 0
            mock_run.sources_succeeded = 2
            mock_run.community_sources_succeeded = 2
            mock_run.notes = ""
            mock_run.triggered_by = "test"
            mock_run.finished_at = None
            mock_session.get.return_value = mock_run

            mock_source = MagicMock()
            mock_source.code = "test_source"
            mock_sources.return_value = [(mock_source, MagicMock())]

            MockPE.return_value.run.return_value = publish_summary

            mock_cfg_row = MagicMock()
            mock_cfg_row.upload_enabled = True
            mock_session.scalars.return_value.first.return_value = mock_cfg_row

            run_pipeline(1, skip_upload=False)

            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            assert call_args[0][1] == ["public_report.json", "manifest.json"]

    @patch("organic_market_agent.scheduler.pipeline.upload_artifacts")
    def test_upload_skipped_when_disabled(self, mock_upload):
        """When skip_upload=True, upload_artifacts is never called."""
        from organic_market_agent.scheduler.pipeline import run_pipeline

        with (
            patch("organic_market_agent.scheduler.pipeline.SessionFactory") as MockSF,
            patch("organic_market_agent.scheduler.pipeline.config") as mock_config,
            patch("organic_market_agent.scheduler.pipeline.PublishEngine") as MockPE,
            patch("organic_market_agent.scheduler.pipeline._get_active_sources_with_profiles") as mock_sources,
            patch("organic_market_agent.scheduler.pipeline.execute_ingestion_for_run"),
            patch("organic_market_agent.scheduler.pipeline.NormalizerEngine"),
            patch("organic_market_agent.scheduler.pipeline.AggregatorEngine"),
            patch("organic_market_agent.scheduler.pipeline.register_pipeline_run"),
            patch("organic_market_agent.scheduler.pipeline.unregister_pipeline_run"),
            patch("organic_market_agent.scheduler.pipeline.merge_run_progress"),
            patch("organic_market_agent.scheduler.pipeline.persist_log"),
            patch("organic_market_agent.scheduler.pipeline.persist_error_log"),
        ):
            mock_config.ensure_dirs.return_value = None

            mock_session = MagicMock()
            MockSF.return_value.__enter__ = MagicMock(return_value=mock_session)
            MockSF.return_value.__exit__ = MagicMock(return_value=False)

            mock_run = MagicMock()
            mock_run.status = "running"
            mock_run.sources_failed = 0
            mock_run.sources_succeeded = 2
            mock_run.community_sources_succeeded = 2
            mock_run.notes = ""
            mock_run.triggered_by = "test"
            mock_run.finished_at = None
            mock_session.get.return_value = mock_run

            mock_source = MagicMock()
            mock_source.code = "test_source"
            mock_sources.return_value = [(mock_source, MagicMock())]

            MockPE.return_value.run.return_value = {
                "output_dir": "/tmp/test",
                "files": ["test.json"],
                "artifact_version": "20260402_120000",
            }

            run_pipeline(1, skip_upload=True)

            mock_upload.assert_not_called()
