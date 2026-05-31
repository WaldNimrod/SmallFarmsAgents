---
id: VERDICT_SFA-S003-P004_TARGET_B_BACKEND_BUILD_VERIFICATION_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-05-30
type: validation_verdict
wp: SFA-S003-P004-WP-CB-1
gate: independent_build_verification
target: B (backend build verification)
commits:
  - fd7dfba
  - 1222fe5
validator_engine: Codex / GPT-5 (non-Claude)
result: PASS
checks: 5/5 passed
---

# Target B Verdict — WP-CB-1 Backend Build Verification

```yaml
target: B (backend build verification)
validator_engine: Codex / GPT-5 (non-Claude)
result: PASS
checks: 5/5 passed
findings:
  - id: F-190-CB1-01
    severity: INFO
    summary: "Full crop_book suite still has the two expected pre-existing failures."
    location: "tests/crop_book/test_ni_publisher_isolation.py:30; tests/crop_book/test_source_registry.py:66"
    remediation: "Track separately from WP-CB-1 backend math; do not block this backend verification."
summary: "The backend slice's durable core passes independent verification. Calculator math is correct, AssumptionField defaults and links are present, calculator metadata follows its declared map, field-mapping defects are correctly out of scope/deferred to the canon migration, and fd7dfba does not modify locked reconciler/model/migration files."
```

## Evidence

### Required Commands

```bash
python3 -m pytest tests/crop_book/test_calculators.py tests/crop_book/test_assumptions.py \
  tests/crop_book/test_calculator_meta.py tests/crop_book/test_field_policy.py -q
```

Result: **92 passed in 0.11s**.

```bash
python3 -m pytest tests/crop_book/ -q
```

Result with local DB access permitted: **548 passed / 2 failed / 75 warnings**. The two failures are:

- `tests/crop_book/test_ni_publisher_isolation.py::TestNiPublisherIsolation::test_ac21b_publisher_dir_clean`
- `tests/crop_book/test_source_registry.py::test_uc_prefix_requires_moderation`

These match the mandate's expected pre-existing failures. Blame confirms the NI publisher isolation test predates this slice (`e95dce4`), the `crop_knowledge_notes` publisher reference was introduced by WP-UI-patch04 (`70dc728`), and the UC expectation originates from `11edbd1` while runtime source-registry behavior changed under WP-C5 (`1a29c03`). Neither failure is caused by the calculator backend slice.

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Result: **29 PASS / 19 SKIP / 0 FAIL**.

```bash
git show --stat fd7dfba
```

Confirmed backend slice files:

- added `organic_market_agent/crop_book/assumptions.py`
- added `organic_market_agent/crop_book/calculator_meta.py`
- added `organic_market_agent/crop_book/calculators.py`
- modified `organic_market_agent/crop_book/field_policy.py`
- modified `organic_market_agent/publisher/sfa_ingest_push.py`
- added/updated the four focused test files
- no locked reconciler/model/migration files touched

### Independent Calculator Recompute

I independently exercised one case for each of the 14 calculator functions and verified the expected arithmetic:

| Calc | Function | Result |
|---|---|---:|
| 1 | `seed_quantity_to_buy` | PASS |
| 2 | `transplants_needed` | PASS |
| 3 | `nursery_trays_and_sow_date` | PASS |
| 4 | `sowing_date_from_harvest` | PASS |
| 5 | `harvest_window_from_sowing` | PASS |
| 6 | `succession_schedule` | PASS |
| 7 | `beds_for_target_yield` | PASS |
| 8 | `expected_yield` | PASS |
| 9 | `expected_revenue` | PASS |
| 10 | `plant_population` | PASS |
| 11 | `frost_planting_window` | PASS |
| 12 | `fertilizer_compost_rate` | PASS |
| 13 | `crop_profit_comparison` | PASS |
| 14 | `seed_input_cost` | PASS |

`CalcUnavailable(<field>)` behavior is covered in the focused tests and is present for required book-value nulls. AssumptionFields and user inputs are not treated as missing book data.

### AssumptionField Registry

Verified:

- scalar/default assumptions present: `germination_rate=0.90`, `bed_width=0.80`, `oversow=1.10`, `std_bed_length_m=30.0`, `compost_N_pct=0.015`, `application_efficiency=0.50`, `rotation_gap_seasons=3`
- `germination_rate` and `bed_width` have non-null `nimrod.bio/blog/...` `post_url` values after `1222fe5`
- `get_assumption` returns override when provided and default otherwise
- `TRAY_CELLS` table and `HARDINESS_OFFSET` table are present with helpers

The dispatch phrase "8 keys" is implemented as 7 scalar `ASSUMPTIONS` plus module-level lookup tables for `tray_cells` and `hardiness_offset`; the tests document and verify that interpretation.

### Calculator Metadata

`calculator_meta.calc_enabled` disables iff a required field is `MISSING`; it allows `VALIDATED` and `UNVALIDATED` fields. Synthetic test coverage confirms the rule across all 14 calculators. Field-name correctness against the live canon is explicitly out of scope per mandate and deferred to Target A / migration.

### Constraints

`git diff --name-status fd7dfba^..fd7dfba` shows no changes to:

- `organic_market_agent/crop_book/importer/reconciler.py`
- `organic_market_agent/crop_book/importer/enrichment_runner.py`
- `organic_market_agent/crop_book/enrichment_models.py`
- `organic_market_agent/crop_book/models.py`
- `organic_market_agent/crop_book/constants.py`
- migrations `001` through `057`
- `vendor/`

`field_policy.py` and `sfa_ingest_push.py` changes are additive within the WP-CB-1 slice.

## Final Decision

**PASS.**

The durable backend core is cross-engine confirmed. Full WP-CB-1 L-GATE_V remains deferred until the canon migration and UI work complete, but the committed backend math/registry/metadata slice satisfies the narrow independent verification mandate.
