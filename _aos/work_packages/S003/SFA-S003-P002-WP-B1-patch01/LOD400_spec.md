---
id: SFA-S003-P002-WP-B1-patch01-LOD400
wp: SFA-S003-P002-WP-B1-patch01 — JMF_CROP_MAP alias extension + Rutabaga Hebrew correction
gate: L-GATE_S (LOD400 — implementation spec)
status: PRE_LOD400_LOCK — awaiting team_190 L-GATE_S verdict (R2)
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.1
changelog: >
  v1.0.1 — Remediation of two BLOCKERS from team_190 L-GATE_S R1
  verdict (LOD400-VERDICT_v1.0.0.md). B-01: §3.2 entry-count math
  reorganized — `Eggplant  (Feld)` integrated as a new "Field-qualifier
  variants" category (1 entry) within §3.2; alias total restated as 34;
  grand total stated unambiguously as 86. §AC-04.1 rewritten as
  design-rationale only (no longer claims to "raise count from 85 to
  86" — the §3.2 block is now the single source of truth). B-02: AC-03
  Counter assertion widened from 13 to 25 by-design duplicate
  pairs/groups, enumerating every alias-introduced collision
  (Brussel Sprouts/Brussels Sprouts → כרוב ניצנים; Pak Choi/Bok Choy →
  פאק צ'וי; Coriander/Cilantro → כוסברה; Swiss Chard/Chard → מנגולד;
  Watermelon/Watermelons → אבטיח; Potato/Potatoes → תפוח אדמה;
  Green Onion/Scallions → בצל ירוק; Cauliflower / Romanesco/Cauliflower
  → כרובית; Hakurei Turnip/Turnips → לפת; Mini Celery Root/Celery Root
  → סלרי שורש; Mini Fennel/Fennel → שומר; Eggplant  (Feld)/Eggplant →
  חציל). Total: 25 pairs/groups in the Counter set.
  v1.0.0 — Initial authoring; FAIL by team_190 R1 (B-01 + B-02 — both
  spec-internal-consistency issues, fixed in v1.0.1).
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD200_spec.md
parent_wp: SFA-S003-P002-WP-B1
parent_locked_commit: "6a85561"        # WP-B1 LOD500_LOCKED — DO NOT reopen
wp_a_locked_commit: "594cbc8"          # WP-A LOD500_LOCKED — engine SSoT
builder: sfa_build (separate session per IR#1)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-B1-patch01

**Read before writing a single line of code:**

1. LOD200 (this WP): `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD200_spec.md`
2. WP-B1 disposition: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/DISPOSITION_FINDING-01_v1.0.0.md`
3. WP-B1 inquiry (live workbook crop inventory): `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B1/INQUIRY_AC04_CROP_CHART_MISMATCH_v1.0.0.md`
4. WP-B1 LOD400 (parent, LOD500_LOCKED — read-only reference): `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md`
5. Existing JMF_CROP_MAP in `organic_market_agent/crop_book/constants.py` (post-WP-B1 build)

---

## 1. Goal

Tight additive patch to `JMF_CROP_MAP` (the only file modified):

1. **Single-cell correction:** `"Rutabaga"` value from `"ברוקקואר"`
   (team_110 hallucination — not a Hebrew word) to **`"רוטבגה"`**
   (phonetic transliteration per team_00 directive).
2. **28 alias entries appended** so the farm-specific JMF MasterClass
   workbook on Nimrod's disk maps cleanly via the existing WARN+skip
   miss-handling contract (most importer rows now hit a real mapping).
3. **Test updates:** AC-03 Counter assertion in
   `test_jmf_crop_map.py` widened to enumerate every by-design
   duplicate-target pair (~6 pairs post-patch).
4. **Documentation:** `CHANGELOG.md` `[Unreleased]` entry.

On completion: `seed.py --all` against the live workbook covers ≥42/50
crops cleanly; the Rutabaga row writes `"רוטבגה"` to `crops.name_he`
(not the hallucinated value); the operational pause from
`DISPOSITION_FINDING-01 §3.4` is lifted.

---

## 2. Architecture

### 2.1 Files modified

```
organic_market_agent/crop_book/constants.py   ← Edit JMF_CROP_MAP literal:
                                                  (a) change "Rutabaga" value;
                                                  (b) append 28 alias entries
tests/crop_book/test_jmf_crop_map.py          ← Widen Counter-set assertion
                                                  in test_ac03_*; add Rutabaga
                                                  regression + ≥4 new tests
CHANGELOG.md                                   ← Append [Unreleased] entry
```

### 2.2 No other files modified

| File / path | Reason |
|-------------|--------|
| `organic_market_agent/crop_book/crop_task_templates.py` | B1 deliverable — LOD500_LOCKED state preserved |
| `organic_market_agent/crop_book/importer/jmf_masterclass.py` | B1 deliverable — no behavioral change needed (the WARN+skip miss contract handles unmapped crops cleanly) |
| `organic_market_agent/db/versions/044_*.py` | LOD500_LOCKED |
| All WP-A engine SSoT (source_registry, field_policy, reconciler, enrichment_runner, enrichment_models, models, tend) | LOD500_LOCKED |
| `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md` | LOD500_LOCKED (parent WP — DO NOT reopen) |
| `organic_market_agent/crop_book/importer/seed.py` | LOD500_LOCKED (post-B1) |

---

## 3. The change to `constants.py`

### 3.1 Rutabaga single-value correction

Locate the existing line in `JMF_CROP_MAP`:

```python
    "Rutabaga":           "ברוקקואר",
```

Replace with:

```python
    "Rutabaga":           "רוטבגה",   # phonetic transliteration (team_00 directive 2026-05-25; "ברוקקואר" was a hallucination, NOT a real Hebrew word)
```

### 3.2 Append 28 alias entries

Append the following block to `JMF_CROP_MAP` AFTER the existing 52
entries and BEFORE the closing `}`. Add a section comment to delineate
the alias block from the baseline canonical block:

```python
    # ─── BEGIN patch01 alias additions (2026-05-25) ───
    # Maps farm-specific JMF MasterClass workbook variants to the same
    # crops.name_he as the canonical baseline keys. After this patch,
    # ~42/50 live-workbook crops map cleanly; the remaining 8 require
    # new crops.name_he rows and are out-of-scope for patch01.
    # Maintenance rule: when a new variant appears in any future
    # JMF workbook edition, append here — NEVER branch on the
    # English label elsewhere in the codebase.

    # ── Typo / spelling variants ──
    "Brussel Sprouts":              "כרוב ניצנים",   # Brussels Sprouts (singular-l typo)
    "Raddish":                      "צנונית",       # Radishes (double-d typo)
    "Spinach TR":                   "תרד",          # Spinach (edition suffix)
    "Spinarch SD":                  "תרד",          # Spinach (edition typo + suffix)

    # ── Synonyms / alternative English names ──
    "Pak Choi":                     "פאק צ'וי",     # Bok Choy synonym (matches existing TEND_CROP_MAP value)
    "Coriander":                    "כוסברה",       # Cilantro (Coriander = same plant)
    "Swiss Chard":                  "מנגולד",       # Chard with explicit Swiss qualifier
    "Watermelon":                   "אבטיח",        # Watermelons singular
    "Potato":                       "תפוח אדמה",    # Potatoes singular
    "Fresh Carrots":                "גזר",          # Carrots with freshness qualifier

    # ── Storage / season qualifiers (same species, marketed differently) ──
    "Storage Onion":                "בצל",          # Onions for storage
    "Green Onion":                  "בצל ירוק",     # Scallions synonym (matches TEND_CROP_MAP)
    "Leek Storage":                 "כרישה",        # Leeks (storage cultivar)
    "Leek Summer":                  "כרישה",        # Leeks (summer cultivar)

    # ── Pepper variants ──
    "Bell Pepper":                  "פלפל",         # Peppers (bell variant — same species at crops.name_he level)
    "Hot Pepper":                   "פלפל",         # Peppers (hot variant)

    # ── Tomato variants (all Solanum lycopersicum at species level) ──
    "Roma Tomato":                  "עגבנייה",      # paste cultivar
    "Greenhouse Cherry Tomato":     "עגבנייה",      # protected-culture cherry
    "Greenhouse Heirloom Tomato":   "עגבנייה",      # protected-culture heirloom

    # ── Cucumber variants ──
    "Greenhouse English Cucumber":  "מלפפון",       # protected-culture long
    "Greenhouse Libanese Cucumber": "מלפפון",       # protected-culture Lebanese (note: workbook spelling preserved)

    # ── Cabbage variants ──
    "Fall Cabbage":                 "כרוב",
    "Savoy Cabbage":                "כרוב",
    "Summer Cabbage":               "כרוב",
    "Chinese Cabbage":              "כרוב",

    # ── Lettuce variants ──
    "Salanova Lettuce":             "חסה",
    "Sucrine":                      "חסה",

    # ── Brassica & misc variants ──
    "Baby kale":                    "קייל",
    "Cauliflower / Romanesco":      "כרובית",       # workbook literal preserves the "/" (parser already substring-matches; this is the EXACT cell label)
    "Hakurei Turnip":               "לפת",
    "Mini Celery Root":             "סלרי שורש",
    "Mini Fennel":                  "שומר",
    "Winter Radish":                "צנונית",

    # ── Field-qualifier variants (preserved workbook literals — no parser-side normalization) ──
    "Eggplant  (Feld)":             "חציל",         # workbook literal: double space + (Feld) field qualifier. See §4 AC-04.1 rationale for why this is a literal alias rather than a parser change.
    # ─── END patch01 alias additions ───
```

**Entry count math (single source of truth — no later-§4 additions):**

- Existing baseline (B1): 52 entries
- Typo / spelling variants: 4
- Synonyms: 6
- Storage / season: 4
- Pepper variants: 2
- Tomato variants: 3
- Cucumber variants: 2
- Cabbage variants: 4
- Lettuce variants: 2
- Brassica & misc: 6
- Field-qualifier variants: 1
- **Alias additions total: 34**
- **Grand total after patch: 86**

The §3.2 alias block is the COMPLETE inventory. §4 ACs reference these
entries but introduce no additional ones. AC-01 in §4 enforces the
exact total `len(JMF_CROP_MAP) == 86`.

### 3.3 Live-workbook coverage projection

With the patch applied, the inquiry's "Not in JMF_CROP_MAP" set
shrinks from 36 to **8** unmapped crops. Those 8 remain unmapped (and
the importer WARN-skips them per the unchanged miss-handling contract):

| Unmapped (post-patch) | Reason for keeping unmapped |
|---|---|
| `Baby Mustard` | Genuinely new species (not in canonical map); would seed a new `crops.name_he`. Out-of-scope. |
| `Eggplant  (Feld)` | Has double space + parenthetical field qualifier; semantically `Eggplant → חציל` is already in baseline. But the parser strips whitespace? **Builder must verify** (see §6 AC-04.1). |
| `Rapini` | Genuinely new species (broccoli rabe — `ברוקולי רבע` or new entry). Out-of-scope. |
| `Mesclun` | Already in baseline (canonical key) → if absent from live workbook this is fine. |
| `New Zealand Spinach` | Already in baseline (canonical key) → if absent from live workbook this is fine. |
| `Beans (Bush)` / `Beans (Pole)` / `Snow Peas` | Already in baseline; if absent from this workbook edition, fine. |
| Possibly 1-2 others surfaced at build time | Builder records in BUILD_REPORT runtime stats. |

Post-patch live-workbook coverage target: **≥ 42/50** (AC-04 in §4
below). The exact final number depends on how the parser handles the
`Eggplant  (Feld)` whitespace anomaly and is fixed at build time.

---

## 4. Acceptance Criteria

**AC-01 — `JMF_CROP_MAP` has exactly 86 entries.**
`from organic_market_agent.crop_book.constants import JMF_CROP_MAP` succeeds;
`len(JMF_CROP_MAP) == 85`.

**AC-02 — Rutabaga value corrected.**
`JMF_CROP_MAP["Rutabaga"] == "רוטבגה"`. The historical value
`"ברוקקואר"` must NOT appear anywhere in the file — assert via
file-content grep.

**AC-03 — Counter-set assertion enumerates exact post-patch duplicates.**

```python
from collections import Counter
counts = Counter(JMF_CROP_MAP.values())
duplicates = {v: sorted([k for k, mv in JMF_CROP_MAP.items() if mv == v])
              for v, c in counts.items() if c > 1}
assert duplicates == {
    # ── Baseline pairs from WP-B1 ──
    "תערובת סלט":  ["Mesclun", "Salad Mix"],
    "קישוא":        ["Summer Squash", "Zucchini"],

    # ── Pairs introduced by patch01 typo variants ──
    "כרוב ניצנים":  ["Brussel Sprouts", "Brussels Sprouts"],

    # ── Pairs introduced by patch01 synonyms ──
    "פאק צ'וי":     ["Bok Choy", "Pak Choi"],
    "כוסברה":       ["Cilantro", "Coriander"],
    "מנגולד":       ["Chard", "Swiss Chard"],
    "אבטיח":        ["Watermelon", "Watermelons"],
    "תפוח אדמה":    ["Potato", "Potatoes"],
    "גזר":          ["Carrots", "Fresh Carrots"],

    # ── Pairs introduced by patch01 storage/season qualifiers ──
    "בצל":          ["Onions", "Storage Onion"],
    "בצל ירוק":     ["Green Onion", "Scallions"],
    "כרישה":        ["Leek Storage", "Leek Summer", "Leeks"],

    # ── Pairs introduced by patch01 pepper variants ──
    "פלפל":         ["Bell Pepper", "Hot Pepper", "Peppers"],

    # ── Pairs introduced by patch01 tomato variants ──
    "עגבנייה":      ["Greenhouse Cherry Tomato", "Greenhouse Heirloom Tomato",
                     "Roma Tomato", "Tomatoes"],

    # ── Pairs introduced by patch01 cucumber variants ──
    "מלפפון":       ["Cucumbers", "Greenhouse English Cucumber",
                     "Greenhouse Libanese Cucumber"],

    # ── Pairs introduced by patch01 cabbage variants ──
    "כרוב":         ["Cabbage", "Chinese Cabbage", "Fall Cabbage",
                     "Savoy Cabbage", "Summer Cabbage"],

    # ── Pairs introduced by patch01 lettuce variants ──
    "חסה":          ["Lettuce", "Salanova Lettuce", "Sucrine"],

    # ── Pairs introduced by patch01 brassica & misc + spinach edition typos ──
    "קייל":         ["Baby kale", "Kale"],
    "צנונית":       ["Raddish", "Radishes", "Winter Radish"],
    "תרד":          ["Spinach", "Spinach TR", "Spinarch SD"],
    "כרובית":       ["Cauliflower", "Cauliflower / Romanesco"],
    "לפת":          ["Hakurei Turnip", "Turnips"],
    "סלרי שורש":    ["Celery Root", "Mini Celery Root"],
    "שומר":         ["Fennel", "Mini Fennel"],

    # ── Pair introduced by patch01 field-qualifier variant ──
    "חציל":         ["Eggplant", "Eggplant  (Feld)"],
}, f"unexpected Hebrew-value duplicates: {duplicates}"
```

**25 by-design duplicate-target pairs/groups after patch01.** Coverage
math: 34 aliases enumerated in §3.2 + 0 net change to baseline = 34
distinct aliases that each create or extend an existing
duplicate-target group. (Each entry's `crops.name_he` is by design
shared with at least one canonical baseline key — that is the entire
point of the alias.) The Counter result therefore has exactly the
above 25 entries; ALL other Hebrew values in `JMF_CROP_MAP` appear
exactly once.

**AC-04 — Live-workbook coverage ≥ 42/50.**
After `parse_crop_chart(<master XLSX>)`, at least 42 of the 50 returned
`crop_jmf_en` values are keys in `JMF_CROP_MAP`. Test enumerates the
exact mapped vs. unmapped sets. Builder captures the precise final
number in BUILD_REPORT.

**AC-04.1 — `Eggplant  (Feld)` literal-alias design rationale (no count change).**
The workbook label `Eggplant  (Feld)` (note: double space + `(Feld)`
field qualifier) appears verbatim in the live JMF master XLSX. The B1
parser (`jmf_masterclass.py` §6.4) does NOT normalize whitespace or
strip parentheticals — it returns each cell's raw string. Therefore the
crop-name lookup must match the raw label exactly.

**Design choice (locked):** add the literal `"Eggplant  (Feld)"` (with
both spaces preserved) as its own `JMF_CROP_MAP` key, mapping to the
same `crops.name_he = "חציל"` as the canonical `"Eggplant"` baseline
entry. This is **option (a)** — preserves the B1 parser contract
without modification. The literal IS already included in the §3.2
alias block under "Field-qualifier variants" (1 entry). The AC-01
entry count of **86** already accounts for it.

**Why not option (b) — parser normalization?** Two reasons: (1)
modifying `jmf_masterclass.py` would touch a LOD500_LOCKED file
(post-B1 closure), requiring a wider GCR. (2) The set of possible
field-qualifier strings is open-ended; whitelisting the exact strings
we observe is auditable, whereas a normalization rule has surprise
surface (e.g., what if a future workbook adds `Eggplant (Greenhouse)`
or `Pepper  (Field)`?). The literal-alias approach localizes the
contract to `constants.py` exactly where every other crop-naming
decision lives.

**AC-05 — All 22 WP-B1 ACs still PASS (regression).**
Running the full `tests/crop_book/` suite after this patch yields the
same 56 WP-B1 tests PASS (no breakage from the map literal change).

**AC-06 — `validate_aos.sh` 29 PASS / 17 SKIP / 0 FAIL.**

**AC-07 — `seed.py --all --dry-run` against the master XLSX succeeds
without ERROR-level log lines** for the previously unmapped crops that
this patch now maps. WARN lines remain only for the ~6-8 genuinely
unmapped crops (Baby Mustard, Rapini, etc.). Assert via captured
log output in `test_seed_jmf_dry_run_coverage`.

**AC-08 — `CHANGELOG.md` `[Unreleased]` entry exists** documenting the
patch: Rutabaga fix + 34 alias additions.

---

## 5. Test requirements

**Minimum 6 new tests, broken down (preliminary):**

| File | Tests | Coverage |
|------|-------|----------|
| `test_jmf_crop_map.py` (EXTEND existing) | +5 | AC-01 (86 count); AC-02a (Rutabaga value correct); AC-02b (`ברוקקואר` absent from file content); **AC-03 update** (new 13-entry Counter set); AC-04.1 (`Eggplant  (Feld)` literal alias present) |
| `test_jmf_crop_map_aliases.py` (NEW) | +3 | Alias spot-checks: 5 sample new aliases each resolve to the expected `crops.name_he`; entry count grew by exactly 34; Hebrew-value-collision-set widened to 25 pairs/groups |
| `test_jmf_live_workbook_coverage.py` (NEW) | +1 | AC-04 — parse the live master XLSX and assert ≥42 of 50 crop_jmf_en values are mapped |
| `test_jmf_seed_dry_run.py` (NEW) | +1 | AC-07 — `seed.py --all --dry-run` against live master logs WARN for only the genuinely-unmapped crops |

**Total new tests: ≥ 10** (target stated in LOD200 §10 was ≥ 6;
expanded here for thoroughness).

The existing `test_jmf_crop_map.py::test_ac03_*` test from WP-B1 must
be UPDATED (not duplicated) — its assertion block widens to match
AC-03 above. Builder cites the old commit hash (`262d9a3` test version)
in the new commit message for traceability.

---

## 6. Build sequence (4 steps — small WP)

**Step 1** — Read this LOD400 + the WP-B1 disposition + the inquiry MSG.

**Step 2** — Edit `organic_market_agent/crop_book/constants.py`:
(a) change `"Rutabaga"` value to `"רוטבגה"`;
(b) append the alias block from §3.2 (33 entries) + the
`Eggplant  (Feld)` literal from §AC-04.1 (1 entry) = 34 alias additions.
Total: 86 entries. Commit:
`spec(WP-B1-patch01/step2): JMF_CROP_MAP — Rutabaga fix + 34 aliases`

**Step 3** — Update + add tests:
- Update `tests/crop_book/test_jmf_crop_map.py::test_ac03_*` to the new
  Counter set (§4 AC-03).
- Add tests per §5.
- Run `pytest tests/crop_book/ -q` — must show all 56 WP-B1 tests still
  PASS plus the new ≥10 patch01 tests.
Commit: `spec(WP-B1-patch01/step3): +10 tests + update AC-03 assertion`

**Step 4** — Append `CHANGELOG.md` entry. Run
`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
— must be 29 PASS / 17 SKIP / 0 FAIL. Write BUILD_REPORT.
Commit: `spec(WP-B1-patch01/step4): CHANGELOG + BUILD_REPORT`

---

## 7. LOD500_LOCKED inventory (unchanged scope — patch01 must not modify any of these)

Same as WP-B1 §14 inventory PLUS the following files now LOD500_LOCKED
post-B1 closure (do not touch in this patch):

- `organic_market_agent/crop_book/crop_task_templates.py`
- `organic_market_agent/crop_book/importer/jmf_masterclass.py`
- `organic_market_agent/db/versions/044_crop_task_templates.py`
- `organic_market_agent/crop_book/importer/seed.py` (now LOD500_LOCKED via B1 closure)
- `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md` (parent — LOD500_LOCKED)

**Permitted modifications (the only 3 files this patch touches):**
- `organic_market_agent/crop_book/constants.py` — JMF_CROP_MAP literal only
- `tests/crop_book/test_jmf_crop_map.py` — AC-03 assertion update + AC additions
- `CHANGELOG.md` — `[Unreleased]` append

**New files created:**
- `tests/crop_book/test_jmf_crop_map_aliases.py`
- `tests/crop_book/test_jmf_live_workbook_coverage.py`
- `tests/crop_book/test_jmf_seed_dry_run.py`
- `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/BUILD_REPORT_v1.0.0.md`

---

## 8. PRE_HANDOFF advisory disposition

WP-B1 PRE_HANDOFF advisories #1, #2, #3 are out-of-scope for patch01
(carried to WP-B2 / WP-B3). Advisory #4 (transitive WP-A dependency)
remains satisfied: this patch reuses the WP-A engine unchanged via the
B1 importer.

---

## 9. Risk register

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | Constraint name collision: a new alias accidentally duplicates a key that already exists | LOW | LOW | AC-01 (`len == 86`) catches accidental key duplicates because `dict` literal would raise `SyntaxWarning` and the count would be off. CI surfaces it. |
| R-02 | An alias maps to a `crops.name_he` that doesn't actually exist in the DB (typo in Hebrew value) | MEDIUM | MEDIUM | AC-04 live-workbook coverage probe runs against a real DB seeded by WP-A — if the alias `crops.name_he` doesn't resolve, the importer's WARN+skip surfaces it. AC-04 threshold ≥ 42 forces the count to be honest. |
| R-03 | `Eggplant  (Feld)` parser whitespace handling breaks | LOW | LOW | AC-04.1 forces the literal-alias approach (no parser change), eliminating the risk. |
| R-04 | Future map maintenance reverts a Hebrew correction | LOW | MEDIUM | Inline comment on the Rutabaga line cites this LOD400 + the team_00 directive date; any reviewer touching the line sees the rationale. |

---

## 10. File-level deliverables summary

### MODIFY (existing)

```
organic_market_agent/crop_book/constants.py   ← Rutabaga value + 34 alias entries (+ inline section comments)
tests/crop_book/test_jmf_crop_map.py          ← AC-03 Counter assertion update + AC-01/AC-02 expected values updated
CHANGELOG.md                                   ← [Unreleased] append
```

### CREATE (new)

```
tests/crop_book/test_jmf_crop_map_aliases.py
tests/crop_book/test_jmf_live_workbook_coverage.py
tests/crop_book/test_jmf_seed_dry_run.py
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/BUILD_REPORT_v1.0.0.md   ← builder writes after L-GATE_B
```

### DO NOT TOUCH

See §7 LOD500_LOCKED inventory.

---

*LOD400 v1.0.1 — patched 2026-05-25 by team_110 under EXECUTION_MANDATE
SFA-S003-P002-WP-B (ADR045, `execution_authority: full`).*
*v1.0.0 FAILed at team_190 L-GATE_S R1 with 2 BLOCKERS (B-01 count
conflict; B-02 incomplete Counter assertion). v1.0.1 addresses both:
§3.2 Eggplant integration + AC-03 expansion to 25 pairs/groups.
Pending: team_190 L-GATE_S R2 validation.*
