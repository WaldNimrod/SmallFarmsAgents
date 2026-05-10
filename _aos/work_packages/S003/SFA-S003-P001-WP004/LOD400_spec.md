# LOD400 — SFA-S003-P001-WP004 — ספר גידולים: WordPress Integration

**Date:** 2026-05-10 (Round 2 revision)
**Author:** team_100 (Claude Sonnet 4.6 declared / Opus 4.7 actual)
**WP:** SFA-S003-P001-WP004 — CropBookPublisher + `[sfagent_crop_book]` shortcode + first publish
**Type:** LOD400_SPEC
**Status:** L-GATE_S ROUND_2 — Round 1 BLOCKED, all 4 findings remediated; awaiting team_190 re-review
**Round 1 verdict:** BLOCKED (team_190, 2026-05-10, commit `feee36c`); F-190-WP004-01 (entity registry source path) + F-190-WP004-02 (timeline rule) BLOCKERs, F-190-WP004-03 (substitution-miss AC) MAJOR, F-190-WP004-04 (roadmap drift) MINOR. Verdict: `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LOD400-VERDICT_v1.0.0.md`
**Builder:** sfa_build (Sonnet, Team 10)
**Validator:** team_190 (external — L-GATE_SPEC + L-GATE_VALIDATE)
**Depends on:** SFA-S003-P001-WP002 (DB tables + seed), SFA-S003-P001-WP003 (Flask views — semantic SSoT for filter parity)
**Profile:** L0
**Effort:** LARGE
**Engine constraint:** sfa_build (Claude Sonnet 4.6) builder; team_190 validator must be **non-Claude** per Iron Rule #1.

**Reference documents (read before writing a single line of code):**
1. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md` — schema SSoT
2. `_aos/work_packages/S003/SFA-S003-P001-WP003/LOD400_spec.md` — UI semantics SSoT (filter logic + tab data context)
3. `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md` — operational gotchas (mu-plugin install, port 21 block, App Password format)
4. `organic_market_agent/publisher/engine.py` — reference impl for `PublishEngine`
5. `organic_market_agent/publisher/wp_upload.py` — canonical WP REST upload path
6. `organic_market_agent/publisher/upload_dispatch.py` — single dispatch function reused here with a new `profile` arg
7. `scripts/wp_shortcode_install.py` — reference shortcode PHP body + WP option register pattern
8. This LOD400 spec

---

## 1. Goal

Make the locked `crop_book` data publicly readable on `https://www.nimrod.bio` through a single-page-app HTML fragment delivered by a new shortcode `[sfagent_crop_book]`. Mirror the existing market-report pipeline (manifest-of-URLs pointer → body fragment → shortcode dereference) to keep one canonical operational shape.

**Boundary:** WP004 produces the publish pipeline + ships the mu-plugin file. team_99 deploys the mu-plugin and runs the first publish. WP004 does **not** modify the existing `/crop-book/` Flask admin views, models, or migrations (all LOD500_LOCKED).

---

## 2. Architecture

### 2.1 Pipeline

```
PostgreSQL (alembic head=040)
   │
   ▼
CropBookPublisher.run(session, output_dir)
   │
   ├─→ output/crop_book/sfagent-crop-book-body.html        (HTML fragment, ~30–60 KB)
   ├─→ output/crop_book/sfagent-crop-book-data.json        (data, ~3–5 MB raw)
   └─→ output/crop_book/sfagent-crop-book-manifest.json    (provenance + URLs)
   │
   ▼
upload_dispatch.dispatch_upload(output_dir, profile="crop_book")
   │
   ▼ HTTPS / port 443  (FTPS path INTENTIONALLY DISABLED for crop_book — Bezeq blocks port 21)
   │
WP media library (4 artifacts uploaded; sfagent-crop-book-manifest-of-urls.json is pointer)
   │
   ▼
WP option `sfagent_crop_book_manifest_of_urls_url`  (set via REST PUT /wp/v2/settings)
   │
   ▼
mu-plugin sfagent-crop-book-shortcode.php  (registers [sfagent_crop_book])
   │
   ▼
Public WP page renders body fragment → SPA boots → fetches data.json → ready
```

### 2.2 Module layout

```
organic_market_agent/
└── crop_book/
    └── publisher/
        ├── __init__.py
        ├── engine.py                                ← CropBookPublisher
        ├── entity_registry_data.py                  ← Python-owned canonical entity registry (NEW R2)
        ├── templates/
        │   ├── crop_book.html                       ← full standalone (preview)
        │   └── crop_book_body.html                  ← WordPress fragment (the SPA shell)
        └── static/
            └── sfagent-crop-book.js                 ← SPA JS (read at render time, inlined)

organic_market_agent/publisher/
    ├── wp_upload.py                                 ← extended (new canonical names + crop_book uploader)
    └── upload_dispatch.py                           ← extended (profile kwarg)

organic_market_agent/__main__.py                     ← extended (crop_book_publish subcommand)

wordpress/mu-plugins/
    └── sfagent-crop-book-shortcode.php              ← NEW (deployed manually by team_00 once)

documentation/05-admin-and-operations/
    └── UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md        ← extended (Crop Book section)

tests/crop_book/
    ├── test_publisher.py                            ← NEW
    ├── test_filter_parity.py                        ← NEW
    └── test_wp_upload_crop_book.py                  ← NEW
```

### 2.3 Reuse vs. new code

| Component | Decision | Rationale |
|-----------|----------|-----------|
| `dispatch_upload` | **Extend** (add `profile` kwarg) | Single upload code path; FTPS-skip branch is just an `if profile == "crop_book"` guard. |
| `wp_upload.py` | **Extend** (new constants + new function) | Existing `upload_all_artifacts` stays untouched; new `upload_all_crop_book_artifacts` mirrors it. |
| `PublishEngine` | **Do NOT subclass** | `CropBookPublisher` is a sibling class (different data, different templates). Inheritance would couple the two; sibling avoids regression risk on market path. |
| `sfagent-base.css` | **Do NOT modify** | Crop book ships its own inline CSS in the body fragment for v1. |
| Existing market shortcode (`sfagent_market_report`) | **Do NOT modify** | Crop book gets its own mu-plugin file, its own option, its own shortcode tag. |
| `sfagent-allow-json.php` mu-plugin | **Do NOT modify** | Already permits `.json` and `.html` MIME upload — crop book artifacts are these types, no additional MIME registration needed. |

