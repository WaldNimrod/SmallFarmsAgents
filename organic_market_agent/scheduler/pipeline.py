"""Full pipeline: ingestion for an existing run, then normalize, aggregate, publish, upload."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from organic_market_agent.aggregator.engine import AggregatorEngine
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models import IngestionRun, PipelineAlert, SchedulerConfig
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.publisher.engine import PublishEngine
from organic_market_agent.publisher.upload_dispatch import (
    NoUploadConfigured,
    UploadResult,
    dispatch_upload,
)
from organic_market_agent.scheduler.pipeline_cancel import (
    PipelineRunCancelled,
    is_cancelled,
    register_pipeline_run,
    unregister_pipeline_run,
)
from organic_market_agent.scheduler.run_ingestion import (
    _get_active_sources_with_profiles,
    execute_ingestion_for_run,
)
from organic_market_agent.scheduler.run_progress import merge_run_progress
from organic_market_agent.utils.config import config
from organic_market_agent.utils.exceptions import PublishAbortError
from organic_market_agent.utils.log_persist import persist_error_log, persist_log
from organic_market_agent.utils.logging_setup import get_logger
from organic_market_agent.utils.pipeline_alert_tags import (
    TAG_FTPS_UPLOAD_FAILURE,
    TAG_FTPS_UPLOAD_PARTIAL,
    TAG_FTPS_UPLOAD_SUCCESS,
    TAG_PIPELINE_FAILURE,
    TAG_PIPELINE_MISSING_RUN,
    TAG_PIPELINE_NO_ACTIVE_SOURCES,
    TAG_PIPELINE_PUBLISH_ABORT,
    TAG_PIPELINE_UNFINISHED,
    TAG_SIMULATION_TEST,
    tagged_message,
)

# Upload protocol tags (WP REST primary via WP008)
_TAG_UPLOAD_SUCCESS = "[UPLOAD:ok]"
_TAG_UPLOAD_FAILURE = "[UPLOAD:fail]"
_TAG_UPLOAD_PARTIAL = "[UPLOAD:partial]"

logger = get_logger(__name__)


def _exit_if_cancelled(ingestion_run_id: int) -> bool:
    """If cancel was requested, mark run failed when still running and return True."""
    if not is_cancelled(ingestion_run_id):
        return False
    try:
        with SessionFactory() as session:
            run = session.get(IngestionRun, ingestion_run_id)
            if run is not None and run.status == "running":
                run.status = "failed"
                run.finished_at = datetime.now(timezone.utc)
                note = (run.notes or "").strip()
                run.notes = (note + " " if note else "") + "marked_failed:cancelled"
                merge_run_progress(session, ingestion_run_id, phase="cancelled")
                session.commit()
            elif run is not None:
                merge_run_progress(session, ingestion_run_id, phase="cancelled")
                session.commit()
    except Exception:
        logger.exception("run_pipeline: cancel cleanup failed for ingestion_run_id=%s", ingestion_run_id)
    return True


def run_pipeline(
    ingestion_run_id: int,
    *,
    source_code: str | None = None,
    skip_normalize: bool = False,
    skip_publish: bool = False,
    skip_upload: bool = False,
    retry_attempts: int = 2,
) -> None:
    """Background worker: collect/parse, optional normalizer, aggregator (today UTC), optional publish, optional FTPS upload."""
    config.ensure_dirs()
    registered = False
    try:
        with SessionFactory() as session:
            ingestion_run = session.get(IngestionRun, ingestion_run_id)
            if ingestion_run is None:
                logger.error("run_pipeline: IngestionRun id=%s not found", ingestion_run_id)
                with SessionFactory() as s2:
                    s2.add(
                        PipelineAlert(
                            level="error",
                            message=tagged_message(
                                TAG_PIPELINE_MISSING_RUN,
                                f"run_pipeline: IngestionRun id={ingestion_run_id} not found "
                                "(removed or never committed before worker started).",
                            ),
                            ingestion_run_id=None,
                        )
                    )
                    s2.commit()
                return
            pairs = _get_active_sources_with_profiles(session)
            if source_code:
                pairs = [(s, p) for s, p in pairs if s.code == source_code]
            if not pairs:
                msg = (
                    f"No active source+fetch_profile for code={source_code!r} at pipeline start "
                    f"(source or profile may have been deactivated after the run was queued)."
                    if source_code
                    else "No active sources with fetch profiles at pipeline start"
                )
                logger.warning("run_pipeline: %s (ingestion_run_id=%s)", msg, ingestion_run_id)
                ingestion_run.sources_total = 0
                ingestion_run.sources_succeeded = 0
                ingestion_run.sources_failed = 0
                ingestion_run.community_sources_succeeded = 0
                ingestion_run.finished_at = datetime.now(timezone.utc)
                ingestion_run.status = "failed"
                session.add(
                    PipelineAlert(
                        level="error",
                        message=tagged_message(TAG_PIPELINE_NO_ACTIVE_SOURCES, msg),
                        ingestion_run_id=ingestion_run_id,
                    )
                )
                persist_log(
                    session,
                    level="ERROR",
                    module="scheduler.pipeline",
                    message=msg,
                    ingestion_run_id=ingestion_run_id,
                    extra={"source_filter": source_code},
                )
                session.commit()
                return

            register_pipeline_run(ingestion_run_id)
            registered = True

            merge_run_progress(
                session,
                ingestion_run_id,
                phase="pipeline_start",
                skip_normalize=skip_normalize,
                skip_publish=skip_publish,
            )
            persist_log(
                session,
                level="INFO",
                module="scheduler.pipeline",
                message="Full pipeline: starting ingestion phase",
                ingestion_run_id=ingestion_run_id,
                extra={
                    "source_filter": source_code,
                    "active_pairs": len(pairs),
                    "source_codes": [s.code for s, _ in pairs],
                    "skip_normalize": skip_normalize,
                    "skip_publish": skip_publish,
                    "retry_attempts": retry_attempts,
                },
            )

            execute_ingestion_for_run(
                session,
                ingestion_run,
                pairs,
                retry_attempts=retry_attempts,
                defer_terminal_status=True,
            )
            persist_log(
                session,
                level="INFO",
                module="scheduler.pipeline",
                message=(
                    f"Ingestion stored: logical counters ok={ingestion_run.sources_succeeded} "
                    f"failed={ingestion_run.sources_failed}"
                ),
                ingestion_run_id=ingestion_run_id,
                extra={
                    "sources_succeeded": ingestion_run.sources_succeeded,
                    "sources_failed": ingestion_run.sources_failed,
                    "community_sources_succeeded": ingestion_run.community_sources_succeeded,
                },
            )
            session.commit()

        if _exit_if_cancelled(ingestion_run_id):
            return

        if not skip_normalize:
            with SessionFactory() as session:
                merge_run_progress(session, ingestion_run_id, phase="normalize")
                session.commit()
            ncounts: dict[str, int] = {}
            with SessionFactory() as session:
                ncounts = NormalizerEngine().run(session, ingestion_run_id=ingestion_run_id)
            with SessionFactory() as log_session:
                persist_log(
                    log_session,
                    level="INFO",
                    module="scheduler.pipeline",
                    message=(
                        f"Normalizer finished: resolved={ncounts.get('resolved', 0)} "
                        f"unresolvable={ncounts.get('unresolvable', 0)} "
                        f"scope_skipped={ncounts.get('scope_skipped', 0)} "
                        f"skipped={ncounts.get('skipped', 0)}"
                    ),
                    ingestion_run_id=ingestion_run_id,
                    extra=dict(ncounts),
                )
                merge_run_progress(
                    log_session,
                    ingestion_run_id,
                    phase="normalize_done",
                    normalizer_resolved=ncounts.get("resolved"),
                    normalizer_unresolvable=ncounts.get("unresolvable"),
                    normalizer_scope_skipped=ncounts.get("scope_skipped"),
                    normalizer_skipped=ncounts.get("skipped"),
                )
                log_session.commit()

        if _exit_if_cancelled(ingestion_run_id):
            return

        agg_date = datetime.now(timezone.utc).date()
        with SessionFactory() as session:
            merge_run_progress(session, ingestion_run_id, phase="aggregate", aggregate_date=agg_date.isoformat())
            session.commit()
        agg_result: dict[str, int] = {}
        with SessionFactory() as session:
            agg_result = AggregatorEngine().run(session, agg_date)
        with SessionFactory() as log_session:
            persist_log(
                log_session,
                level="INFO",
                module="scheduler.pipeline",
                message=(
                    f"Aggregator finished: created={agg_result.get('created', 0)} "
                    f"updated={agg_result.get('updated', 0)} "
                    f"date={agg_date.isoformat()}"
                ),
                ingestion_run_id=ingestion_run_id,
                extra={**agg_result, "aggregate_date": agg_date.isoformat()},
            )
            merge_run_progress(
                log_session,
                ingestion_run_id,
                phase="aggregate_done",
                aggregate_created=agg_result.get("created"),
                aggregate_updated=agg_result.get("updated"),
            )
            log_session.commit()

        if _exit_if_cancelled(ingestion_run_id):
            return

        publish_summary: dict[str, object] | None = None
        publish_aborted: str | None = None
        if not skip_publish:
            with SessionFactory() as session:
                merge_run_progress(session, ingestion_run_id, phase="publish")
                session.commit()
            with SessionFactory() as session:
                try:
                    publish_summary = PublishEngine().run(session, Path("output/public"))
                except PublishAbortError as exc:
                    logger.warning("run_pipeline: publish aborted: %s", exc)
                    publish_aborted = str(exc)
                    with SessionFactory() as s3:
                        s3.add(
                            PipelineAlert(
                                level="warning",
                                message=tagged_message(TAG_PIPELINE_PUBLISH_ABORT, f"Publish aborted: {exc}"),
                                ingestion_run_id=ingestion_run_id,
                            )
                        )
                        persist_log(
                            s3,
                            level="WARNING",
                            module="scheduler.pipeline",
                            message=f"Publish aborted: {exc}",
                            ingestion_run_id=ingestion_run_id,
                            extra={"reason": str(exc)},
                        )
                        s3.commit()

        # --- Upload phase (WP REST primary, FTPS fallback — WP008 / F-190-01 fix) ---
        upload_result_summary: dict[str, object] | None = None
        if not skip_upload and publish_summary is not None:
            upload_enabled = False
            with SessionFactory() as session:
                cfg = session.scalars(
                    __import__("sqlalchemy").select(SchedulerConfig).limit(1)
                ).first()
                upload_enabled = cfg.upload_enabled if cfg else False

            if upload_enabled and config.upress_configured():
                with SessionFactory() as session:
                    merge_run_progress(session, ingestion_run_id, phase="upload")
                    session.commit()
                try:
                    output_dir = Path(publish_summary.get("output_dir", "output/public"))
                    result: UploadResult = dispatch_upload(output_dir)
                    upload_result_summary = {
                        "protocol": result.protocol_used,
                        "success": result.success,
                        "success_count": result.success_count,
                        "total_count": result.total_count,
                        "errors": result.errors,
                    }
                    with SessionFactory() as session:
                        if result.success:
                            # Protocol-aware success message
                            if result.protocol_used == "wp_rest":
                                msg = (
                                    f"WP REST upload OK: {result.success_count} artifacts uploaded"
                                )
                            else:
                                msg = (
                                    f"FTPS upload OK: {result.success_count} files to {result.remote_base}"
                                )
                            session.add(PipelineAlert(
                                level="info",
                                message=tagged_message(_TAG_UPLOAD_SUCCESS, msg),
                                ingestion_run_id=ingestion_run_id,
                            ))
                        elif result.success_count > 0:
                            err_detail = "; ".join(result.errors) if result.errors else "see logs"
                            session.add(PipelineAlert(
                                level="warning",
                                message=tagged_message(
                                    _TAG_UPLOAD_PARTIAL,
                                    f"{result.protocol_used.upper()} partial: "
                                    f"{result.success_count} ok, "
                                    f"{result.total_count - result.success_count} failed — {err_detail}",
                                ),
                                ingestion_run_id=ingestion_run_id,
                            ))
                        else:
                            err_detail = "; ".join(result.errors) if result.errors else "all files failed"
                            session.add(PipelineAlert(
                                level="error",
                                message=tagged_message(
                                    _TAG_UPLOAD_FAILURE,
                                    f"{result.protocol_used.upper()} upload FAILED: {err_detail}",
                                ),
                                ingestion_run_id=ingestion_run_id,
                            ))
                        merge_run_progress(session, ingestion_run_id, phase="upload_done")
                        session.commit()
                except NoUploadConfigured as exc:
                    logger.warning("run_pipeline: no upload method configured, skipping upload: %s", exc)
                except Exception as exc:
                    logger.error("run_pipeline: upload unexpected error: %s", exc)
                    with SessionFactory() as session:
                        session.add(PipelineAlert(
                            level="error",
                            message=tagged_message(
                                _TAG_UPLOAD_FAILURE,
                                f"Upload error: {exc}",
                            ),
                            ingestion_run_id=ingestion_run_id,
                        ))
                        session.commit()

        with SessionFactory() as session:
            run = session.get(IngestionRun, ingestion_run_id)
            if run is not None:
                if run.status == "running":
                    run.status = (
                        "completed"
                        if run.sources_failed == 0
                        else ("partial" if run.sources_succeeded > 0 else "failed")
                    )
                run.finished_at = datetime.now(timezone.utc)
                merge_run_progress(
                    session,
                    ingestion_run_id,
                    phase="done",
                    skip_normalize=skip_normalize,
                    skip_publish=skip_publish,
                    publish_summary=publish_summary,
                    publish_aborted=publish_aborted,
                    upload_result=upload_result_summary,
                )
                session.commit()
        with SessionFactory() as log_session:
            persist_log(
                log_session,
                level="INFO",
                module="scheduler.pipeline",
                message="Full pipeline: wall-clock finished",
                ingestion_run_id=ingestion_run_id,
                extra={
                    "skip_normalize": skip_normalize,
                    "skip_publish": skip_publish,
                    "skip_upload": skip_upload,
                    "publish_summary": publish_summary,
                    "publish_aborted": publish_aborted,
                    "upload_result": upload_result_summary,
                },
            )
            log_session.commit()
    except PipelineRunCancelled:
        logger.info("run_pipeline: cooperative cancel ingestion_run_id=%s", ingestion_run_id)
        try:
            with SessionFactory() as session:
                run = session.get(IngestionRun, ingestion_run_id)
                if run is not None and run.status == "running":
                    run.status = "failed"
                    run.finished_at = datetime.now(timezone.utc)
                    note = (run.notes or "").strip()
                    run.notes = (note + " " if note else "") + "marked_failed:cancelled"
                    merge_run_progress(session, ingestion_run_id, phase="cancelled")
                    session.commit()
        except Exception:
            logger.exception(
                "run_pipeline: could not finalize cancelled ingestion_run_id=%s", ingestion_run_id
            )
    except Exception as exc:
        logger.exception("run_pipeline failed for ingestion_run_id=%s", ingestion_run_id)
        err_msg = f"{type(exc).__name__}: {exc}"
        if len(err_msg) > 1800:
            err_msg = err_msg[:1797] + "..."
        try:
            with SessionFactory() as session:
                run = session.get(IngestionRun, ingestion_run_id)
                if run is not None:
                    run.finished_at = datetime.now(timezone.utc)
                    run.status = "failed"
                    is_test = (run.triggered_by or "").strip().lower() == "test"
                    tag = TAG_SIMULATION_TEST if is_test else TAG_PIPELINE_FAILURE
                    level = "warning" if is_test else "error"
                    session.add(
                        PipelineAlert(
                            level=level,
                            message=tagged_message(tag, f"run_pipeline failed: {err_msg}"),
                            ingestion_run_id=ingestion_run_id,
                        )
                    )
                    persist_error_log(
                        session,
                        module="scheduler.pipeline",
                        message=f"run_pipeline failed: {err_msg}",
                        ingestion_run_id=ingestion_run_id,
                        extra={"exception_type": type(exc).__name__},
                    )
                    merge_run_progress(session, ingestion_run_id, phase="failed", error=err_msg[:500])
                    session.commit()
        except Exception:
            logger.exception(
                "run_pipeline: could not mark ingestion_run_id=%s failed", ingestion_run_id
            )
    finally:
        if registered:
            unregister_pipeline_run(ingestion_run_id)
        try:
            with SessionFactory() as session:
                run = session.get(IngestionRun, ingestion_run_id)
                if run is not None and run.finished_at is None:
                    run.finished_at = datetime.now(timezone.utc)
                    if run.status == "running":
                        run.status = "failed"
                    is_test = (run.triggered_by or "").strip().lower() == "test"
                    tag = TAG_SIMULATION_TEST if is_test else TAG_PIPELINE_UNFINISHED
                    level = "warning" if is_test else "error"
                    session.add(
                        PipelineAlert(
                            level=level,
                            message=tagged_message(
                                tag,
                                "Pipeline finished without setting finished_at (worker may have "
                                "been interrupted before the success path, or an early exit left "
                                "the run stuck). Run marked failed.",
                            ),
                            ingestion_run_id=ingestion_run_id,
                        )
                    )
                    persist_error_log(
                        session,
                        module="scheduler.pipeline",
                        message=(
                            "Pipeline finished without finished_at; run marked failed "
                            "(worker interrupt or early exit)."
                        ),
                        ingestion_run_id=ingestion_run_id,
                    )
                    session.commit()
        except Exception:
            logger.exception(
                "run_pipeline: finally cleanup failed for ingestion_run_id=%s",
                ingestion_run_id,
            )
