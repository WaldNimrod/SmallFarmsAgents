---
id: MANDATE_WP-UI_L-GATE_V_R3_v2.0.0
from: team_100 (Chief System Architect — Claude Opus 4.7)
to: team_190 (External Constitutional Validator — non-Claude per IR#1)
date: 2026-05-28
type: L-GATE_V_MANDATE
gate: L-GATE_V (R3 — post-RE-BUILD)
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
priority: HIGH
status: ACTIVE
verdict: PENDING

engine_constraint: |
  Validator MUST be NON-CLAUDE (per Iron Rule #1: builder engine ≠ validator engine).
  Builders + orchestrator in this RE-BUILD cycle are Claude family
  (Claude Sonnet sub-agents B1, B2, B3, B4, B5, B6, B7, R-Controllers,
  R-CSS, D1, D2 + Claude Opus 4.7 orchestrator). Acceptable validator
  engines: GPT-5.5 / Cursor / Codex / any non-Claude.

reviewed_commit: e7e8bb7
build_branch: claude/sfa-ui-build-v2 (origin)
production_url: https://sfa.nimrod.bio/
build_report: _COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/BUILD_REPORT_v2.0.0.md
prior_attempts:
  - v1.0.0 → v1.0.1 → v1.0.2 (commit 740ea2c) — L-GATE_V R2 PASS but team_00 REVOKED via direct audit (commit dfb8cf1)
  - This R3 = post-revoke RE-BUILD cycle
---

# L-GATE_V MANDATE — SFA-S003-P002-WP-UI (R3 — post-RE-BUILD)

**Constitutional verdict requested.** The previous L-GATE_V R2 (verdict v1.0.1, 2026-05-27, commit 740ea2c) returned PASS but team_00 directly audited the live site and discovered ~91% of design CSS was dead code (HTML emitted invented class names, not the COMPONENTS.md BEM contract). team_00 REVOKED that verdict and mandated a full RE-BUILD. **This R3 mandate is the verification that the rebuild actually closes the visual-fidelity gap.**

## 0. Read these FIRST (in order)

1. **Mandate that triggered the rebuild:** `.claude/worktrees/gallant-elbakyan-727a60/_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md`
   - §1 four deliverables · §2 mandatory responsive · §3 per-route DOM contract · §5 acceptance criteria (57 total)

2. **LOD400 v1.0.3 §0.5 (CRITICAL — team_00 in-session approval):**
   `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` §0.5
   > "When mandate §3 BEM names diverge from COMPONENTS.md, COMPONENTS.md is the binding SSoT for actual class names emitted. Mandate §3 names are colloquial shorthand documenting intent — not literal grep targets."

   **What this means for you:** when validating §5.2 visual-fidelity ACs, grep against COMPONENTS.md names (right-hand column of BEM_MAPPING_TABLE in BUILD_REPORT v2.0.0 §3), NOT mandate §3 stubs. team_00 approved 2026-05-27 20:00 IDT.

3. **BUILD_REPORT v2.0.0** (consolidated): `_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/BUILD_REPORT_v2.0.0.md`
   - §3 BEM_MAPPING_TABLE: mandate stub → COMPONENTS.md canonical
   - §4 57-AC table
   - §5 findings (F-V2-01 through F-V2-05 — all INFO/NOTE, none blocking)

4. **Screenshot evidence (D2 sub-agent):** `_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/SCREENSHOTS_REPORT_v1.0.0.md`
   - 42 PNGs at `visual_diff/` (3 viewports × 14 routes)
   - Lighthouse mobile JSON+HTML

5. **COMPONENTS.md** (binding design contract): `.claude/worktrees/gallant-elbakyan-727a60/_archive/SFA-S003-P002-WP-UI/team_35/_handoff/COMPONENTS.md` — §1–§17.

## 1. Validation scope (57 ACs)

| Cluster | Count | Where defined |
|---------|-------|---------------|
| Inherited from v1.0.2 §5 | 38 | BUILD_REPORT §4.1 |
| NEW Visual fidelity (per-route DOM) | 14 | BUILD_REPORT §4.2 — **grep against COMPONENTS.md names** |
| NEW Responsive (3 viewports + no-h-scroll + touch targets) | 4 | BUILD_REPORT §4.3 + D2 screenshots |
| NEW DB-resilience (AC-DB-1 unknown-field fallback) | 1 | BUILD_REPORT §4.4 + live URL spot-check |
| **TOTAL** | **57** | |

## 2. Verification methodology (binding)

### 2.1 Visual fidelity (14 NEW ACs — §5.2)

For each of the 14 routes in mandate §3:

```bash
curl -sS "https://sfa.nimrod.bio{route}" | grep -c "{class}"
```

Use the **COMPONENTS.md names** from BUILD_REPORT v2.0.0 §3 BEM_MAPPING_TABLE right-hand column. Expect count ≥ 1 per required class per route.

**Do NOT grep mandate §3 stub names** (e.g., `module-card`) — those are colloquial. Grep the canonical names (`mod-card`, `mod-card__name`, etc.).

### 2.2 Responsive (4 NEW ACs — §5.3) — MANDATORY METHODOLOGY

Per mandate §2: "true CSS viewport emulation (Playwright/Chrome devtools), **NOT OS-window resize**."

Use Playwright (Python or Node) with `page.set_viewport_size({width, height})` OR `browser.new_context(viewport={...})`. Acceptable alternative: Chrome DevTools Protocol via `Emulation.setDeviceMetricsOverride`.

Cross-reference D2's 42 screenshots at `visual_diff/{viewport}__{route}.png` + their assertions in SCREENSHOTS_REPORT v1.0.0 §2 (shell-swap verification).

#### AC-R-1 — Mobile shell visibility at 390×844
```python
page.set_viewport_size({"width": 390, "height": 844})
page.goto("https://sfa.nimrod.bio/")
assert page.locator(".gj-shell").is_visible()
dt_display = page.evaluate("getComputedStyle(document.querySelector('.dt-shell')).display")
assert dt_display == "none"
```

#### AC-R-2 — Desktop shell visibility at 1280×900
```python
page.set_viewport_size({"width": 1280, "height": 900})
page.goto("https://sfa.nimrod.bio/")
assert page.locator(".dt-shell").is_visible()
gj_display = page.evaluate("getComputedStyle(document.querySelector('.gj-shell')).display")
assert gj_display == "none"
```

#### AC-R-3 — No horizontal scroll at 390px (all 14 routes)
```python
for route in ROUTES:
    page.goto(f"https://sfa.nimrod.bio{route}")
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert overflow <= 0, f"horizontal scroll at {route}: {overflow}px"
```

#### AC-R-4 — Touch targets ≥24×24 (Lighthouse target-size audit)
Run Lighthouse mobile against `/` and verify the `target-size` audit (under "Accessibility") returns 0 failures. D2 already executed Lighthouse — extract from JSON.

### 2.3 DB-resilience (1 NEW AC — §5.4)

#### AC-DB-1 — Unknown-field fallback DOM

```bash
curl -sS "https://sfa.nimrod.bio/crop-book/anise-hyssop/variety/variety-1" | grep -c "variety-fields__extras"
```

Expect ≥ 1 occurrence. Inspect the rendered output: the `<details>` block should contain `<summary>פרטים נוספים מהמקור (N)</summary>` followed by `<dl>` with extra-fields (8+ keys not in the 11-entry known_labels dictionary).

Spot-test logic: read `sfa_delivery/templates/pages/book_variety.php` and confirm:
- `$known_labels` dict has at least 11 entries (lines ~140–155)
- `$reserved_keys` exclusion list excludes identifier/system keys
- Iteration handles scalars + flat-scalar arrays + nested JSON (rendered as `<code>`) + array-of-objects (skipped)
- `is_internal_farm_use_only` filter is applied to `knowledge_notes` (lines ~197–201)

### 2.4 Inherited 38 ACs (§5.1)

Validate per LOD400 v1.0.2 §5 — most are inherited from prior R2 PASS work. Key spot-checks team_100 suggests:

- `/api/v1/health` returns 200 JSON `{status:"ok",...}`
- `/api/v1/ingest` POST with bad HMAC returns 401 (no regression in HmacAuthMiddleware)
- `community.php` has 0 `<form>` in `<main>` content (sidebar global search form is OK — LV-S-1 binding is about contribution writes, not navigation search)
- `validate_aos.sh` returns `0 FAIL`
- `php -l` on all 14 templates + 10 macros + 4 shells/layout + 10 controllers PASSES

## 3. Known caveats — non-blocking but read

| ID | Severity | Summary | Status |
|----|----------|---------|--------|
| F-V2-01 | INFO | Module card art slots have no hero images yet (CSS progressive enhancement fills with enlarged icon) | Tracked follow-up — not blocking |
| F-V2-02 | INFO | Sidebar feed-item slot empty (data hook = controller responsibility, not in scope) | Tracked follow-up — not blocking |
| F-V2-03 | LOW | D1 sub-agent appeared silent ~1h but completed cleanly | Process improvement — not blocking |
| F-V2-04 | INFO | Visual audit caught 5 bugs grep smoke missed | Process improvement — addressed in §2.2 of this mandate (Playwright required) |
| F-V2-05 | NOTE | `winning_source_class` pill regex is permissive (forward-compatible) | Design intent — not a defect |

team_00 has personally audited a sample of the live site post-RE-BUILD via Chrome MCP at 1280×900 (homepage, /crop-book/anise-hyssop, /crop-book/anise-hyssop/variety/variety-1, /market/prd017) and confirmed icons + BEM + mk-disclaimer copy + AC-DB-1 fallback render correctly. The R3 verdict is the cross-engine constitutional verification on top of that.

## 4. Disposition options

### PASS (clean — preferred)
All 57 ACs verified. team_100 proceeds to ADR042 closure:
1. Merge `claude/sfa-ui-build-v2` → `main` (ff or merge commit)
2. Push main + re-mirror `sfa_delivery/` from main (canonical-source sanity)
3. Flip roadmap `WP-UI: status=COMPLETE, lod_status=LOD500_LOCKED, current_lean_gate=L-GATE_V`
4. Issue archive mandate to team_191

### PASS_WITH_FINDINGS
Specify findings with severity (BLOCKER/MAJOR/MINOR/LOW/INFO), remediation owner, must_resolve_before flag. team_100 either remediates inline (and you re-verify R4) or files patch01.

### BLOCKED / FAIL
Any BLOCKER finding. team_100 will rebuild and re-dispatch.

## 5. Output

Write your verdict to:
`_COMMUNICATION/TEAM_190/VERDICT_WP-UI_L-GATE_V_R3_v1.0.0.md`

Use the canonical verdict format (§0 Verdict Box, §1 Summary, §2 Parameters, §3 Criteria Table, §4 Findings, §5 validate_aos.sh, §6 Disposition, §7 Next Step).

## 6. Branch context for validator activation

```bash
# Activate
cd /Users/nimrod/Documents/SmallFarmsAgents
git fetch origin
git checkout claude/sfa-ui-build-v2  # or work in your own validator worktree
git log --oneline -8  # confirm HEAD = e7e8bb7

# Read these in order (BEFORE running curls):
cat _aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md  # §0.5 first!
cat _COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/BUILD_REPORT_v2.0.0.md
cat _COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/SCREENSHOTS_REPORT_v1.0.0.md
ls visual_diff/  # 42 PNGs + lighthouse_mobile.{json,html}

# Then verify on live URL
curl -sS https://sfa.nimrod.bio/  | grep -c "mod-card"  # expect ≥ 8
curl -sS https://sfa.nimrod.bio/crop-book/anise-hyssop/variety/variety-1 | grep -c "variety-fields__extras"  # expect ≥ 1

# Playwright responsive (mandatory — see §2.2 above)
```

---

*Mandate filed 2026-05-28 by team_100 (Claude Opus 4.7) for SFA-S003-P002-WP-UI L-GATE_V R3 verification. Awaiting team_190 non-Claude verdict.*