### 2.4 Entity registry — Round 2 source-of-truth resolution (F-190-WP004-01)

The WP003 admin templates `crop_book/templates/crop_book/index.html:142` and `crop_book/templates/crop_book/crop.html:464` reference `crop_book/static/entity_registry.js` via `url_for('static', ...)`. **That file is NOT tracked in `HEAD`** at the reviewed commit `b9baf75` — a known WP003 deliverables gap that survived L-GATE_V (the admin UI works in the local dev environment because the file exists as untracked working-tree state, but the canonical repo does not have it).

WP004 does not attempt to fix the WP003 gap. Instead, **WP004 owns its own canonical entity-registry data** as a Python module:

- **Path:** `organic_market_agent/crop_book/publisher/entity_registry_data.py`
- **Type:** plain Python data module — top-level `ENTITY_REGISTRY: dict` literal
- **Structure:** mirrors the JS-side schema declared in §4 — `{"version": "1.0.0", "type_labels": {...}, "entities": {pest: {...}, disease: {...}, equip: {...}, input: {...}, technique: {...}, crop: {...}}}`
- **Seed content:** the same 7 pests, 5 diseases, 3 equipment, 5 inputs, 6 techniques, 4 crops the WP003 working-tree JS contains (transcribed by the builder; see §13 step 3)
- **SSoT for both surfaces:** the publisher imports `ENTITY_REGISTRY` directly into the SPA JSON blob. **No JS file parsing, no regex, no eval.**

This eliminates the AC-16 contradiction (the spec is no longer asking the builder to read a file that does not exist while also locking it as immutable) and gives the publisher a deterministic, type-checked source. The WP003 admin gap (templates reference a missing file) is **out-of-scope for WP004** and will be addressed by a separate follow-up WP if/when the admin tooltips need to render in production-like environments.

---

## 3. CropBookPublisher

### 3.1 Class signature

`organic_market_agent/crop_book/publisher/engine.py`:

```python
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session, joinedload

class CropBookPublisher:
    """Renders ספר גידולים artifacts for WordPress publication.

    Stateless — instantiate once, call run() per publish.
    """

    SCHEMA_VERSION = "crop_book.v1"
    DATA_VERSION   = "1.0.0"

    def run(
        self,
        session: Session,
        output_dir: Path,
        generated_at: datetime | None = None,
    ) -> dict[str, Any]:
        ...
```

### 3.2 `run()` contract

**Inputs:**
- `session`: SQLAlchemy Session bound to the crop_book schema (alembic ≥ 040).
- `output_dir`: directory to write 3 artifacts to. Created if missing.
- `generated_at`: optional UTC timestamp for the manifest; defaults to `datetime.now(timezone.utc)`.

**Side effects:** writes exactly 3 files into `output_dir`:
- `sfagent-crop-book-body.html` — Jinja2-rendered fragment (template `crop_book_body.html`), with the SPA JS file inlined into a `<script>` block and the **data JSON URL** templated into a `<script>window.CROP_BOOK_DATA_URL = "{{ data_url }}"</script>` block. The data URL is initially `./sfagent-crop-book-data.json` (relative — works for local preview); the deployed WP shortcode resolves to the absolute media URL via the manifest-of-URLs pattern (see §5.3).
- `sfagent-crop-book-data.json` — JSON blob per §4.
- `sfagent-crop-book-manifest.json` — provenance manifest per §3.4.

**Returns:** dict with keys `{"output_dir": str, "files": [str, str, str], "crop_count": int, "variety_count": int, "data_size_bytes": int, "generated_at": str}`.

**Logging:** `logger.info` at start and on completion with crop/variety counts. No PII.

**Errors:** raises `CropBookPublishAbortError` (new exception in `publisher/engine.py`) if crop count is 0 (sanity check — protects against publishing an empty book).

### 3.3 Database queries

Single transaction, eager-loaded:

```python
crops = (
    session.query(Crop)
    .options(
        joinedload(Crop.family),
        joinedload(Crop.varieties).joinedload(CropVariety.source_values),
        joinedload(Crop.conversion_group).joinedload(CropConversionGroup.unit_conversions),
    )
    .order_by(Crop.name_he)
    .all()
)
families            = session.query(CropFamily).order_by(CropFamily.scientific_name).all()
conversion_groups   = session.query(CropConversionGroup).order_by(CropConversionGroup.name).all()
crop_conversions    = session.query(CropUnitConversion).filter(CropUnitConversion.crop_id.isnot(None)).all()
group_conversions   = session.query(CropUnitConversion).filter(CropUnitConversion.conversion_group_id.isnot(None)).all()
```

Use `_crop_to_dict` / `_variety_to_dict` / `_source_value_to_dict` / `_conversion_to_dict` helpers (private module functions, not methods) that mirror the field naming in §4.

### 3.4 Manifest schema (`sfagent-crop-book-manifest.json`)

```json
{
  "schema_version": "crop_book.manifest.v1",
  "artifact_version": "20260509_120000",
  "generated_at": "2026-05-09T12:00:00Z",
  "crop_count": 52,
  "variety_count": 242,
  "source_value_count": 9876,
  "data_size_bytes": 4123456,
  "artifacts": {
    "body":     "sfagent-crop-book-body.html",
    "data":     "sfagent-crop-book-data.json",
    "manifest": "sfagent-crop-book-manifest.json"
  }
}
```

`artifact_version` is a `YYYYMMDD_HHMMSS` timestamp built from `generated_at` (matches market-report manifest convention).

---

## 4. Data JSON shape (`sfagent-crop-book-data.json`)

Schema id: `crop_book.v1`. **All field names lowercase_with_underscores. All Hebrew text passes through unchanged.**

