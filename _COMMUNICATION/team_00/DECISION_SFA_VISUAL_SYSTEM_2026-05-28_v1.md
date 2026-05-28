---
id: DECISION_SFA_VISUAL_SYSTEM_2026-05-28_v1
from: team_00 (Principal — in-session via /AOS_decide)
to: [team_100]
date: 2026-05-28
type: DECISION
scope: SFA Visual System Phase 2 (design/planning — pre-WP); ChatGPT design handoff
status: AUTHORIZED
trigger: "team_100 prepared SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF package with 10 decisions (D01-D10). /AOS_decide brief generated; team_00 ruled in-session."
api_note: "Hub API unreachable from Mac (127.0.0.1:8090 HTTP 410; 100.125.98.56:8090 000000). File-based context fallback per ADR043 §15.4."
---

# DECISION — SFA Visual System Phase 2

## §1. Rulings (D01–D10)

| ID | Topic | Ruling | Notes |
|----|-------|--------|-------|
| D01 | Scope | **C** — full visual system, **phased** | 2a assets → 2b icons → 2c textures/empty/community/future |
| D02 | Style anchor | **B** — nimrod.bio illustrations PRIMARY | SFA v1 prompts demoted to technical/product specs only |
| D03 | Reference base | **C** — full style board (15–30 refs) | Commission new pieces in the nimrod.bio hand / locate offline design files; only ~4 exist online |
| D04 | First production step | **C** — calibration set first | (recommended default, accepted) |
| D05 | Calibration size | **6** | 8 if including icon + community scene |
| D06 | Generator workflow | **C** — hybrid | ChatGPT for prompt design + review; best generator for finals |
| D07 | Final file production | **C** — hybrid | visual-approve PNG → scripted sips/cwebp |
| D08 | Naming/folders | **C** — versioned workflow | candidates / approved / rejected |
| D09 | Icon style | **B** — line-art + minimal wash | matches existing line basket; UI-usable |
| D10 | Literalness | **B** — mix literal + abstract | product-system balance |

## §2. Revised sequence (consequence of D03=C)

D03=C inserts a reference-board prerequisite BEFORE calibration:

1. **Phase 2.0 — Reference board:** collect/commission 15–30 illustrations in the
   nimrod.bio hand (only ~4 genuine pieces exist online → likely new commissions
   or offline design-file retrieval). Build the style board.
2. **Phase 2a — Calibration:** 6-image calibration set (D04/D05) → team_00 style approval.
3. **Phase 2b+ — Production:** families in order (brand/OG + 8 heroes → icons +
   favicon → textures/backgrounds + empty states + community), versioned (D08),
   hybrid generate (D06) + hybrid export (D07).

## §3. Open parameters
- D03: source of the extra references (commission vs. offline files) — TBD by team_00.
- D06: whether to stay all-in-ChatGPT or use external generators for finals — TBD.
- "Future module visuals" (D01-C phase 2c) scoped when those modules are defined.

## §4. Pointers
- Handoff package: `_COMMUNICATION/TEAM_100/SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF/`
- Ready-to-upload: `…/07_READY_TO_UPLOAD_TO_CHATGPT/` (+ 4 anchors in `…/03_.../images/`)
- Decision table (updated to reflect these rulings): `…/06_DECISIONS_FOR_NIMROD/decision_table.md`
