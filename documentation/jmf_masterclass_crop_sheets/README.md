# JMF MasterClass — Per-Crop Reference Sheets

**Source:** Jean-Martin Fortier MasterClass workbook PDFs (Hebrew-named local copies on team_00's MacBook Air).
**Extraction method:** NotebookLM → pdf2md.
**Date received:** 2026-05-25.
**Total deliverable:** 37 substantive crop-sheet MD files + 193 images. ~3.0 MB.

> The first 37 entries (001-037) in the original archive were `__MACOSX/._*` metadata shadows — discarded. Files 038-074 are the actual extractions.

## What's in here

Each MD file is a single-crop MasterClass reference sheet containing:
- **Cultivars** (specific varieties grown — e.g., Tomatoes: Marnero, Marbonne, Margold, Beorange, Aurea, Bigdena, Trust, Maxifort)
- **Intensive spacing** (row layout, distance on row, distance between rows)
- **Sowing / transplanting dates** (calendar week ranges)
- **Yield expectations** (per bed or per row)
- **Common pests** + **diseases**
- **Harvest + storage** notes

Per-PDF page images are preserved in `images/<file-basename>/`.

## Coverage map (37 sheets → JMF_CROP_MAP)

See `_index.json` for the machine-readable cross-reference. Summary:

### Direct matches (20 sheets) — current `JMF_CROP_MAP`

| Hebrew | English keys (current) | Pages | MD file |
|--------|-----------------------|-------|---------|
| כרוב | Cabbage + 4 cultivar aliases | 3 | 039-document-039.md |
| כרישה | Leeks + 2 season variants | 3 | 040-document-040.md |
| צנונית | Radishes + 2 variants | 3 | 042-aaoao.md |
| תרד | Spinach + 2 edition variants | 4 | 043-document-043.md |
| קייל | Kale + Baby kale | 3 | 044-ooo.md |
| קישוא | Summer Squash + Zucchini | 3 | 045-oooe.md |
| בצל | Onions + Storage Onion | **8** | 047-document-047.md |
| בצל ירוק | Scallions + Green Onion | 3 | 048-a-ooo.md |
| ברוקולי | Broccoli | 4 | 049-oooo.md |
| בזיל | Basil | 4 | 054-document-054.md |
| אפונה | Peas | 4 | 055-enoao.md |
| סלק | Beets | 4 | 057-document-057.md |
| פלפל | Peppers + Bell + Hot | 4 | 058-document-058.md |
| חציל | Eggplant + (Feld) | 4 | 064-uao.md |
| חסה | Lettuce + Salanova + Sucrine | 3 | 065-uio.md |
| מלון | Melons | 4 | 068-document-068.md |
| מנגולד | Chard + Swiss Chard | 3 | 069-aoo.md |
| שום | Garlic | 4 | 071-document-071.md |
| שעועית | Beans (Bush) | 3 | 073-oooo.md |
| שעועית מטפסת | Beans (Pole) | **9** | 074-oooo-yni.md |

### Confirms patch03 architectural decision (1 sheet)

| Hebrew | Maps post-patch03 to | Pages | MD file |
|--------|---------------------|-------|---------|
| **מלפפון חממה** | Greenhouse Libanese Cucumber | **17** | 067-nno-uo.md |

→ Validates patch03 §1.3: the user maintains a SEPARATE MasterClass sheet for "מלפפון חממה" (greenhouse cucumber), distinct from generic "מלפפון" (open-field). This is direct field evidence that the patch03 split is the right call.

### NEW crops / variants not in JMF_CROP_MAP (16 sheets)

| Hebrew | Type | Pages | MD file | Disposition |
|--------|------|-------|---------|-------------|
| בייבי מיקס - חסה | variant of עלי בייבי (post-patch03) | 4 | 051-... | **Confirms patch03 עלי בייבי baseline.** Variety detail for crop_varieties. |
| מיזונה וחרדל | variant of עלי בייבי (post-patch03) | 4 | 070-... | Another עלי בייבי variant. Suggests Mizuna/Mustard rows should be added to JMF_CROP_MAP → "עלי בייבי" in a follow-up. |
| שומר בייבי | variant of שומר (matches `Mini Fennel`) | 3 | 072-... | Already captured: `Mini Fennel → שומר`. ✅ |
| חסה ראש קטן | variant of חסה (matches `Sucrine`?) | 3 | 066-... | Likely already captured. |
| גזר טרי | matches `Fresh Carrots → גזר` | 4 | 053-... | ✅ Already captured. |
| גזר איחסון | NEW — storage carrot variant | 3 | 052-... | Suggests `Storage Carrots → גזר איחסון` (new key + value). Out-of-scope for patch03; patch04 candidate. |
| פלפל חממה | NEW — greenhouse pepper | **13** | 059-... | Suggests `Greenhouse Pepper → פלפל חממה` (new key + new baseline name_he). Architecturally same shape as the Cucumber split in patch03. |
| עגבניות חממה | NEW — greenhouse tomato sheet | **22** | 062-... | Suggests this is the umbrella for `Greenhouse Cherry/Heirloom Tomato` (already patch03-split). Sheet covers Beefsteak (Marnero/Marbonne/etc.) — implies a `Greenhouse Beefsteak Tomato → עגבניות חממה` baseline. |
| עגבניות שטח פתוח | NEW — field tomato | 5 | 063-... | The "regular" `Tomatoes → עגבנייה` content. |
| עגבניות - הרכבה | NEW — tomato grafting | 5 | 061-... | Operational technique doc; not a crop. crop_knowledge_notes companion record? |
| רוקט | likely Arugula synonym | 4 | 046-... | Currently `Arugula → ארוגולה`. Sheet uses colloquial "רוקט" — alias candidate (`Rocket → ארוגולה`). |
| לפט | likely Turnips typo of לפת | 3 | 041-... | Diacritical drift; same crop as `Turnips → לפת`. Likely no action. |
| פריזה | NEW — Frisée endive | 3 | 060-... | Cultivar of Endive (`Endive → אנדיב`). Add `Frisée → אנדיב` alias? |
| גינגר | NEW — Baby ginger | 6 | 050-... | Entirely new crop. Title says "FT_editable_Bébé-gingembre_eng". Patch04 candidate. |
| FT_FINALE_PIMENTFORT_ENG | DUPLICATE of פלפל חריף content | 6 | 038-... | Already captured by patch03 `Hot Pepper → פלפל חריף`. |
| איחסון ושטיפהֿ | Operational doc (storage + washing itinerary) | 3 | 056-... | Not a crop. General reference for `crop_knowledge_notes` of type `harvest_handling`. |

---

## What this unlocks

### 1. WP-B2 NIImporter cache can be populated NOW (no further LLM calls)

The 37 MD files are pre-extracted, structured English content per crop. They can be directly loaded into `data/jmf/extracted/jmf_book/<crop>.json` via a small converter script — bypassing the NotebookLM/LLM call entirely. Cost: $0.

**Converter shape** (writes to `data/jmf/extracted/jmf_book/<crop_jmf_en>.json` per the WP-B2 schema):

```python
# pseudo-code:
for md_file in documentation/jmf_masterclass_crop_sheets/*.md:
    text = read(md_file)
    crop_jmf_en = lookup_jmf_key(md_file_hebrew_name)
    sections = parse_md_sections(text)  # cultivars, spacing, pests, ...
    notes = {
        "pest_pressure": [],
        "disease_pressure": [],
        "general_husbandry": [...],  # cultivars + spacing → general
        ...
    }
    write_json(f"data/jmf/extracted/jmf_book/{crop_jmf_en}.json", notes)
# Then: python scripts/seed.py --ni-only
```

Effort: small follow-up WP (patch04 candidate or post-patch03 operational task).

### 2. Direct cultivar data for `crop_varieties` table

Each sheet enumerates 4-8 specific cultivars (e.g., Tomatoes lists 8 named cultivars including the rootstock Maxifort). This is **structured variety data** that can populate `crop_varieties` directly — currently sparse in the DB.

### 3. patch03 architectural decisions VALIDATED by field evidence

The user's own farm reference materials prove that:
- **"מלפפון חממה" is a real, separate crop classification** (17-page sheet) → patch03 §1.3 split is correct.
- **"בייבי מיקס - חסה" + "מיזונה וחרדל" are distinct variants under the עלי בייבי umbrella** → patch03 §1.1 new baseline is correct.
- **"שומר בייבי" exists as a sheet → cultivar approach for Mini Fennel is correct** (status-quo confirmed).

### 4. New WP candidates surfaced (post-patch03)

- **patch04 (small):** Add `Rocket → ארוגולה` alias; `Frisée → אנדיב` alias; `לפט` typo handling.
- **patch05 (medium):** Add new crops surfaced here:
  - `Ginger → ג'ינג'ר` (or פונטי "גינגר")
  - `Storage Carrots → גזר איחסון` (new baseline OR cultivar under גזר)
  - `Greenhouse Pepper → פלפל חממה` (new baseline, mirroring the cucumber split)
  - `Greenhouse Beefsteak Tomato → עגבניות חממה` (new baseline)
  - `Field Tomatoes → עגבניות שטח פתוח` (new baseline, OR keep mapped to עגבנייה)
  - `Mizuna → עלי בייבי`, `Mustard Greens → עלי בייבי` (variant aliases)
- **Schema follow-up:** the "עגבניות - הרכבה" (grafting) sheet is technique-not-crop content. Either add a `technique_notes` table or fold into `crop_knowledge_notes` with `note_type = 'general_husbandry'`.

### 5. Hebrew name_he sanity-check across the board

The MD filenames decode cleanly to canonical Israeli Hebrew. Cross-checking against `JMF_CROP_MAP` post-patch03:
- 19 of 20 matched sheets use IDENTICAL Hebrew to what patch03 will lock — strong validation.
- One drift: `בזיל` filename vs patch03's `בזיליקום`. The user's own filing uses `בזיל`, so patch03's normalization to `בזיליקום` is an upgrade, not a correction. (The filename may simply have been chosen years ago.)

---

## Recommended next actions

| Priority | Action | Owner | Effort |
|----------|--------|-------|--------|
| **HIGH** | Close patch03 (already in flight — L-GATE_S R1 returned FAIL with localized issues; R2 incoming) | team_110 + team_190 | small |
| HIGH | Open patch04 (operational): write `scripts/load_masterclass_sheets.py` to convert these MDs into `data/jmf/extracted/jmf_book/*.json`. Then `seed.py --ni-only`. | team_110 + team_10 | medium |
| MEDIUM | Open patch05 (taxonomic): add 5-8 new crops + 2-3 aliases per §1 + §4 above | team_110 | medium |
| LOW | Decide cultivar-level pipeline (populate `crop_varieties` from MasterClass cultivar lists) | team_00 (architecture) + team_110 | medium |

---

## Provenance

| Item | Value |
|------|-------|
| Original extraction tool | NotebookLM (Google) + pdf2md converter |
| Delivered as | ZIP archive `/Users/nimrod/Downloads/pdf2md_markdown_and_images.zip` |
| Date | 2026-05-25 |
| Licensing | Internal-farm-use only (IR — same fair-use posture as B2 §3.1). DO NOT republish externally. |
| Storage | `documentation/jmf_masterclass_crop_sheets/` (versioned in git) |
| Index | `_index.json` (cross-reference to JMF_CROP_MAP) |

---

*README authored 2026-05-25 by team_110 (Claude Opus 4.7) after analyzing the NotebookLM deliverable.*