```jsonc
{
  "schema": "crop_book.v1",
  "data_version": "1.0.0",
  "generated_at": "2026-05-09T12:00:00Z",

  "categories": {
    "vegetables":   "ירקות",
    "herbs":        "עשבי תיבול",
    "baby":         "עלים בייבי",
    "legumes":      "קטניות",
    "fruits":       "פירות",
    "fruit_trees":  "עצי פרי",
    "grains":       "דגנים",
    "cover_crops":  "גידולי כיסוי"
  },

  "season_tokens": [
    { "key": "summer", "tokens": ["קיץ", "summer"], "emoji": "☀️" },
    { "key": "spring", "tokens": ["אביב", "spring"], "emoji": "🌸" },
    { "key": "winter", "tokens": ["חורף", "winter"], "emoji": "🌧" },
    { "key": "fall",   "tokens": ["סתיו", "fall", "autumn"], "emoji": "💨" }
  ],

  "families":          [ /* CropFamily rows: id, scientific_name, name_he */ ],
  "conversion_groups": [ /* CropConversionGroup rows: id, name, description */ ],
  "conversions":       [ /* CropUnitConversion rows: full set, both group-scoped and crop-scoped */ ],

  "entity_registry": {
    "version":      "1.0.0",
    "type_labels":  { "pest": "מזיק", "disease": "מחלה", "equip": "ציוד", "input": "תשומה", "technique": "טכניקה", "crop": "גידול" },
    "entities":     { /* imported from crop_book/publisher/entity_registry_data.py at publish time */ }
  },

  "crops": [
    {
      "id": 12, "name_he": "עגבנייה", "name_en": "Tomato",
      "scientific_name": "Solanum lycopersicum", "family_id": 1,
      "category": "vegetables", "growth_cycle": "annual",
      "harvest_unit_default": "kg", "first_fruit_year": null,
      "conversion_group_id": null, "description": "...",
      "oma_product_id": "VEG_TOM",
      "varieties": [
        {
          "id": 87, "name_he": "תמרי", "name_en": "Datterino",
          "is_default": true, "is_grafted": false, "rootstock_variety": null,
          "planting_method": "transplant",
          "days_to_maturity": 70,
          "harvest_window_min_days": 21, "harvest_window_max_days": 56,
          "in_row_spacing_cm": 50.0, "rows_per_bed": 1,
          "planting_season": "אביב–קיץ", "harvest_stage": "full_size",
          "harvest_unit": "kg", "avg_yield_per_bed_m": 1.8, "yield_source": "Tend",
          "documented_price": 22.0, "documented_price_unit": "kg",
          "documented_price_source": "JMF 2024",
          "avg_revenue_per_bed_m": 39.6, "pricebook_product_id": null,
          "days_in_gh_total": 35,
          "seeder": null, "seeder_front_gear": null, "seeder_rear_gear": null, "seeder_roller_plate": null,
          "notes": null,
          "source_values": [
            { "field_name": "documented_price", "source": "JMF 2024",
              "value_text": null, "value_numeric": 22.0, "unit": "kg", "note": null }
          ]
        }
      ]
    }
  ]
}
```

**Numeric encoding:** SQLAlchemy `Numeric` columns serialize as **JSON numbers** (not strings). Use `float()` cast in `_to_dict` helpers. `null` for nullable empty values.

**Entity registry source (R2 — F-190-WP004-01):** at build time, the publisher imports the canonical Python registry from `organic_market_agent.crop_book.publisher.entity_registry_data` (`ENTITY_REGISTRY: dict`), validates required top-level keys (`version`, `type_labels`, `entities`) and required entity-type subkeys (`pest`, `disease`, `equip`, `input`, `technique`, `crop`), and embeds it. **No JS file parsing. No regex. No eval.** If validation fails (missing key or wrong type), the publisher fails loudly (raises `CropBookPublishAbortError`) — better to fail than ship a broken registry.

---

## 5. WP REST upload extensions

### 5.1 New canonical filenames in `wp_upload.py`

```python
CANONICAL_CROP_BOOK_BODY     = "sfagent-crop-book-body.html"
CANONICAL_CROP_BOOK_DATA     = "sfagent-crop-book-data.json"
CANONICAL_CROP_BOOK_MANIFEST = "sfagent-crop-book-manifest.json"
CANONICAL_CROP_BOOK_MOU      = "sfagent-crop-book-manifest-of-urls.json"
```

### 5.2 New `upload_all_crop_book_artifacts(output_dir) -> dict[str, tuple[int, str]]`

Mirrors `upload_all_artifacts` exactly:
1. Reads 3 local files from `output_dir` (body, data, manifest).
2. Uploads each via `upload_artifact` with the canonical name + correct content type:
   - `body`     → `text/html`
   - `data`     → `application/json`
   - `manifest` → `application/json`
3. Builds a fresh `sfagent-crop-book-manifest-of-urls.json` (schema `crop_book.mou.v1`) containing the 3 uploaded URLs.
4. Uploads the MoU as a fourth artifact.
5. Returns `{"body": (id, url), "data": (id, url), "manifest": (id, url), "mou": (id, url)}`.

**Crop book MoU schema:**
```json
{
  "schema": "crop_book.mou.v1",
  "generated_at": "2026-05-09T12:00:00Z",
  "artifacts": {
    "body":     "https://www.nimrod.bio/wp-content/uploads/.../sfagent-crop-book-body.html",
    "data":     "https://www.nimrod.bio/wp-content/uploads/.../sfagent-crop-book-data.json",
    "manifest": "https://www.nimrod.bio/wp-content/uploads/.../sfagent-crop-book-manifest.json"
  }
}
```

### 5.3 SPA data-URL resolution at WP runtime (R2 — F-190-WP004-03)

The body fragment ships with the **literal sentinel** `window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"` (relative, for local preview). When the shortcode renders the body inside a WordPress page, **the shortcode rewrites this** before emitting HTML.

**Sentinel constant (used by both publisher and PHP):**
```
SFAGENT_CROP_BOOK_DATA_URL_SENTINEL = 'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"'
```

**Two-sided invariants:**

1. **Publisher side (Python — `engine.py`):** after rendering `crop_book_body.html`, before writing the file, assert the rendered body contains the exact sentinel string. If absent, raise `CropBookPublishAbortError("body fragment missing CROP_BOOK_DATA_URL sentinel — template drift")`. Loud failure prevents the publisher from ever shipping a body fragment that the WP shortcode cannot rewrite.

2. **WordPress side (PHP shortcode):** use `str_replace` with the **4-argument form** to capture the replacement count, then check it explicitly:

