---
id: DISPOSITION_SFA-S003-P002-WP-B1_FINDING-01_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_10 (sfa_build)
date: 2026-05-25
type: FINDING_DISPOSITION
wp: SFA-S003-P002-WP-B1
gate: L-GATE_B
inquiry_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B1/INQUIRY_AC04_CROP_CHART_MISMATCH_v1.0.0.md
verdict_on_build: BUILD_COMPLETE — PASS_WITH_FINDINGS (accept; proceed to L-GATE_V)
disposition: ACCEPT_BUILD + FOLLOWUP_WP_REQUIRED
---

# Disposition — FINDING-01 (AC-04 CROP CHART Mismatch)

## 1. Finding restated

team_10 (sfa_build) built LOD400 v1.1.3 against the spec verbatim. During
the live-workbook coverage check (AC-04), team_10 discovered that the
on-disk JMF MasterClass workbook is a **farm-specific adaptation** of the
canonical JMF MasterClass template:

- **14 of 50** workbook crop names match `JMF_CROP_MAP` literal in spec §5
- **36 crops** in the workbook are NOT in `JMF_CROP_MAP`
- Many of the 36 are **obvious aliases** of crops that ARE in the map
  (e.g., `Pak Choi` ↔ `Bok Choy`; `Coriander` ↔ `Cilantro`; `Raddish` ↔
  `Radishes`; `Swiss Chard` ↔ `Chard`; `Watermelon` ↔ `Watermelons`)
- Others are **farm-specific variants** (Greenhouse Cherry Tomato, Hakurei
  Turnip, Salanova Lettuce, Sucrine, Baby Mustard) or **storage/season
  qualifiers** of base crops (Storage Onion, Leek Summer / Leek Storage,
  Summer/Fall/Savoy Cabbage)

team_10 correctly followed the spec §11 Step 4 non-improvisation rule:
filed the inquiry rather than guessing at extensions.

## 2. Classification

**FINDING-01 is a DATA-GAP finding, not a SPEC or IMPLEMENTATION defect.**

- The importer behaves correctly per LOD400 §5 maintenance rule: "On
  runtime miss (JMF row whose English label is not a key), the importer
  logs WARN with the unmapped label and skips that row."
- The spec literal `JMF_CROP_MAP` (52 entries) is the **canonical** JMF
  MasterClass naming and remains correct as a baseline contract.
- The gap is between the canonical map and the **specific farm
  adaptation** the user happens to have on disk — not between the spec
  and the implementation.

## 3. Disposition

**ACCEPT BUILD as L-GATE_B BUILD_COMPLETE / PASS_WITH_FINDINGS.**

team_110 authorizes:

1. **No spec patch (v1.1.4) for B1.** Re-opening L-GATE_S to extend the
   map for farm-workbook aliases would be scope creep: the spec is
   contractually correct against the canonical JMF MasterClass, and
   re-validating Round 4 of L-GATE_S would cost more than the value
   delivered.

2. **Proceed to L-GATE_V (Phase 6).** team_190 (non-Claude) validates
   the implementation against the spec. The build matches the spec
   exactly — both Counter assertion of the duplicate-target set AND
   parser behavior on miss are conformant.

3. **Open a follow-up WP** to address the alias + Hebrew-terminology
   gaps in a single coherent patch (see §4 below).

