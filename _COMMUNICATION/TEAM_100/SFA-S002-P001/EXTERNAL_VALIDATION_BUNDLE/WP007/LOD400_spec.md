# LOD400 — SFA-S002-P001-WP007 — HTTP Upload Migration (WP REST API)

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP007
**Type:** LOD400_SPEC
**Status:** READY for L-GATE_BUILD
**Builder:** sfa_build (Sonnet, Team 10)
**Production validator:** team_99
**QA:** Team 50
**Validator:** external (cross-engine — code merge to main)
**Priority:** P0 — actual blocker for F-01 launch regression

---

## 1. Goal

Replace SFA's primary publish-upload path from **FTPS port 21** (blocked by Bezeq home-network egress) to **HTTPS port 443** via the **uPress WP REST API**, modeled after the proven `shaked-wg-agent/shaked_wg_agent/publisher/wp_upload.py` reference (same uPress server, same hosting environment, same network egress conditions, currently works).

---

## 2. Root cause re-classification (binding)

team_99's WP006 deploy log (commit `3754050`) and team_100's verification via `/server` confirmed:

- Port 21 outbound is **BLOCKED at the Bezeq home-network egress layer**, on both Mac and waldhomeserver. uPress IP whitelist did NOT unblock.
- Port 443 to the same uPress IP (`185.201.148.144`) is **OPEN**.
- WP REST API at `https://www.nimrod.bio/wp-json/` returns HTTP 200 with shaked-wg credentials (verified from server).
- shaked-wg-agent runs on the same host with the same constraints and uploads via WP REST API successfully (3× daily cron).

The Python `ReusedSessionFTP_TLS` subclass in SFA is correct (WP006 verified). FTPS code may remain as defensive fallback, but cannot be the primary path.

---

## 3. Reference (read-only — do NOT modify)

Authoritative working pattern:
- `/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/wp_upload.py`
- shaked-wg-agent's production `.env` keys (visible on server): `UPRESS_WP_REST_BASE`, `UPRESS_WP_APP_USER`, `UPRESS_WP_APP_PASS`

Pattern essence (copy faithfully into SFA):
```python
def _token() -> str:
    user = os.environ["UPRESS_WP_APP_USER"]
    pw = os.environ["UPRESS_WP_APP_PASS"]
    return base64.b64encode(f"{user}:{pw}".encode()).decode()

# DELETE previous media_id (so URL stays clean — no -1/-2 suffix)
requests.delete(f"{base}/wp/v2/media/{old_id}?force=1", headers=headers_auth, timeout=15)

# POST upload with Content-Disposition naming the canonical filename
resp = requests.post(
    f"{base}/wp/v2/media",
    headers={**headers_auth,
             "Content-Disposition": f'attachment; filename="{canonical_filename}"',
             "Content-Type": "application/json|text/html"},
    data=path.read_bytes(),
    timeout=30,
)
```

---

## 4. Scope (4 published artifacts)

The pipeline produces these in `output/public/`:

| File | Content-Type | Canonical filename for upload |
|------|--------------|-------------------------------|
| `manifest.json` | `application/json` | `sfagent-manifest.json` (or chosen) |
| `public_report.json` | `application/json` | `sfagent-public-report.json` |
| `public_report.html` | `text/html` | `sfagent-public-report.html` |
| `public_report_body.html` | `text/html` | `sfagent-public-report-body.html` |

WP `/wp/v2/media` will store these in WP media library at a date-based path (`wp-content/uploads/YYYY/MM/`). The returned `source_url` is what consumers reference.

---

## 5. Acceptance Criteria

### AC-01 — `wp_upload.py` exists in SFA
- `organic_market_agent/publisher/wp_upload.py` modeled on shaked-wg reference.
- Functions: `upload_artifact(local_path, canonical_filename, content_type)` returning `(media_id, public_url)`.
- HTTP Basic auth via `UPRESS_WP_APP_USER` + `UPRESS_WP_APP_PASS`.
- Per-canonical-filename media_id tracking file under `data/.wp_media_id_*` for delete-before-overwrite.