```php
$sentinel    = 'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"';
$replacement = 'window.CROP_BOOK_DATA_URL = "' . esc_url_raw( $artifacts->data ) . '"';
$body_html   = wp_remote_retrieve_body( wp_remote_get( $body_url ) );
$count       = 0;
$body_html   = str_replace( $sentinel, $replacement, $body_html, $count );

if ( $count === 0 ) {
    error_log( '[sfagent_crop_book] sentinel substitution miss — body fragment may have drifted; '
             . 'expected: ' . $sentinel . ' — falling back to placeholder' );
    return '<div class="sfa-crop-book-pending">ספר גידולים — בטעינה</div>';
}
```

This keeps the body fragment self-contained for local preview while making the WP-deployed copy fetch the absolute media-library URL — and refuses to emit a half-broken page silently if the sentinel ever drifts. Both invariants are tested (AC-17 publisher sentinel, AC-18 PHP miss path).

### 5.4 `dispatch_upload` extension

```python
from typing import Literal

def dispatch_upload(
    output_dir: Path,
    *,
    profile: Literal["market", "crop_book"] = "market",
    allow_fallback_ftps_env: str = "UPRESS_FALLBACK_FTPS",
) -> UploadResult:
    if profile == "crop_book":
        # FTPS fallback intentionally disabled — Bezeq blocks port 21 outbound.
        if not Config.wp_rest_configured():
            raise NoUploadConfigured("WP REST not configured; FTPS disabled for crop_book profile.")
        artifacts = wp_upload.upload_all_crop_book_artifacts(output_dir)
        return UploadResult(protocol_used="wp_rest", success=True,
                            success_count=len(artifacts), total_count=len(artifacts),
                            errors=[], wp_artifacts=artifacts,
                            files_uploaded=[], files_failed=[], remote_base="")
    # else: existing market path unchanged
    ...
```

**Constraint:** the existing `profile="market"` branch must produce **byte-identical** behavior to the current function (regression-safe). The new param defaults to `"market"` — no caller change required.

---

## 6. CLI subcommand

`organic_market_agent/__main__.py`:

```python
@cli.command("crop_book_publish")
@click.option("--output-dir", default="output/crop_book",
              help="Directory to write crop book artifacts.")
@click.option("--upload", is_flag=True, default=False,
              help="After rendering, upload artifacts via dispatch_upload(profile=\"crop_book\").")
@click.option("--set-mou-url", is_flag=True, default=False,
              help="After upload, write WP option `sfagent_crop_book_manifest_of_urls_url` via REST.")
def crop_book_publish_cmd(output_dir: str, upload: bool, set_mou_url: bool) -> None:
    """Render and optionally publish the ספר גידולים SPA to WordPress."""
    ...
```

**Behavior:**
1. Open DB session via existing `SessionFactory` / `get_db_session()` helper.
2. `summary = CropBookPublisher().run(session, Path(output_dir))` — log summary.
3. If `--upload`: call `dispatch_upload(Path(output_dir), profile="crop_book")`. Log result. Exit 1 on failure.
4. If `--set-mou-url`: PUT to `/wp/v2/settings` with body `{"sfagent_crop_book_manifest_of_urls_url": <mou_url>}` using the same Basic Auth path as `wp_upload.py`. (Existing market-launch precedent for setting `sfagent_manifest_of_urls_url` via REST is in the runbook §177–198 — follow the same pattern.)
5. Exit 0 on success.

**No changes to scheduler.** No changes to admin UI. CLI is the only entrypoint for v1.

---

## 7. WordPress mu-plugin

`wordpress/mu-plugins/sfagent-crop-book-shortcode.php`:

- Single file, ~80 lines PHP.
- Three hooks:
  1. `register_setting('options', 'sfagent_crop_book_manifest_of_urls_url', ['show_in_rest' => true, 'type' => 'string', 'sanitize_callback' => 'esc_url_raw'])` — so the CLI can set it via `/wp/v2/settings`.
  2. `add_shortcode('sfagent_crop_book', 'sfagent_crop_book_shortcode')` — renders the SPA.
  3. `add_action('wp_enqueue_scripts', 'sfagent_crop_book_enqueue_styles')` — *empty for v1* (CSS is inlined in the body fragment); registered as a no-op hook so adding deployed CSS later is a one-line change.

- Shortcode body logic:
  1. Read WP option `sfagent_crop_book_manifest_of_urls_url`. If empty → return placeholder div (`<div class="sfa-crop-book-pending">ספר גידולים — בטעינה</div>`).
  2. `wp_remote_get` the MoU URL. On non-200 (`is_wp_error` or `wp_remote_retrieve_response_code !== 200`) → `error_log` the failure with the URL + status + response body and return placeholder.
  3. Decode JSON. If `json_decode` returns `null` or required keys (`artifacts.body`, `artifacts.data`) are missing → `error_log` and return placeholder.
  4. `wp_remote_get` the body URL. On non-200 → `error_log` and return placeholder.
  5. **Apply the data-URL substitution per §5.3 — using the 4-argument `str_replace` form to capture `$count`. If `$count === 0`, `error_log` a sentinel-drift message and return placeholder.** This is the F-190-WP004-03 remediation.
  6. Return the modified body HTML (raw — `<div class="sfa-crop-book" dir="rtl" lang="he">…</div>`).

- Caching: use **`set_transient` with a 5-minute TTL** keyed on the MoU URL. After publish, the cache is irrelevant for ≤5 minutes; this matches market-report behavior.

- **Idempotency:** the file checks `if (!function_exists('sfagent_crop_book_shortcode'))` before declaring; safe to re-upload.

- **PHP version target:** 7.4 minimum (matches uPress baseline).

- **Deployment:** team_00 uploads this file once via the uPress File Manager to `wp-content/mu-plugins/sfagent-crop-book-shortcode.php` (mode 0644, owner web). Documented in the runbook section.

---

## 8. SPA — `sfagent-crop-book.js` (most defect-prone component)

### 8.1 Top-level shape

