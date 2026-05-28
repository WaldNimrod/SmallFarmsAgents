"""DB-backed source weights resolver (WP-C5 Phase A).

Replaces Python-constant SOURCE_REGISTRY weights with rows in the
``crop_source_weights`` table (migration 054, seeded by migration 056).

Per DECISION_RECORD_SFA-S003-P002-WP-C5_v1.0.0 §Decision 5 (team_00
critical requirement): weights must be DB-stored so they can be re-tuned
system-wide based on field experience and farmer feedback, without a code
deploy. (Original verbatim Hebrew is retained in the decision artifact, per
the English-only source policy.)

Lookup contract (mirrors ``source_registry.get_source_spec`` semantics):
    1. Exact-match in DB by ``source_label``
    2. Prefix-pattern in DB (e.g. ``WR:*``, ``NI:*``, ``OP:*``)
    3. Python-constant fallback via ``source_registry.SOURCE_REGISTRY``
       (kept as the durable last line of defence)
    4. Unknown-source default = WB tier, weight 0.20

Cache strategy:
    Process-local dict cache, invalidated via :func:`invalidate_cache`.
    No TTL — re-run of the enrichment runner is the natural reload point,
    and team_00's tuning workflow is "UPDATE then run_enrichment.py" per
    the DECISION_RECORD §"Future tuning workflow".
"""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceSpec:
    """Mirror of source_registry.SourceSpec for compatibility."""
    label: str
    cls: str
    weight: float | None
    is_hard_override: bool = False
    requires_moderation: bool = False


# ---------------------------------------------------------------------------
# In-process cache (thread-safe; the enrichment runner is single-threaded
# in production but tests + ad-hoc CLI invocations may overlap).
# ---------------------------------------------------------------------------
_CACHE: dict[str, SourceSpec] = {}
_CACHE_LOCK = threading.RLock()


def invalidate_cache() -> None:
    """Clear the in-process cache (call after DB weight UPDATE)."""
    with _CACHE_LOCK:
        _CACHE.clear()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_source_spec(
    source_label: str,
    session=None,  # SQLAlchemy Session (optional — caller may pass own)
) -> SourceSpec:
    """Return a :class:`SourceSpec` for ``source_label``.

    Resolves in this order (idempotent, side-effect-free except for cache):
      1. Process cache hit
      2. DB exact-match on ``source_label``
      3. DB prefix-pattern match (e.g. ``WR:*`` for ``WR:cornell-mediterranean``)
      4. Python-constant fallback (``source_registry.SOURCE_REGISTRY``)
      5. Unknown-source default (WB, weight 0.20)

    The function is safe to call even when the DB is unavailable — it
    falls through to the Python constants.
    """
    with _CACHE_LOCK:
        cached = _CACHE.get(source_label)
        if cached is not None:
            return cached

    spec = _resolve_uncached(source_label, session)

    with _CACHE_LOCK:
        _CACHE[source_label] = spec
    return spec


def is_hard_override(source_label: str, session=None) -> bool:
    """Return True if this source always wins (EX or NI class)."""
    return get_source_spec(source_label, session=session).is_hard_override


# ---------------------------------------------------------------------------
# Resolution internals
# ---------------------------------------------------------------------------
def _resolve_uncached(source_label: str, session) -> SourceSpec:
    # Try DB exact + prefix.  Bail safely if DB is offline.
    db_spec = _lookup_db(source_label, session)
    if db_spec is not None:
        return db_spec

    # Python-constant fallback (preserves pre-WP-C5 behavior).
    from organic_market_agent.crop_book import source_registry as _legacy
    return _legacy_lookup(source_label, _legacy)


def _lookup_db(source_label: str, session) -> Optional[SourceSpec]:
    """Query crop_source_weights.  Returns None if no row OR DB error."""
    own_session = False
    try:
        if session is None:
            from organic_market_agent.db.session import SessionFactory
            session = SessionFactory()
            own_session = True

        # 1. Exact match
        row = session.execute(
            text("""
                SELECT source_label, trust_tier, weight,
                       is_hard_override, requires_moderation
                FROM crop_source_weights
                WHERE source_label = :label
                LIMIT 1
            """),
            {"label": source_label},
        ).first()
        if row is not None:
            return _row_to_spec(source_label, row)

        # 2. Prefix-pattern match.  Convention: pattern rows end in ':*'
        #    (e.g. 'WR:*' matches any 'WR:foo' label).
        if ":" in source_label:
            prefix = source_label.split(":", 1)[0] + ":*"
            row = session.execute(
                text("""
                    SELECT source_label, trust_tier, weight,
                           is_hard_override, requires_moderation
                    FROM crop_source_weights
                    WHERE source_label = :pattern
                    LIMIT 1
                """),
                {"pattern": prefix},
            ).first()
            if row is not None:
                return _row_to_spec(source_label, row)

        return None
    except SQLAlchemyError as exc:
        # DB offline / table missing → fall through to constants.
        logger.warning(
            "crop_source_weights lookup failed for %s (%s); "
            "falling back to Python constants",
            source_label, exc,
        )
        return None
    finally:
        if own_session and session is not None:
            session.close()


def _row_to_spec(label: str, row) -> SourceSpec:
    # Row columns by index: source_label, trust_tier, weight, hard, mod
    weight = float(row[2]) if row[2] is not None else None
    return SourceSpec(
        label=label,
        cls=row[1],
        weight=weight,
        is_hard_override=bool(row[3]),
        requires_moderation=bool(row[4]),
    )


def _legacy_lookup(source_label: str, legacy_module) -> SourceSpec:
    """Defer to source_registry's Python constants (last-resort)."""
    # Avoid recursion: call the raw dict + prefix logic directly.
    registry = legacy_module.SOURCE_REGISTRY
    if source_label in registry:
        spec = registry[source_label]
    elif source_label.startswith("NI:"):
        spec = legacy_module.SourceSpec(
            source_label, "NI", weight=None, is_hard_override=True
        )
    elif source_label.startswith("WR:"):
        spec = legacy_module.SourceSpec(source_label, "WR", weight=0.60)
    elif source_label.startswith("OMA:"):
        spec = legacy_module.SourceSpec(source_label, "MK", weight=0.40)
    elif source_label.startswith("WB:"):
        spec = legacy_module.SourceSpec(source_label, "WB", weight=0.30)
    elif source_label.startswith("UC:"):
        spec = legacy_module.SourceSpec(
            source_label, "UC", weight=0.15, requires_moderation=True
        )
    elif source_label.startswith("OP:"):
        spec = legacy_module.SourceSpec(source_label, "OP", weight=0.55)
    elif source_label.startswith("PR:"):
        spec = legacy_module.SourceSpec(source_label, "PR", weight=0.70)
    elif source_label.startswith("MK:"):
        spec = legacy_module.SourceSpec(source_label, "MK", weight=0.40)
    else:
        spec = legacy_module.SourceSpec(source_label, "WB", weight=0.20)

    # Convert legacy SourceSpec → local SourceSpec (same fields)
    return SourceSpec(
        label=spec.label,
        cls=spec.cls,
        weight=spec.weight,
        is_hard_override=spec.is_hard_override,
        requires_moderation=spec.requires_moderation,
    )
