---
id: DESIGN_REQUEST_team35_WP-CB-UI-FIDELITY_v1.0.0
from: team_10 (Builder, Claude Sonnet)
to: team_35 (UX/Design)
cc: team_100, team_00
date: 2026-06-04
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
status: OPEN — blocking items Q2/Q3/Q4/Q5 only (structural fixes proceeded per LOD §4)
---

# DESIGN_REQUEST — WP-CB-UI-FIDELITY: Open design decisions

team_10 (Build) is executing the WP-CB-UI-FIDELITY build mandate.
The following 4 questions (per LOD §4) require team_35 design authority.
They each block ONLY their own items; all structural/code fixes proceeded independently.

---

## Q2 — Hebrew wording for market category chips: `legumes_fresh`, `eggs`, `baskets`

**Context:** The market `/market/` filter chips show product category keys in Hebrew.
Three keys were missing from FieldRegistry::ENUM_LABELS['category']:
- `legumes_fresh`
- `eggs`
- `baskets`

**Defaults shipped** (pending team_35 confirm):
- `legumes_fresh` → **קטניות טריות**
- `eggs` → **ביצים**
- `baskets` → **סלים**

**Action required:** Confirm or replace these Hebrew labels.
If `baskets` refers to vegetable assortment baskets, "סלים" may need to be "סלסלות" or "ערכות".

---

## Q3 — Yield/removal area unit: `kg_per_ha` → `ק״ג/דונם` or `ק״ג/הקטר`?

**Context:** The canonical unit token `kg_per_ha` appears in:
- `nutrient_removal_n_kg_per_ha` (and P/K variants)
- `yield_per_ha` (if used)

The audience is Israeli small farms; the working area unit is the **dunam** (1 dunam = 0.1 hectare).
However, the stored numeric values were enriched from JMF/international sources that use **hectare**.

**Current implementation:** `kg_per_ha` → `ק״ג/הקטר` (safe default — avoids silent 10× error
if values are hectare-based). Changing to `ק״ג/דונם` would require CONFIRMING that stored values
are already per-dunam (a data verification task, not just a label change).

**Action required:**
1. Confirm whether `nutrient_removal_n_kg_per_ha` stored values are **per hectare** (international
   standard) or **per dunam** (Israeli adapted).
2. If per-hectare: keep `ק״ג/הקטר` and create a separate display conversion (÷10 → dunam) — or
   accept hectare as the display unit for agronomic data.
3. If per-dunam: approve changing the map to `ק״ג/דונם`.

**Decision required** before the unit label goes live with a value.

---

## Q4 — `beginner` / `small-space` leading-questions: backing data required

**Context:** The "שאלות מובילות" (leading questions) had 5 links:
- `מה מתאים לקיץ?` / `מה זורעים לחורף?` — required a `season` filter (D-4a: BLOCKED, see Q4b)
- `מה גדל מהר?` — now correctly routed to `?dtm_max=60` (fixed in this WP)
- `מה מתאים למתחילים?` → no backing data attribute in the DB mirror
- `מה מתאים לשטח קטן?` → no backing data attribute in the DB mirror

**For launch:** `beginner` and `small-space` questions were **removed** to avoid dead 0-result links.
They will reappear once a backing attribute is defined and populated.

**Action required:**
1. Define what attribute backs "beginner" (difficulty rating? specific crop list?)
   and "small-space" (container-suitable? max spacing < threshold?).
2. Identify/create the backing data field in the crop data model.
3. When data exists, team_10 can wire the filter in a follow-up WP.

**Bonus Q4b — Season leading-questions:**
`מה מתאים לקיץ?` / `מה זורעים לחורף?` were also removed because `crops.season` in the delivery
MySQL mirror stores **growth-cycle** tokens (`annual`/`year-round`/`biennial`), NOT planting-season
tokens (summer/winter/spring/fall). The planting-season lives in `crop_attribute` in Postgres
(key: `planting_season`) but is NOT mirrored as a filterable column.

**Data WP required:** Add a `season_class` column to the crops mirror table populated from
`payload_json` → calendar data or the `planting_season` attribute. Then the season filter
and summer/winter leading questions can be wired correctly.

---

## Q5 — English eyebrow label Hebraization (M-2, non-blocking)

**Context:** Hub tiles and audience cards carry English sub-labels: CALC, MARKET, CROP-BOOK,
FARMER, GARDENER, FIELD-LOG, planner. Board-B shows these as intentional bilingual mono eyebrows.
team_00 reads some as "English menus."

**team_100 ruling:** Hebraize/soften eyebrows that read as nav/menu items; keep
purely-decorative mono eyebrows only where Board-B clearly intends them.

**Action required from team_35:**
1. Review the hub tiles / audience cards in Board-B.
2. Specify which eyebrows should be Hebraized and their Hebrew equivalents.
3. Specify which should remain as-is (decorative, not menu-like).

Proposed changes (for team_35 review):
- `CALC` → `מחשבון` (or keep as decorative mono)
- `MARKET` → `מחירון`
- `CROP-BOOK` → `ספר גידולים`
- `FARMER` → `חקלאי`
- `GARDENER` → `גנן`
- `FIELD-LOG` → `יומן שדה`

---

## Non-blocking note: Category chips are live with defaults

The 3 new category entries (`legumes_fresh`, `eggs`, `baskets`) are **already live** with the
proposed Hebrew defaults. If team_35 supplies different wording before deploy, team_10 can
update `FieldRegistry::ENUM_LABELS['category']` in a follow-up edit.

---
*Filed by team_10 · 2026-06-04 · Per WI-7 mandate (LOD §3)*