```js
(function () {
  'use strict';
  const ROOT = document.querySelector('.sfa-crop-book');
  if (!ROOT) return;

  let DATA = null;

  fetch(window.CROP_BOOK_DATA_URL)
    .then(r => r.json())
    .then(data => {
      DATA = data;
      buildIndex();
      hookSearch();
      hookCategoryTabs();
      hookSeasonFilters();
      hookDtmSlider();
      window.addEventListener('hashchange', routeFromHash);
      routeFromHash();
    })
    .catch(err => {
      ROOT.innerHTML = '<p class="sfa-crop-book-error">שגיאה בטעינת ספר גידולים</p>';
      console.error('Crop book data fetch failed:', err);
    });

  // ... helpers below
})();
```

### 8.2 Filter-parity invariant (AC-04)

The Flask `/api/crops` endpoint at `crop_book/views.py:234-304` is the **semantic SSoT**. The SPA must produce identical crop-id sets for every input combination. Specifically:

| Filter | Flask logic | JS logic (must match exactly) |
|--------|-------------|-------------------------------|
| `q` (search) | ILIKE on `name_he OR name_en OR scientific_name` | Case-insensitive substring match on the same 3 fields |
| `category` | `Crop.category == val` (or all if empty/"all") | `crop.category === val` (or pass-through) |
| `season[]` | OR over default-variety `planting_season` text containing any token from any selected season key (PATCH01 `getlist`) | OR over default-variety `planting_season` lowercased substring match against any token from any selected season key |
| `dtm_max` | default-variety `days_to_maturity <= dtm_max` (null DTM excluded) | same — null DTM filtered out when `dtm_max` is set |

**Default variety selection (must match views.py):** prefer `is_default=true`; fallback to first variety in the list (varieties already ordered by insert order from the importer — preserve this in the JSON via `varieties.sort(key=lambda v: v.id)` in `_crop_to_dict`).

### 8.3 Detail panel — 8 tabs

Each tab is a `<section class="sfa-cb-tab" data-tab="{key}">` already in the body shell DOM (rendered server-side by Jinja). The SPA fills the **content** of each tab when a crop is selected. Tab keys: `varieties | description | economics | care | equipment | sources | timeline | field-data`.

**Equipment tab visibility (AC-07):** if `crop.varieties.every(v => !v.seeder && !v.seeder_front_gear && !v.seeder_rear_gear && !v.seeder_roller_plate)` → set `display:none` on the equipment tab + its tab button.

**Timeline ruler (AC-08, R2 — F-190-WP004-02):** the public timeline parity SSoT is the locked Flask view at `crop_book/views.py:197`:

```python
# views.py:195–197
hw_max = default_var.harvest_window_max_days or 0
total_weeks = max(1, -(-hw_max // 7))  # ruler: harvest_window only
```

The SPA must mirror exactly — **default variety only** (NOT max across all varieties), `null` coerced to `0`, floor-of-1 on the result:

```js
const dv = crop.varieties.find(v => v.is_default) || crop.varieties[0];
const hwMax = (dv && dv.harvest_window_max_days) || 0;
const totalWeeks = Math.max(1, Math.ceil(hwMax / 7));
// Render totalWeeks ticks (NOT totalWeeks + 1 — see AC-08).
```

Render exactly `totalWeeks` tick marks (the ruler width represents `totalWeeks` whole weeks). The `max(1, ...)` ensures a degenerate variety with `hw_max=0` still produces a single-week ruler instead of an empty axis — matches the locked Flask behavior precisely.

**Description entity tags:** parse the description HTML for `<span class="etag" data-etype="..." data-eid="...">`; on hover, look up `DATA.entity_registry.entities[etype][eid]` → show tooltip with `nameHe + (typeLabel)`. Mirror `crop_book.js:49-67`.

### 8.4 Hash routing (AC-05)

`#crop-{id}` → set `currentCropId = parseInt(id, 10)`; show detail panel; populate tabs from `DATA.crops.find(c => c.id === currentCropId)`. On invalid/empty id → show index grid.

### 8.5 No external dependencies

The SPA is **vanilla JS only** — no React, no jQuery, no fetch polyfill. Target browsers: evergreen Chrome/Safari/Firefox. **No Babel transpile** — write ES2018 baseline.

---

## 9. Templates

### 9.1 `crop_book_body.html` (the WordPress fragment)

Outline:
```html
<div class="sfa-crop-book" dir="rtl" lang="he">
  <style>/* ~120 lines inline CSS — RTL, category color tokens, tab/grid layout, detail panel */</style>

  <div class="sfa-cb-search-row">
    <input type="text" class="sfa-cb-search" placeholder="חיפוש..." aria-label="חיפוש גידול">
    <div class="sfa-cb-category-tabs">
      <button data-cat="all" class="active">הכל</button>
      <button data-cat="vegetables">ירקות</button>
      <!-- 8 buttons -->
    </div>
  </div>

  <div class="sfa-cb-filter-row">
    <fieldset class="sfa-cb-seasons">
      <label><input type="checkbox" data-season="summer">☀️ קיץ</label>
      <!-- 4 -->
    </fieldset>
    <input type="range" class="sfa-cb-dtm" min="0" max="365" step="5" value="365">
  </div>

  <main class="sfa-cb-grid"></main>           <!-- index cards (built by JS) -->
  <section class="sfa-cb-detail" hidden>
    <header><h2 class="sfa-cb-crop-name"></h2></header>
    <nav class="sfa-cb-tabs">
      <button data-tab="varieties" class="active">זנים</button>
      <button data-tab="description">תיאור</button>
      <button data-tab="economics">כלכלה</button>
      <button data-tab="care">טיפולים</button>
      <button data-tab="equipment">ציוד</button>
      <button data-tab="sources">מקורות</button>
      <button data-tab="timeline">ציר זמן</button>
      <button data-tab="field-data">נתוני שדה</button>
    </nav>
    <section class="sfa-cb-tab" data-tab="varieties"></section>
    <!-- 7 more empty tab sections -->
  </section>

  <script>window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json";</script>
  <script>{{ spa_js | safe }}</script>     <!-- inlined sfagent-crop-book.js content -->
</div>
```

`spa_js` is read once at render time from `static/sfagent-crop-book.js` and passed into the Jinja template context.

### 9.2 `crop_book.html` (full standalone)

