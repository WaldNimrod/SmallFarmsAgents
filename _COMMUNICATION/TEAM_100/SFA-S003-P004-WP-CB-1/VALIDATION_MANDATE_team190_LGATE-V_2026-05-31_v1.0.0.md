---
id: VALIDATION_MANDATE_SFA-S003-P004-WP-CB-1_L-GATE_V_v1.0.0
from: team_100 (Chief System Architect — smallfarmsagents spoke)
to: team_190 (Senior Constitutional Validator — external/non-Claude engine)
date: 2026-05-31
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P004-WP-CB-1
scope: ui
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "IR#1 cross-engine. builder = Claude (Sonnet sub-agent). architect = team_100 (Opus). validator (you) = team_190 NON-CLAUDE (GPT-5/Codex/Cursor). Claude MUST NOT self-issue this verdict (IR#1/#5)."
round: 1
---

# L-GATE_V Validation Mandate — SFA-S003-P004-WP-CB-1 (UI slice)

**Crop Book v1 — team_35 LOD300 design implemented into the Slim4/PHP delivery tier.**
**Branch:** `claude/wp-cb-1-ui-2026-05-31` · **Build commits:** `1456c48..7149ee4` (+ assets `4d7b1e8`)

> ⚠ **Iron Rule #1 / #5:** This is the constitutional final gate. It MUST be executed by a **non-Claude**
> engine (Nimrod runs team_190 in Cursor/Codex/GPT). team_100 (Opus) has done an *advisory* L-GATE_B
> verification only; it cannot and does not issue this verdict.

## Scope of this gate
Validate the **UI slice** of WP-CB-1 — the implementation of the team_35 LOD300 into `sfa_delivery/`. The
**backend slice** (calculators/assumptions/meta/field_policy) was already validated cross-engine (Target B PASS,
commit `fd7dfba`) and is LOCKED — out of scope here except to confirm the UI did not edit it.

## Validation criteria (per team_190.md §L-GATE_VALIDATE)
1. **UI ACs met** (LOD400 §11): AC-10 (audience switch + Simple/Full/Drill + AssumptionField + complete/partial
   via `prov_value`); AC-11 (JS↔Python calc parity for the interactive set — at least #1,#8,#10 tested);
   AC-13-local (COMPLETE crop → enabled calcs w/ correct numbers; PARTIAL crop → `*`/`—` + disabled calc + request-info).
2. **`validate_aos.sh` → 0 FAIL** (team_100 sees 29 PASS / 19 SKIP / 0 FAIL on a clean tree).
3. **No new Iron Rule violations** (constitutional checks below).
4. **Governance consistent** with code (roadmap gate_history reflects this build).
5. **Fidelity** to `FIELD_INTERFACE_MAP_v1.0.0.md` (alias resolver; no raw DB key to users; τ=0.40 stamped-state render).

## Artifacts to review (in order)
1. BUILD_REPORT: `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-1/BUILD_REPORT_UI_v1.0.0.md`
2. DISPATCH (scope/authority): `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/DISPATCH_sfa_build_UI_2026-05-31_v1.0.0.md`
3. Field contract: `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/FIELD_INTERFACE_MAP_v1.0.0.md`
4. LOD400 §10/§11: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-1/LOD400_spec.md`
5. Design SoT: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/LOD300 Crop Book v1.html`
6. Code at branch HEAD: `sfa_delivery/{app/Lib/FieldRegistry.php, app/Controllers/{Assumptions,CropBookView,Hub}Controller.php,
   app/routes.php, templates/macros/*, templates/pages/{book_crop,book_entry,calc_dash}.php,
   public_assets/{css/tokens.css,css/crop-book-v1.css,js/crop-book-v1.js}, tests/CropBookV1*Test.php}`

## Independent execution expected
```
cd sfa_delivery && composer test            # team_100 saw 96/96 (278 assertions)
php -l <each changed PHP file>               # expect clean
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .   # expect 0 FAIL (clean tree)
python3 -m pytest tests/crop_book/ -q        # expect 631 pass / 2 PRE-EXISTING fail only
git diff --name-only main..HEAD              # confirm: no LOCKED backend, no migration; _aos = roadmap + MIG2 spec only
```

## Constitutional checks (report each PASS/FAIL)
C1 directory authority (build wrote only under `sfa_delivery/` + `_COMMUNICATION/TEAM_10/`) · C2 roadmap authority
(builder made no `_aos/roadmap.yaml` edit — only team_100 did) · C3 IR#1 (builder Claude, validator you = non-Claude) ·
C4 LOCKED-backend integrity (no edit to calculators/assumptions/calculator_meta/field_policy/models/*.py or migrations) ·
C5 IR#5 (this verdict issued by team_190) · C6 LOD400 fidelity (FieldRegistry alias resolver honored; no raw DB key
rendered; τ=0.40 stamped-state render, no UI threshold math) · C7 model/asset integrity.

## Known/declared items (assess, don't re-discover)
- **PARTIAL (non-blocking, declared in BUILD_REPORT):** server-side filter execution on book_index; `/calc`
  PDF/CSV export; some calc-parity PHPUnit coverage (#7/#9/#12 formula-audited but not headless-tested).
  tomato/cucumber use glyph fallback (art task spawned).
- **F-UI-01:** live MySQL mirror lacks per-field `field_state` until the backend ingest is deployed; the UI
  degrades defensively (`prov_value` derives a display state from confidence_score/source_class at τ=0.40).
  Verify the degrade logic is honest — it must not present missing/low-confidence data as VALIDATED misleadingly.
- **F-CB1-UI-01 (carried → WP-CB-MIG2):** `field_policy.py` old-name drift on 4 fields; the UI is resolver-immune.
- 2 pytest failures are PRE-EXISTING (documented in the WP-CB-1 backend gate history), not UI-induced.

## Verdict format (required)
Write `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_v1.0.0.md` with the §0 box (Gate/WP/Commit/
Branch/Verdict/AC coverage/Constitutional/LOD500) then §1 reviewed artifacts · §2 execution evidence · §3 AC matrix ·
§4 findings (severity+root-cause+impact) · §5 declared-deviations assessment · §6 constitutional checks · §7 verdict.
On **PASS / PASS_WITH_FINDINGS** → team_100 advances LOD500_LOCKED (UI) + archive mandate to team_191; the declared
PARTIAL items become a tracked WP-CB-1 follow-up patch.

## Authority limits (you)
Own: read all, execute tests, issue verdict. Do NOT: commit app code, edit roadmap, deploy. Verdict commit message:
`validate(SFA-S003-P004-WP-CB-1/L-GATE_V): {VERDICT} — Team 190`.

*Issued by team_100 · 2026-05-31 · hand-off to Nimrod for non-Claude execution (IR#1/#5).*
