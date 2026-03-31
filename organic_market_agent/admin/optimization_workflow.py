"""Generic admin pattern for data-quality optimization (English spec for Team 100/10).

Goal: raise normalization success rates by closing the loop from “monitoring lists”
to “structured corrections” with minimal one-off UI.

Recommended pattern (apply across unresolved names, rule gaps, catalog drift, etc.):

1. **Live list (read)**  
   - SQL at request time only; no server-side HTML fragment cache.  
   - HTTP `Cache-Control: no-store` on list + detail so browsers/CDNs do not serve stale rows.

2. **Machine export (read)**  
   - Authenticated JSON/CSV endpoint mirroring the same query (or superset with a safe row cap).  
   - Payload includes `generated_at` (UTC ISO) and schema version for audit.

3. **Structured ingest (write, future)**  
   - POST accepts a batch of typed actions (e.g. `add_alias`, `add_normalizer_rule`) with idempotency keys.  
   - Each item validated, applied in a transaction, logged to `audit_log`.  
   - Reject partial application unless explicitly requested; surface per-row errors.

4. **Re-run pipeline slice (ops)**  
   - After batch fixes, optionally re-run normalizer for affected `source_id` / `ingestion_run_id` only.

This module holds documentation only; implementation is split across routes and scripts.
"""
