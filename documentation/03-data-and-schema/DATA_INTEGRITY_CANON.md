# Crop-Book Data Integrity — Canon (binding)

**Scope:** How crop-book data is built, kept clean, and deployed without corrupting either the local canonical DB or the live tier.
**Authority:** This document is binding. It encodes team_00 canon and learned operational rules. Where it conflicts with a one-off habit, this doc wins.
**Upstream context:** [`README.md`](README.md) (source-of-truth order), [`sfa-mysql-mirror.md`](sfa-mysql-mirror.md) (delivery schema), [`../02-architecture/sfa-delivery-tier.md`](../02-architecture/sfa-delivery-tier.md) (host roles).

---

## Why this exists

A full re-seed (`seed --all`) was once run against the deploy baseline to "add a few crops". It re-ran every importer, minted **duplicate crops** from a non-canonical name map, and reintroduced **forbidden derived fields** into the canonical tables. The publish whitelist kept the derived leak out of production, but the local DB was now polluted: `tests/crop_book` and `validate_aos.sh` failed, and the cross-engine (team_190) validation could not pass. Recovery meant rebuilding local state by hand.

The lesson is structural, not a one-off: **never use a full re-seed as an "add data" tool, and never deploy from a polluted local DB.** The rules below make the safe path the default path.

---

## 1. Two databases, one direction

| Role | Host / DB | Engine | Purpose |
|------|-----------|--------|---------|
| **Build SSoT** | local Docker `oma-postgres:5433` | PostgreSQL | The canonical place crop data is **built** and edited |
| **Live tier** | `sfa.nimrod.bio` (uPress) | MySQL (read-mirror) | What end users see |

Data flows **local → prod ONLY**, via the HMAC ingest API (`POST https://sfa.nimrod.bio/api/v1/ingest`). There is no reverse path; the live tier never writes back. See [`sfa-mysql-mirror.md`](sfa-mysql-mirror.md) §1.

The **authoritative record of what is LIVE** is the production crop count:

```bash
curl -s https://sfa.nimrod.bio/api/v1/crops | python3 -c 'import sys,json; print(json.load(sys.stdin)["count"])'
```

Trust this number, not your local count, when asking "what did users actually get?"

---

## 2. NEVER `seed --all` to add data — ADD INCREMENTALLY

`seed --all` is a **rebuild**, not an **add**. It re-runs *every* importer, which:

- (a) can **mint duplicate crops** from non-canonical name maps (see §6), and
- (b) **reintroduces forbidden derived fields** that a clean DB must not store (see §3).

To add or correct crop data, run the **specific importer fast-path** and let it upsert idempotently. The mode flags live in [`../../organic_market_agent/crop_book/importer/seed.py`](../../organic_market_agent/crop_book/importer/seed.py) (mutually exclusive group):

| Flag | Importer scope |
|------|----------------|
| `--c1-only` | WP-C1 (Israeli structured + Tend multi-year) |
| `--c2-only` | WP-C2 (Hebrew narrative NI) |
| `--c3-only` | WP-C3 (Curtis Stone + Idan succession + FRANCHI + L49 + Tend 2018) |
| `--c4-only` | WP-C4 (web-source) |
| `--content-only` | WP-CB-CONTENT curated narrative prose |
| `--wd-only` | WP-D (Cursor web research) |
| `--openai-only` | WP-E (OpenAI Tier 1 extension research) |
| `--idan-only` | WP-F (Idan farm seasonal planning) |
| `--calendar-only` | WP-G (Israeli planting calendar) |
| `--gemini-only` | WP-H (Gemini IL research) |
| `--ni-only` / `--jmf-only` / `--tend-overlay-only` | NI / JMF MasterClass / Tend overlay only |
| `--crops NAME [NAME ...]` | Named crops only (Tend English names) |

> Always rehearse with `--dry-run` first. Then deploy with a **scoped** push (§4).

---

## 3. `seed --all` alone is NON-canonical

Even when a full rebuild is genuinely needed (cold rebuild of an empty DB), `seed` by itself does **not** produce the canonical state. The canonical state is:

```
seed  →  canon derived-field strip
```

Run the strip with:

```bash
python -m organic_market_agent.crop_book.canon.migrate phase4
```

(see [`../../organic_market_agent/crop_book/canon/migrate.py`](../../organic_market_agent/crop_book/canon/migrate.py); `phase4` is idempotent).

### Forbidden DERIVED fields (never stored)

These must have **zero rows** in **both** `crop_variety_source_values` and `crop_field_enrichment`:

- `yield_per_m2_kg`
- `nutrient_removal_p2o5_kg_ha`
- `nutrient_removal_k2o_kg_ha`
- `plants_per_m2`
- `avg_revenue_per_bed_m`

