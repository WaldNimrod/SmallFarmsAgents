# team_100 visual sweep — full system vs mockups — live acca9b2 — 2026-06-04

**Method:** qa_probe CDP (--shots) on live sfa.nimrod.bio @ acca9b2 (?v=1780576560), desktop 1440 + mobile 375; team_100 (Opus) eyes-on each surface vs Board-A/B. Run in parallel with an external non-Claude validator for cross-comparison.

## Bottom line: GO-WITH-MINOR-FIXES — 0 BLOCKER, 0 MAJOR
Structurally all surfaces PASS (qa_probe: no overflow, no console errors, no forbidden tokens). On-brand (#f8fbf8 white-green, watercolor, RTL). The crop-book (team_00's concern) is now correct: 70/70 watercolors, 168px cards, single centered crop page.

## Per-surface
- **Hub /** — PASS. 4 tool tiles w/ watercolor module art, audience cards, stats, CTA. (lower "Tend coming-soon" tile = known/acceptable per L-GATE_V.)
- **Crop-book /crop-book/** — PASS. 168px cards, watercolor art all crops, toggle aligned, filters.
- **Crop page** — PASS. single hero, centered 1120px, formatted values, no green blob.
- **Calculator /calc/** — PASS structural; 14 modules + spacing viz + price table. HIGHEST-priority for precise Board-A fidelity confirmation (densest surface; not pixel-certified from thumbnail). INFO: machine JSON English keys (not user-visible).
- **Market /market/** — PASS. Hebrew chips, ₪ prices, freshness pills, source counts. High density.
- **Search** — PASS (grouped book/market, Hebrew, highlighted term). MINOR: crop result uses letter-glyph not watercolor; content right-hugs at 1440.
- **About /about** — PASS. 5-tier, no Tend. Q5: English tier eyebrows (OPEN/BETA/COMING/PAID/CUSTOM) — decide per Q5=B.
- **Community** — PASS. watercolor hero, contribution form.

## MINOR/COSMETIC punch-list (fold into WI-7 build)
1. Search crop results → use the crop watercolor (wc-*) instead of the letter-glyph.
2. Q5 eyebrows (already decided B): Hebraize menu-like hub tiles; decide /about tier badges.
3. Calculator: confirm precise layout/type vs Board-A (external + close look).
4. (carryover) calc machine JSON English keys — leave (machine) unless flagged user-visible.

Evidence: team100_sweep_acca9b2/ (desktop+mobile per surface).