### AC-02 — Pipeline integration
- `organic_market_agent/publisher/engine.py` (or wherever `--upload` is wired) calls `wp_upload.upload_artifact` for each of the 4 artifacts.
- New env keys recognized: `UPRESS_WP_REST_BASE` (default `https://www.nimrod.bio/wp-json`), `UPRESS_WP_APP_USER`, `UPRESS_WP_APP_PASS`.
- `.env.example` updated with the 3 new keys (no real values).

### AC-03 — Failure-mode policy
- If WP REST upload fails AND `UPRESS_FALLBACK_FTPS=1` is set, fall back to existing FTPS code (so a future move to a non-blocked network doesn't break).
- Default: WP REST primary, no FTPS attempt.
- All upload failures recorded in `pipeline_alerts` with the protocol used.

### AC-04 — Shortcode + manifest URL contract
The current shortcode `[sfagent_market_report]` in [`scripts/wp_shortcode_install.py`](../../../../scripts/wp_shortcode_install.py) reads from fixed paths under `wp-content/uploads/market/`. With WP REST media library, paths become dynamic.

Builder MUST do ONE of:
- **A. Manifest URL pointer** *(preferred — minimal shortcode change):* The pipeline writes a single small file `sfagent-manifest-of-urls.json` to media library. The shortcode is updated to fetch THIS pointer file from a stable URL, then dereferences to the actual artifact URLs.
- **B. WP option storage:** Pipeline writes a WP option (via `/wp/v2/options/{key}`) holding the latest URLs. Shortcode reads the option.
- **C. Filename slug pinning:** Verify uPress WP version honors a stable URL when the same `canonical_filename` is reused with delete-before-overwrite (per shaked-wg pattern). If `source_url` returns a stable path, shortcode can hard-code it.

Builder picks one and documents the choice in `_COMMUNICATION/team_10/SFA-S002-P001-WP007/SHORTCODE_INTEGRATION_DECISION.md`. Implement the chosen path. Update `wp_shortcode_install.py` accordingly.

### AC-05 — Tests
- `tests/test_wp_upload.py` — unit tests with mocked `requests.post`/`requests.delete`:
  - happy-path upload returns `(media_id, public_url)`
  - delete-before-overwrite when media_id file exists
  - 401/403 raises `MissingCredentialsError` (or equivalent)
  - HTTP timeout retry behavior (mirror MAX_RETRIES + BACKOFF_SECONDS pattern from `ftps_upload.py`)
  - Content-Type per file extension
- All tests pass.

### AC-06 — Environment hand-off documented
A note for team_99 in `_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md`:
- Exact lines to add to `/data/projects/smallfarmsagents/.env`:
  - `UPRESS_WP_REST_BASE=https://www.nimrod.bio/wp-json`
  - `UPRESS_WP_APP_USER=<from team_00>`
  - `UPRESS_WP_APP_PASS=<from team_00>`
- Quick smoke after env update: `python -m organic_market_agent run_publisher --upload`.
- Expected: 4 artifacts uploaded; `manifest.artifact_version` advances; public page shows fresh data.

### AC-07 — Documentation
- `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md` — section 4 updated to describe WP REST upload as primary; FTPS as opt-in fallback.
- `docs/UPRESS_WORDPRESS_STANDARD_v2.md` — append a note that for spokes whose host network blocks port 21 outbound, WP REST API is the canonical alternative.
- `CHANGELOG.md` `[Unreleased]` `### Changed` entry.

---

## 6. Files in scope

### CREATE
- `organic_market_agent/publisher/wp_upload.py`
- `tests/test_wp_upload.py`
- `_COMMUNICATION/team_10/SFA-S002-P001-WP007/SHORTCODE_INTEGRATION_DECISION.md`
- `_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md`

### UPDATE
- `organic_market_agent/publisher/engine.py` (or wherever upload is invoked) — route through `wp_upload.upload_artifact` first
- `organic_market_agent/utils/config.py` — add three WP REST config fields (matching env var names)
- `.env.example` — add three lines for new keys (no real values)
- `scripts/wp_shortcode_install.py` — update to follow the chosen integration path (AC-04)
- `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`
- `docs/UPRESS_WORDPRESS_STANDARD_v2.md`
- `CHANGELOG.md`

### DO NOT TOUCH
- `organic_market_agent/publisher/ftps_upload.py` — keep code path intact (defensive fallback under `UPRESS_FALLBACK_FTPS=1`)
- shaked-wg-agent codebase — reference only
- `_aos/governance/`, `_aos/roadmap.yaml`, `_aos/PENDING_DB_SYNC.yaml`
- DB schema, migrations, collectors, templates, CSS

---

## 7. Implementation notes

- **Auth header:** `Authorization: Basic <base64(user:pass)>`. Application password preserves spaces as 4-char-groups in some uPress UIs — strip spaces before base64-encoding (defensive).
- **Idempotency:** the delete-before-upload pattern keeps URLs stable. Track `media_id` per canonical filename in a tracker file (e.g., `data/.wp_media_id_{slug}`) to survive runs.
- **Content-Type discipline:** wrong Content-Type can cause uPress to refuse JSON uploads (it sometimes whitelists by extension). Use `application/json` for `.json` and `text/html; charset=utf-8` for `.html`.
- **WP allowed file types:** uPress may restrict media library upload extensions. If `.json` is rejected, try with `.txt` extension and override Content-Type — OR install a tiny "allow JSON in media library" mu-plugin (provide PHP snippet in `DEPLOY_HANDOFF.md` if needed).
- **Two FTP users (audit notes):**
  - `AgentsRoot@nimrod.bio` — root access (broader scope, retain only for FTPS fallback)
  - `HomeServer@nimrod.bio` — internal directory (preferred FTPS user when fallback is needed)
  - Neither used for WP REST — that uses the WP application password.

---

## 8. Test plan

### Unit (offline, mocked)
- `tests/test_wp_upload.py` per AC-05.

### Integration (when WP credentials available locally — optional)
- Smoke against staging or a sandbox WP install if available.

### Production (team_99 domain)
- After env update: `python -m organic_market_agent run_publisher --upload`.
- Verify `pipeline_alerts` has no `FTPS upload FAILED`.
- Verify public manifest URL serves the new artifact_version within 60s.
- WP003 Pass-2 re-run lifts AC-04 from FAIL to PASS.

---

## 9. Risks

| Risk | Mitigation |
|------|-----------|
| uPress WP rejects `.json` extension in media library | Use a tiny mu-plugin to allow `.json` MIME — snippet provided in DEPLOY_HANDOFF |
| WP application password not configured / expired | team_00 supplies fresh app password; document in DEPLOY_HANDOFF |
| Shortcode integration is more invasive than estimated | LOD400 §AC-04 offers 3 paths — builder picks lowest-friction |
| FTPS regression if `UPRESS_FALLBACK_FTPS` accidentally enabled in a non-blocked network | Defaults are safe; documented behavior |

---

## 10. Sprint estimate

**SMALL–NORMAL (1–3 days)** — pattern established in shaked-wg, verified accessible from server. Largest unknown: AC-04 shortcode integration choice + JSON MIME acceptance.

---

## 11. References

- WP006 (superseded): `_COMMUNICATION/TEAM_100/SFA-S002-P001-WP006/MANDATE_v1.0.0.md`
- team_99 deploy log (network diagnosis): commit `3754050` on `main`
- Reference impl: `/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/wp_upload.py`
- uPress standard: `docs/UPRESS_WORDPRESS_STANDARD_v2.md`
- shortcode: `scripts/wp_shortcode_install.py`
- Program package: `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md`

---

*LOD400 ready. L-GATE_E + L-GATE_S fast-tracked.*
