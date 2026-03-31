# Documentation archive

## Purpose

Store **completed**, **time-bound** specification and handoff documents that are no longer “active” work but should remain discoverable for audits and future agents.

## What belongs here

- Finished design drafts that were superseded by implementation
- Dated team reports that are **closed** (not ongoing mandates)
- One-off analysis exports (sanitized) referenced in commits

## What does **not** belong here

- **Canonical** specs that are still authoritative — keep in `docs/` or `_COMMUNICATION/` until explicitly retired
- **Secrets** — never commit credentials or production dumps

## Naming convention

`YYYY-MM-DD_short-topic_source.md`

Examples:

- `2026-03-31_scope_skip_approval_final.md`
- `2026-04-01_publish_window_decision.md`

## Process

1. When a document is **closed**, copy or move it under `documentation/archive/YYYY/` (optional year subfolder) or flat with date prefix.
2. Add a one-line pointer in the nearest active README if the topic is still relevant (e.g. “Final approved scope-skip list: see archive/2026/…”).

## Existing team archive

Formal team reports may continue to live under [`../../_COMMUNICATION/`](../../_COMMUNICATION/) by convention; this folder is for **documentation hub** material you want co-located with `documentation/` for agent discovery.