A `<!DOCTYPE html>` + `<head>` + `<body>` shell that includes the body fragment via `{% include "crop_book_body.html" %}`. Used for local preview (`python -m http.server` from the output dir → open in browser). Not uploaded to WordPress.

---

## 10. CLI runbook section (added to `UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`)

**Section name:** `Crop Book publish (S003 / WP004)`. Append after the existing market-report section. Include:

1. **Prerequisites** — alembic head ≥ 040; seed importer has run; `UPRESS_WP_*` env vars set as for market report (no new credentials).
2. **One-time mu-plugin install** — step-by-step uPress File Manager upload of `wordpress/mu-plugins/sfagent-crop-book-shortcode.php` to `/wp-content/mu-plugins/`.
3. **First publish** — `python -m organic_market_agent crop_book_publish --upload --set-mou-url`.
4. **Smoke test** —
   - `curl -sSI https://www.nimrod.bio/wp-content/uploads/.../sfagent-crop-book-manifest-of-urls.json` returns 200.
   - `curl -sS .../sfagent-crop-book-data.json | jq '.schema'` returns `"crop_book.v1"`.
   - Create a WP page with `[sfagent_crop_book]` shortcode — page renders the SPA.
5. **Failure modes** —
   - "ספר גידולים — בטעינה" placeholder visible → option not set or MoU URL 404. Re-run with `--set-mou-url`.
   - SPA loads but no crops appear → data.json fetch failed (browser console). Check Mixed Content (must be HTTPS), check media URL is public.
   - Filter returns wrong set → check parity test suite.

---

## 11. Acceptance Criteria

| AC | Criterion | Evidence |
|----|-----------|----------|
| AC-01 | `CropBookPublisher.run(session, Path("/tmp/cb"))` writes 3 artifacts (body, data.json, manifest.json) — files exist, sizes > 0. | `tests/crop_book/test_publisher.py::test_run_writes_three_artifacts` |
| AC-02 | `sfagent-crop-book-data.json` parses as JSON and contains top-level keys: `schema`, `data_version`, `generated_at`, `categories`, `season_tokens`, `families`, `conversion_groups`, `conversions`, `entity_registry`, `crops`. | `test_publisher.py::test_data_schema_keys` |
| AC-03 | Data JSON contains `>= 52` crops and `>= 242` varieties total against the seeded DB. | `test_publisher.py::test_full_seed_present` |
| AC-04 | **Filter parity matrix** — for the 12-case input matrix below, the JS filter produces identical crop-id sets as Flask `/api/crops`. Test runs against jsdom-loaded SPA + a Flask test client over the same fixture DB. | `tests/crop_book/test_filter_parity.py` |
| AC-05 | Loading the body in jsdom + setting `location.hash = "#crop-{ID}"` shows the detail panel for that crop with the correct `name_he` rendered. | `test_publisher.py::test_hash_routing` |
| AC-06 | All 8 tabs render with the same primary fields the Flask `crop_detail` view passes (sample 3 representative crops: one with seeder data, one without, one with rich source values). Snapshot diff is byte-stable across runs. | `test_publisher.py::test_tab_snapshots` |
| AC-07 | For a crop where no variety has any `seeder*` field, the equipment tab's nav button has `style="display: none"` (or equivalent visibility-off) after detail panel population. | `test_publisher.py::test_equipment_tab_hidden_when_no_seeder` |
| AC-08 | Timeline ruler tick count = `max(1, ceil(default_variety.harvest_window_max_days / 7))` (default-variety only; null coerced to 0; floor-of-1). Mirrors `views.py:197` exactly. Fixtures: hw_max=21 → 3 ticks; hw_max=22 → 4 ticks; hw_max=0 → 1 tick; hw_max=null → 1 tick. | `test_publisher.py::test_timeline_ruler_weeks` (all 4 fixtures) |
| AC-09 | Multi-season filter selecting `[summer, fall]` returns crops whose default-variety `planting_season` contains either summer or fall tokens (not AND). | `test_filter_parity.py::test_multi_season_or` |
| AC-10 | `dispatch_upload(Path("/tmp/cb"), profile="crop_book")` against a mocked `requests.Session` posts 4 artifacts to `/wp/v2/media` with the canonical names from §5.1; returns `UploadResult(success=True, protocol_used="wp_rest", success_count=4)`. | `tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile` |
| AC-11 | `php -l wordpress/mu-plugins/sfagent-crop-book-shortcode.php` exits 0; static grep confirms `add_shortcode('sfagent_crop_book',`, `register_setting(.*sfagent_crop_book_manifest_of_urls_url`, `wp_remote_get`, the **literal sentinel** `window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"`, and the **4-arg `str_replace` form with `$count` check** (`if ( $count === 0 )`) are all present. | `test_wp_upload_crop_book.py::test_mu_plugin_static_lint` (uses `subprocess.run(['php', '-l', ...])`; skip with `pytest.skip` if PHP not installed) |
| AC-12 | CLI `python -m organic_market_agent crop_book_publish --output-dir /tmp/cb` exits 0 in CI with the seed DB; produces 3 files. | `test_publisher.py::test_cli_smoke` (using `click.testing.CliRunner`) |
| AC-13 | Body fragment root element has `dir="rtl"` and `lang="he"` attributes. | `test_publisher.py::test_rtl_lang_attrs` |
| AC-14 | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL. | CI step (post-build, before commit) |
| AC-15 | The `profile="market"` branch of `dispatch_upload` is unchanged behaviorally — running the existing market-report test suite (untouched) still passes. | Existing `tests/test_publisher.py` + `tests/test_upload_dispatch.py` continue to pass. |
| AC-16 | No edits to LOD500_LOCKED files: `crop_book/models.py`, `crop_book/views.py`, all migrations 035–040, `crop_book/templates/{index,crop,_macros}.html`, `crop_book/static/{crop_book.css,crop_book.js}`. *(R2: `entity_registry.js` removed from this list — it is not tracked in `HEAD`; WP004 owns its own canonical registry per §2.4.)* | `git diff` review at L-GATE_B; constitutional check by team_190. |
| AC-17 | **Publisher sentinel invariant (R2 — F-190-WP004-03):** `CropBookPublisher.run` raises `CropBookPublishAbortError` if the rendered `crop_book_body.html` does not contain the literal string `window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"`. Tested by deliberately mutating the template to remove the sentinel and asserting the exception. | `test_publisher.py::test_body_sentinel_invariant_raises_when_missing` + `::test_body_sentinel_present_on_normal_render` |
| AC-18 | **Shortcode substitution-miss path (R2 — F-190-WP004-03):** when the body fragment served from WP media has no sentinel, the PHP shortcode logs an error and returns the placeholder div — does NOT emit body HTML with the relative `./sfagent-crop-book-data.json` URL still present. Tested via static-lint pattern check on the mu-plugin source (see AC-11) plus a runtime PHP-CLI fixture test that runs the shortcode function against a sentinel-stripped fixture body. | `test_wp_upload_crop_book.py::test_shortcode_substitution_miss_returns_placeholder` (skip if PHP-CLI unavailable) |
| AC-19 | **Entity registry source-of-truth (R2 — F-190-WP004-01):** `entity_registry_data.ENTITY_REGISTRY` validates against the schema declared in §2.4 (top-level keys `version`, `type_labels`, `entities`; entity-type subkeys `pest`, `disease`, `equip`, `input`, `technique`, `crop`); the publisher import path is `from organic_market_agent.crop_book.publisher.entity_registry_data import ENTITY_REGISTRY` (no file I/O, no regex); a known entity (`pest:diamondback-moth`) parses through to the SPA JSON blob. | `test_publisher.py::test_entity_registry_schema` + `::test_entity_registry_known_entity_present` |

