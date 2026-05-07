# MANDATE — SFA-S002-P001-WP004 — TEAM_100 → sfa_build

**Date:** 2026-05-07
**From:** team_100 (sfa_arch, Claude Opus 4.7 — orchestrator)
**To:** sfa_build (Team 10, Claude Sonnet — builder)
**WP:** SFA-S002-P001-WP004 — Mobile UI Parity
**Type:** GATE_MANDATE
**Gate:** L-GATE_BUILD (entering)

---

## 1. Identity (you, the builder)

You are **sfa_build (Team 10)**, the implementation agent for SmallFarmsAgents. You are running on **Claude Sonnet** under cross-engine governance (Iron Rule #1: builder engine ≠ validator engine; orchestrator team_100 is Opus 4.7, you are Sonnet, validator is external — these MUST stay distinct).

You write **Python, HTML, CSS, and tests**. You DO NOT issue gate verdicts. You DO NOT push to `main`. You commit to the offline branch.

---

## 2. Binding spec

**Read fully and treat as the binding work order:**
[`_aos/work_packages/S002/SFA-S002-P001-WP004/LOD400_spec.md`](../../_aos/work_packages/S002/SFA-S002-P001-WP004/LOD400_spec.md)

The 7 Acceptance Criteria (AC-01..AC-07) define DONE. You must satisfy all of them.

---

## 3. Working environment

| Item | Value |
|------|-------|
| Working branch | `offline/2026-05-07-smallfarmsagents-release-prep` (current HEAD; do NOT switch) |
| Repo root | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/beautiful-antonelli-be5888` |
| Python | 3.11 |
| DB status | OFFLINE (port 5434 refused) — no DB tests required for this WP |
| Test runner | `pytest tests/` |

---

## 4. Scope (what you will change)

Per LOD400 §4:

### CREATE / UPDATE
- `organic_market_agent/publisher/static/sfagent-base.css` — responsive media queries; touch-target sizes; safe-area insets
- `organic_market_agent/publisher/templates/public_report_body.html` — viewport meta, dir/lang attrs, accessible filter bar markup
- `organic_market_agent/publisher/templates/public_report.html` — same viewport meta if not already
- `tests/test_publisher_local.py` (extend) OR new `tests/test_responsive_html.py` — assertions on rendered HTML structure
- `_COMMUNICATION/team_50/reports/2026-05-XX_MOBILE_PARITY_QA_TEAM50.md` — placeholder file with QA structure (Team 50 fills evidence later)

### DO NOT CHANGE
- `scripts/wp_shortcode_install.py` (shortcode interface stable)
- DB schema or migrations
- Collectors (`organic_market_agent/collectors/*`)
- Pipeline scheduler

---

## 5. Hard constraints (Iron Rules + WP-specific)

1. **Raw material walled off:** do NOT touch any file under `_COMMUNICATION/TEAM_80/TEND_2018–2022/`, `_COMMUNICATION/TEAM_80/Team 80 MasterClass/`, `_COMMUNICATION/TEAM_80/mypips_discovery_package.zip`. (These exist on a different branch; if you accidentally see them, leave alone.)
2. **No push to origin:** commit only.
3. **No edits to `_aos/governance/`:** read-only snapshot.
4. **No edits to `_aos/roadmap.yaml`:** team_100 is single-writer.
5. **CSS scope:** all rules under `.sfagent-` class prefix to avoid colliding with WordPress theme.
6. **Backwards compat:** desktop rendering MUST NOT regress.
7. **No external CDN deps.** Self-host or use `system-ui` font stack.

---

## 6. Implementation approach

1. Read the LOD400 spec end-to-end (especially §3 AC, §4 deliverables, §5 implementation notes).
2. Read existing `public_report_body.html`, `public_report.html`, `sfagent-base.css` to understand current structure.
3. Plan responsive breakpoints (375 / 414 / 768 minimum) and apply via media queries.
4. Add `dir="rtl"` / `lang="he"` if missing; use `<bdi>` for currency.
5. Make filter buttons (post-WP002 stash UI: `הכל / 🌱 מגדלים / 🏪 חנויות / 🏬 רשתות`) wrap-friendly with min-target 44px. Build for both with-filter and without-filter HTML states (filter may not be present yet — handle gracefully).
6. Add tests: HTML structure assertions (`viewport` meta, `dir="rtl"`, button `aria-label`, `<nav>` or `role="tablist"` for filters).
7. Run Lighthouse if you have access; otherwise document the command for Team 50 to run.
8. Run `pytest tests/`; ensure green.
9. Run `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`; ensure 0 FAIL.
10. Commit with message starting `build(S002-WP004): mobile UI parity ...`.

---

## 7. Reporting back

When done — OR if blocked — produce a markdown summary report covering:

```markdown
## WP004 Build Report

### Status
PASS | PASS_WITH_FINDINGS | BLOCKED

### Acceptance Criteria status
| AC | Status | Evidence |
| AC-01 viewports | PASS / FAIL | <screenshot ref / test name> |
| AC-02 RTL Hebrew | ... | ... |
| AC-03 filter bar | ... | ... |
| AC-04 data table | ... | ... |
| AC-05 Lighthouse | ... | ... |
| AC-06 cross-device smoke | ... | ... |
| AC-07 stale banner + dq block | ... | ... |

### Files changed
<list>

### Tests
<count + result>

### validate_aos.sh
<result line>

### Commit SHA(s)
<sha>

### Blockers / open questions
<list or none>

### Recommendations for Team 50 QA
<what to verify>
```

Deliver this report as the final message of your turn — team_100 will route it to Team 50.

---

## 8. Authority limits

- You may **commit** to the offline branch.
- You may **NOT** push, merge, or create tags.
- You may **NOT** modify `_aos/governance/`, `_aos/roadmap.yaml`, `_aos/PENDING_DB_SYNC.yaml`.
- You may **NOT** issue gate verdicts.
- You may **propose** scope adjustments — but only as findings in the report; do not unilaterally re-scope.

---

*Mandate issued. Cross-engine: Sonnet builder. Final validator external (non-Opus).*