4. **Operational gate — `seed.py --all` against live workbook is
   PAUSED** until the follow-up patch lands. The 14 matching crops
   would import correctly, BUT one of them (Rutabaga → "ברוקקואר", a
   known hallucination per pending Task #10) would write incorrect
   Hebrew into `crops.name_he`. Better to fix the Hebrew + extend the
   map first, then run the production import.

## 4. Follow-up scope (to be filed as separate WP after WP-B1 closure)

Anticipated as **SFA-S003-P002-WP-B1-FOLLOWUP** (small, LARGE-effort-no,
likely MEDIUM):

### 4.1 Alias-extension entries (high-confidence)

Add the following to `JMF_CROP_MAP` (all map to existing
`crops.name_he` values — pure additive expansion):

| Workbook label | Map to (existing key's Hebrew) |
|---|---|
| `Brussel Sprouts` | `כרוב ניצנים` (Brussels Sprouts typo) |
| `Pak Choi` | `פאק צ'וי` (Bok Choy synonym) |
| `Coriander` | `כוסברה` (Cilantro synonym) |
| `Raddish` / `Winter Radish` | `צנונית` (Radishes typo/variant) |
| `Swiss Chard` | `מנגולד` (Chard explicit) |
| `Watermelon` | `אבטיח` (Watermelons singular) |
| `Potato` | `תפוח אדמה` (Potatoes singular) |
| `Fresh Carrots` | `גזר` (Carrots variant) |
| `Storage Onion` | `בצל` (Onions variant) |
| `Green Onion` | `בצל ירוק` (Scallions synonym) |
| `Leek Storage` / `Leek Summer` | `כרישה` (Leeks variants) |
| `Bell Pepper` / `Hot Pepper` | `פלפל` (Peppers variants) |
| `Roma Tomato` / `Greenhouse Cherry Tomato` / `Greenhouse Heirloom Tomato` | `עגבנייה` (Tomatoes variants) |
| `Greenhouse English Cucumber` / `Greenhouse Libanese Cucumber` | `מלפפון` (Cucumbers variants) |
| `Fall Cabbage` / `Savoy Cabbage` / `Summer Cabbage` / `Chinese Cabbage` | `כרוב` (Cabbage variants) |
| `Salanova Lettuce` / `Sucrine` / `Baby kale` | `חסה` / `קייל` (Lettuce / Kale variants) |
| `Cauliflower / Romanesco` | `כרובית` |
| `Hakurei Turnip` | `לפת` (Turnips) |
| `Mini Celery Root` | `סלרי שורש` |
| `Mini Fennel` | `שומר` (Fennel) |
| `Spinach TR` / `Spinarch SD` | `תרד` (Spinach editions/typos) |

That's ~28 alias entries. Coverage after extension: **~42 / 50** (the
remaining 8 — Baby Mustard, Eggplant (Feld) [Eggplant has variant `חציל`
already?], Rapini, etc. — need genuine new species rows).

### 4.2 Hebrew terminology corrections (Task #10)

| Existing key | Current value (hallucinated/suspect) | Correct value |
|---|---|---|
| `Rutabaga` | `ברוקקואר` (hallucinated) | `רוטבגה` (transliteration) or `כרוב לפת שוודי` |
| `Tomatillos` | `תומאטיו` (verify) | `טומטיו` (more standard) |
| `Parsnips` | `גזר לבן` (colloquial) | acceptable; alternative `פרסניפ` if user prefers transliteration |
| `Shallots` | `שאלוט` | acceptable; alternative `בצלצל` |

### 4.3 Operational dependency

This follow-up MUST land **before** the first live `seed.py --all` run
against the production DB, to prevent corrupting `crops.name_he` with
incorrect Hebrew for Rutabaga.

## 5. L-GATE_V mandate authorization

team_110 hereby authorizes Phase 6 to proceed for WP-B1 against the
current HEAD (`6eb312d`). The L-GATE_V mandate will be filed at
`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/MANDATE_L-GATE_V_v1.0.0.md`
immediately following this disposition.

team_10's work on WP-B1 is **CLOSED**. Thank you for the disciplined
inquiry MSG — it prevented a botanically-wrong spec extension that
would have rippled into wrong import data.

## 6. Iron Rules check (this disposition)

- **IR#1:** Disposition author = team_110 (Claude Opus 4.7), distinct
  from team_10 (Claude Sonnet 4.6 sub-agent) and team_190 (GPT-5.5).
- **IR#4:** No roadmap mutation in this disposition; lifecycle stays
  `BUILDING / LOD400_LOCKED / L-GATE_B` until L-GATE_V verdict.
- **IR#6:** Disposition routed via `_COMMUNICATION/TEAM_10/<WP>/`.
- **IR#11:** No governance / lean-kit edits.

---

*Disposition issued 2026-05-25 by team_110 (Claude Opus 4.7) under
EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045 R2 #2).*
*Closes INQUIRY_AC04_CROP_CHART_MISMATCH_v1.0.0.md (status: RESOLVED).*