### 11.1 Filter parity matrix (AC-04)

12 cases — all run twice (once via Flask test client, once via jsdom-loaded SPA), assert id-set equality:

| # | q | category | season[] | dtm_max |
|---|---|---|---|---|
| 1 | "" | all | [] | 365 |
| 2 | "" | vegetables | [] | 365 |
| 3 | "" | herbs | [] | 365 |
| 4 | "tomato" | all | [] | 365 |
| 5 | "עגב" | all | [] | 365 |
| 6 | "" | all | [summer] | 365 |
| 7 | "" | all | [winter] | 365 |
| 8 | "" | all | [summer, fall] | 365 |
| 9 | "" | all | [summer, spring, winter, fall] | 365 |
| 10 | "" | all | [] | 60 |
| 11 | "" | all | [] | 30 |
| 12 | "tomato" | vegetables | [summer] | 90 |

---

## 12. Constitutional invariants

| Iron Rule | Application to WP004 |
|-----------|----------------------|
| #1 Cross-engine validator | sfa_build = Sonnet 4.6 (Claude). team_190 validator must be **non-Claude** (Cursor Composer or Codex). |
| #2 Physical lean-kit | No lean-kit changes. |
| #3 Repo-internal `spec_ref` | This file. |
| #4 Single writer on roadmap | team_100 commits the WP004 entry; sfa_build does not touch `_aos/roadmap.yaml`. |
| #5 Final validation owned by team_190 | L-GATE_S Round 1 + L-GATE_V both by team_190. |
| #6 Inter-team via `_COMMUNICATION/` | Bundle at `_COMMUNICATION/team_190/SFA-S003-P001-WP004/`. |
| #7 API-only structured mutations | DB online; CropBookPublisher is read-only (SELECT). No structured mutations. Roadmap is spoke-native (file-based per ADR034 R9). |
| #8 Port canon | No new long-running listeners (publisher is one-shot CLI). |
| #9 Universal team numbering | team_100 / team_10 / team_190 / team_99 / team_191 — all canonical. |
| #10/#11 Governance flow | No `_aos/governance/` writes. |
| #12 gov-update locked | N/A — no governance changes. |
| #13 Thin orchestrator | N/A — this is product code, not an AOS command. |

**Raw material guard:** `_raw_material/` is not touched. Verified via `git diff --stat` constraint.

**Directory authority:** sfa_build (team_10) writes only to `organic_market_agent/`, `tests/`, `wordpress/`, `documentation/`, and `_COMMUNICATION/team_10/`. No writes to `_aos/`.

---

## 13. Build sequence

10 ordered steps for the builder. Each step has its own commit; no monolithic squash.

1. **Scaffold** — create `crop_book/publisher/` package with empty `engine.py` skeleton and 3 empty templates. Commit "feat(S003-WP004): scaffold publisher package". (~30 min)
2. **Data builder** — `_*_to_dict` helpers + queries + JSON assembly + manifest writer. `test_publisher.py::test_data_schema_keys`, `test_full_seed_present` PASS. Commit. (~2 h)
3. **Entity registry data module (R2 — F-190-WP004-01)** — author `organic_market_agent/crop_book/publisher/entity_registry_data.py` with the canonical `ENTITY_REGISTRY: dict` (transcribed from the working-tree WP003 JS: 7 pests, 5 diseases, 3 equipment, 5 inputs, 6 techniques, 4 crops). Add schema validator. Tests AC-19 PASS. Commit. (~45 min)
4. **SPA JS — index/grid + search + filters** — port logic from `views.py:234-304`. Get parity matrix cases #1–#5 PASSING. Commit. (~3 h)
5. **SPA JS — detail panel + tabs + hash routing** — port from `crop.html` + `crop_book.js`. AC-05/06/07/08 PASSING. Commit. (~3 h)
6. **Templates + Jinja inlining** — `crop_book_body.html` with inlined CSS + JS, `crop_book.html` for preview. AC-13 PASSING. Commit. (~1 h)
7. **wp_upload + dispatch_upload extensions** — new constants + `upload_all_crop_book_artifacts` + `profile` kwarg. AC-10/15 PASSING. Commit. (~1 h)
8. **CLI subcommand** — `crop_book_publish` in `__main__.py`. AC-12 PASSING. Commit. (~1 h)
9. **mu-plugin PHP + runbook** — author `sfagent-crop-book-shortcode.php`, append runbook section. AC-11 PASSING. Commit. (~1.5 h)
10. **Final test sweep + validate_aos.sh** — full pytest run, all 19 ACs verified (16 R1 + AC-17/18/19 added in R2), validate_aos.sh 0 FAIL. AC-14 PASSING. Commit BUILD_REPORT. (~30 min)

Total budget: **~14 h** of focused builder time. Recommend the builder break the JS work (steps 4–5) over two sessions if needed; it's the highest-defect-density block.

