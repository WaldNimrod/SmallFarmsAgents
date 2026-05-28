# Audit — existing SFA media package (MEDIA_CHATGPT_PROJECT)

Audited the prior package (copied verbatim into `original_docs/`). It was built
for a narrow goal: generate the 12 known assets. Phase 2 widens scope to a full
visual system. Verdict per artifact:

| Artifact | Keep / Demote / Rework | Reason |
|----------|------------------------|--------|
| `C3_ASSET_SPEC_TABLE.md` | **KEEP (as technical spec)** | Accurate paths/dims/budgets + sips/cwebp export recipe. Still the SSoT for file specs. |
| `context/reference_existing/` (3 refs + README) | **KEEP + EXPAND** | Correct anchors; expand with the flyer + style-DNA notes from section 03. |
| `00_PROJECT_DESCRIPTION.md` / `01_PROJECT_INSTRUCTIONS.md` | **REWORK** | Good bones, but lead with nimrod.bio anchors + calibration-first; superseded by the `07_READY_TO_UPLOAD` revisions. |
| `STYLE_UPDATE_PROMPT_for_media_team.md` | **KEEP / PROMOTE** | This is the correct direction (continue the line); fold into the revised instructions. |
| `C1_BRAND_AND_PRODUCT.md` | KEEP (light edit) | Product context still valid. |
| `C2_DESIGN_SYSTEM.md` | KEEP (merge into C2_VISUAL_DNA) | Palette/type accurate; needs the style-DNA observations added. |
| `C4_ICON_VOCABULARY.md` | KEEP (light) | Useful subject anchors; reframe as guidance not mandate. |
| `SESSION_01..12_*.md` | **DEMOTE to "asset spec stubs"** | Per-asset target specs are useful, but the *prompt bodies* are too generic and over-emphasize "seedling + tomato + carrot" centered lineups. Do NOT use as-is for generation. |
| `README_MAPPING.md` | KEEP (superseded by Phase 2 README) | Historical map of the v1 package. |

## Specific problems to fix in Phase 2
1. **Generic AI-watercolor risk:** the session prompts describe scenes but don't
   bind hard enough to the *actual* reference images → output drifts to stocky
   AI watercolor. Fix: every prompt must attach + match `ref_watercolor_radishes.jpg`.
2. **Repetition:** "seedling + tomato + lettuce + carrot" recurs across og-default
   and several heroes → the set risks looking same-y and icon-like. Fix: vary
   subjects per the asset-family guidance; favor loose single-subject/cluster
   compositions with breathing room over centered lineups.
3. **One-shot scope:** v1 implied generating all 12 at once. Fix: calibration set
   first (6–8), approve style, then produce.
4. **No icon/texture/empty-state families:** v1 covered only og + heroes + favicon.
   Phase 2 must define the broader families (icons, textures, empty states).
5. **Keep technical specs authoritative:** dims/paths/budgets/export recipe from
   C3 remain binding — don't relitigate those; only the *art direction* changes.