They are computed on read, never persisted (canon LOD200 §6.4). Leaving any of them in the DB fails [`../../tests/crop_book/test_ac05_derived_fields.py`](../../tests/crop_book/test_ac05_derived_fields.py) (AC-05).

---

## 4. Scoped, incremental deploys

Push **only the crops you changed**, never the whole table off a freshly-rebuilt DB:

```bash
python -m organic_market_agent.publisher.sfa_ingest_push --table <t> --crop-ids <ids>
```

(crop-keyed tables only — [`../../organic_market_agent/publisher/sfa_ingest_push.py`](../../organic_market_agent/publisher/sfa_ingest_push.py)).

- **NEVER** `--table all` against a polluted local DB — that propagates the pollution surface.
- The publish whitelist (`_AGRONOMY_FIELD_WHITELIST` in `sfa_ingest_push.py`) **excludes the derived fields**, so production is protected from a derived leak even if local is dirty. This is a backstop, not an excuse — **local/validation still breaks, so fix local.**
- **Prefer `--crop-ids` over `--slugs`.** Crop slugs can collide: a duplicate crop yields an ambiguous slug, and the push will error rather than guess. IDs are unambiguous.

Always `--dry-run` the push before the real one.

---

## 5. Crop taxonomy rule (team_00 canon)

> **A different agricultural PRODUCT is a different crop, even if it is the same botanical species.**

| Treated as SEPARATE crops | Treated as the SAME crop / a name-duplicate |
|---------------------------|---------------------------------------------|
| Beet vs Chard | Rutabaga → treated as **Turnip** (same product) |
| Celery vs Celeriac | "Basil" / "בזיליקום" — name-duplicate, one crop |
| Cabbage vs Chinese Cabbage vs Brussels Sprouts | "Salad Mix" / "תערובת סלט" — name-duplicate, one crop |
| Peppers vs Hot Pepper | |

**Baby-leaf greens (עלי בייבי)** legitimately have varieties that are themselves mixes or different species grown for baby leaves. Those are **VARIETIES**, not crops — do not promote a baby-leaf variety into its own crop.

When in doubt, ask: "is this a different thing a grower sells/plans?" If yes → crop. If it is the same product under another name → it is a name-duplicate, fold it.

---

## 6. Duplicate crops come from non-canonical name maps

The usual root cause of a minted duplicate is `JMF_CROP_MAP` in [`../../organic_market_agent/crop_book/constants.py`](../../organic_market_agent/crop_book/constants.py) mapping a crop to a Hebrew name that does **not** match the canonical crop's name. The seed then can't resolve it to the existing crop and **creates a new one**.

**Fix the map, not the data.** Point `JMF_CROP_MAP` (and any other importer name map) at the **canonical** Hebrew crop names. Never let an importer mint a crop that already exists under a different name. If you find a duplicate already in the DB, merge it down to the canonical crop and prefer `--crop-ids` for any subsequent push (§4).

---

## 7. Pre-deploy checklist

Run **all** of these before any push. A single failure means **do not deploy** — fix local first.

- [ ] **Count parity** — compare local crop count to the production API count (§1). Investigate any unexpected delta before pushing.
- [ ] **AC-05 clean** — `python -m pytest tests/crop_book` passes, especially [`test_ac05_derived_fields.py`](../../tests/crop_book/test_ac05_derived_fields.py) (zero derived rows in both tables).
- [ ] **AOS validation** — `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → **0 FAIL**.
- [ ] **No internal/licensed notes in the publish path** — confirm `crop_knowledge_notes` is never read by the publisher (enforced by `test_ni_publisher_isolation`; see [`../../organic_market_agent/crop_book/content_models.py`](../../organic_market_agent/crop_book/content_models.py)).
- [ ] **Scoped push** — `--crop-ids` for exactly the crops you changed; `--dry-run` first; never `--table all` off a rebuilt DB.

---

## Related

- Source-of-truth order, migrations workflow: [`README.md`](README.md)
- Delivery-tier schema (binding DDL, whitelist context): [`sfa-mysql-mirror.md`](sfa-mysql-mirror.md)
- Host roles (build vs serve vs deploy-from): [`../02-architecture/sfa-delivery-tier.md`](../02-architecture/sfa-delivery-tier.md)
- UI/data deploy runbooks: [`../05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`](../05-admin-and-operations/UI_DEPLOY_RUNBOOK.md)
- Docker port canon (PG=5433 `oma-postgres`): see project `CLAUDE.md` → "Docker port canon"

*Last updated: 2026-06-11 — created after the full-re-seed pollution incident (duplicate crops + derived-field reintroduction → AC-05 + cross-engine validation failure).*