---

## 14. Risk register

| ID | Risk | Severity | Mitigation |
|----|------|----------|-----------|
| R-WP004-01 | SPA filter parity drift — JS logic diverges from Flask under edge cases not covered by the 12-case matrix. | HIGH | AC-04 matrix; team_190 may add cases at L-GATE_V. Property-based parity test (Hypothesis) is a stretch goal. |
| R-WP004-02 | Bundle size — 5 MB raw JSON is borderline for some browsers/connections. | MEDIUM | Server gzip is automatic on uPress. Measure raw + gzipped at L-GATE_B; if gzipped > 1 MB, defer optimization (chunking, paging) to a follow-up WP. |
| R-WP004-03 | mu-plugin install requires manual uPress panel step. | LOW | Documented in runbook; precedent set by `sfagent-allow-json.php`. team_00 owns this step. |
| R-WP004-04 | ~~`entity_registry.js` regex extraction breaks if the file format changes.~~ **OBSOLETE in R2** — replaced by Python-owned `entity_registry_data.py` (F-190-WP004-01 remediation). Type-checked at import time; AC-19 asserts schema + a known entity. No regex, no file parsing. | RESOLVED |
| R-WP004-05 | WP `wp_remote_get` timeout under slow uPress edges → shortcode renders placeholder. | LOW | Transient; user reload fixes. 5-minute transient cache absorbs most variance. |
| R-WP004-06 | Body-HTML `str_replace` substitution for `CROP_BOOK_DATA_URL` is fragile if the body fragment drifts. | LOW (mitigated, R2) | Two-sided invariants now ACs (R2 — F-190-WP004-03): publisher AC-17 raises `CropBookPublishAbortError` if the literal sentinel is missing from the rendered body; PHP shortcode AC-18 uses 4-arg `str_replace` with `$count` check, logs + returns placeholder on miss. AC-11 grep enforces the sentinel string + count check are present in the mu-plugin. |

---

## 15. Out of scope (deferred to S004 or later)

- Editing/admin write paths in WordPress.
- Crop images / photo gallery.
- Daily cron auto-publish.
- Shared CSS deployment (sfagent-base.css unification across market and crop book).
- Per-variety hash routes.
- Mobile-specific responsive tuning beyond inheriting RTL + sane defaults.
- Combining market-report + crop-book into a unified shortcode.
- Internationalization beyond Hebrew (English UI strings welcome but not required).
- **WP003 admin entity-registry asset gap** — the locked admin templates reference `crop_book/static/entity_registry.js` which is not tracked in `HEAD`. WP004 routes around this by owning its own canonical Python registry (§2.4). Restoring/committing the JS file for the admin tooltip surface is a separate follow-up WP, not in WP004 scope.

---

## 16. Definition of Done (LOD500)

LOD400 → LOD500_LOCKED requires:
1. All 19 ACs PASS (sfa_build self-attestation; R2 added AC-17/18/19).
2. team_190 L-GATE_V verdict = PASS (no MAJOR or BLOCKER findings).
3. Production smoke test by team_99: mu-plugin uploaded; first publish executed; WP page renders SPA; filter parity verified on live data.
4. validate_aos.sh = 0 FAIL.
5. roadmap.yaml updated by team_100 (single-writer rule).
6. Build report at `_COMMUNICATION/TEAM_10/SFA-S003-P001-WP004/BUILD_REPORT_v1.0.0.md`.

---

## 17. Decision log (team_00, 2026-05-09)

| # | Decision | Resolution |
|---|----------|-----------|
| A | SPA data delivery | **Separate JSON file** (`sfagent-crop-book-data.json`). Body HTML stays ~30–60 KB; SPA fetches data on load. |
| B | Shortcode install path | **mu-plugin via uPress panel** — ship `wordpress/mu-plugins/sfagent-crop-book-shortcode.php` in repo, team_00 installs once. Single-purpose file (separate from `sfagent-allow-json.php`). |
| C | Effort tier | **LARGE** — JS parity work is substantial (~6 h of ~14 h total). |
| D | Cron wiring | **CLI-only for v1.** No `scheduler/pipeline.py` changes; re-publish on demand only. |

---

## 18. Round 2 changelog (response to team_190 verdict 2026-05-10, commit `feee36c`)

| Finding | Severity | Remediation in this revision |
|---------|----------|------------------------------|
| F-190-WP004-01 | BLOCKER | §2.4 added — Python-owned `crop_book/publisher/entity_registry_data.py` is the canonical SSoT for the SPA's entity registry. §4 updated (no JS parsing, no regex). AC-16 updated (`entity_registry.js` removed from lock list — file is not tracked anyway). AC-19 added (schema + known-entity assertions). §13 step 3 rewritten (transcribe registry, validate, no file I/O). R-WP004-04 marked OBSOLETE. §15 explicitly defers the WP003 admin-tooltip gap to a follow-up WP. |
| F-190-WP004-02 | BLOCKER | §8.3 rewritten to mirror `views.py:195–197` exactly: **default variety only**, `null → 0`, `max(1, ceil(hw_max/7))`. AC-08 updated with 4 fixtures (hw_max=21/22/0/null). Removed the contradictory "max across varieties" wording. |
| F-190-WP004-03 | MAJOR | §5.3 rewritten with named sentinel constant + 4-arg `str_replace` `$count` check + explicit error_log + placeholder return. §7 step 5 updated. AC-11 grep extended to require sentinel + `$count` check in PHP. AC-17 added (publisher sentinel invariant raises). AC-18 added (PHP miss-path returns placeholder). R-WP004-06 mitigation updated. |
| F-190-WP004-04 | MINOR | Roadmap WP004 entry updated by team_100 in this revision: `current_lean_gate: L-GATE_S`, `lod_status: LOD400_REVIEW_R2`, gate_history extended with R1 BLOCKED entry + R2 awaiting. (Roadmap update is separate from this spec file but lands in the same R2 commit.) |

AC count grew 16 → 19. R-WP004-04 RESOLVED. R-WP004-06 downgraded MEDIUM → LOW (mitigated). All Round 1 BLOCKER findings remediated; MAJOR remediated; MINOR addressed in roadmap.
