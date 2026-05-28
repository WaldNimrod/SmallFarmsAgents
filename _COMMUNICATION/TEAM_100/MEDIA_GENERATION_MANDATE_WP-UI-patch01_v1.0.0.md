# MEDIA GENERATION MANDATE — SFA UI visuals (WP-UI-patch01)

**Single handoff dossier for an external media-generation tool/session.**
team_100 does NOT generate media (IR#1). This is the consolidated list +
requirements + mandate for team_00 to route to Midjourney / DALL·E / Imagen /
Sora / Claude Desktop (image-gen).

- **From:** team_100 (Chief System Architect)
- **To:** team_00 → external media session
- **Date:** 2026-05-28
- **WP:** SFA-S003-P002-WP-UI-patch01
- **Site:** https://sfa.nimrod.bio/

---

## 1. Detailed list — every missing visual

Status legend: **BREAK** = referenced + missing (visible defect) · **WIRED** =
code slot ready, asset missing (graceful fallback) · **LATENT** = design intent,
not yet wired · **GAP** = production best-practice, not referenced.

| # | Asset | Final path | Dims | Format / budget | Status | Priority | Prompt source |
|---|-------|-----------|------|-----------------|--------|----------|---------------|
| 1 | og-default | `public_assets/img/og-default.webp` | 1200×630 | WebP q80 ≤120 KB | **BREAK** | **P0** | [MEDIA_PROMPT_og-default](MEDIA_PROMPT_og-default_v1.0.0.md) (3 variants) |
| 2 | hero · crop-book | `public_assets/img/heroes/crop-book.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | [MEDIA_PROMPT_module_heroes](MEDIA_PROMPT_module_heroes_v1.0.0.md) §1 |
| 3 | hero · market | `public_assets/img/heroes/market.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | …§2 |
| 4 | hero · calc | `public_assets/img/heroes/calc.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | …§3 |
| 5 | hero · planner | `public_assets/img/heroes/planner.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | …§4 |
| 6 | hero · clients | `public_assets/img/heroes/clients.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | …§5 |
| 7 | hero · inventory | `public_assets/img/heroes/inventory.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | …§6 |
| 8 | hero · tend-bridge | `public_assets/img/heroes/tend-bridge.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | …§7 |
| 9 | hero · field-log | `public_assets/img/heroes/field-log.webp` | 800×800 | WebP q80 ≤90 KB | WIRED | P1 | …§8 |
| 10 | hub hero | `public_assets/img/hub-hero.webp` | 1600×900 (16:9) | WebP q80 ≤140 KB | LATENT | P2 | `modules.php` → `thumb_prompts['module_hub']` (HE) |
| 11 | contact illustration | `public_assets/img/contact.webp` | 1600×900 (16:9) | WebP q80 ≤140 KB | LATENT | P2 | `modules.php` → `thumb_prompts['contact']` (HE) |
| 12 | favicon set | `public_assets/img/favicon.ico` + `favicon-32.png` + `apple-touch-icon.png` (180×180) | ICO/PNG | ≤30 KB each | GAP | P2 | derive from SFA seedling mark (see §4) |

**P0/P1 (items 1–9)** are this wave's deliverable — prompts are already authored,
spec'd, and copy-paste ready. **P2 (items 10–12)** are recommended follow-ons;
prompts 10–11 already exist (Hebrew) inside `modules.php::thumb_prompts`; the
favicon (12) needs deriving from the brand mark.

> Note on the 8 module thumbnails in `modules.php::thumb_prompts['module_thumb_*']`:
> those Hebrew prompts describe the SAME 8 mod-card art slots as items 2–9. The
> English prompts in MEDIA_PROMPT_module_heroes_v1.0.0.md are the detailed, spec'd
> SSoT for generation — use those; the Hebrew metadata is the original design
> intent and is consistent with them.

---

## 2. Requirements documents (the binding specs)

- **og-default (item 1):** `_COMMUNICATION/TEAM_100/MEDIA_PROMPT_og-default_v1.0.0.md`
  — 3 variants, target spec, palette, delivery instructions.
- **module heroes (items 2–9):** `_COMMUNICATION/TEAM_100/MEDIA_PROMPT_module_heroes_v1.0.0.md`
  — 8 slug-exact prompts, shared spec, slug→file→palette table.

Both carry the full design system (palette from `gj.css`: paper `#f6f1e3`, leaf
`#6f8a45`, tomato `#c24f2c`, sun `#d39a32`, soil `#8b5d2f`, ink `#2a2418`;
heading font Frank Ruhl Libre) and the calm-craft watercolor + ink-linework
style. **No text in any image** (HTML renders the Hebrew); **no photographs.**

---

## 3. Mandate to the external media session

1. Generate items **1–9** (P0/P1) using the copy-paste prompt blocks in the two
   requirement docs above. og-default: pick a variant (Variant 1 recommended).
2. Export each at the exact dims/format/budget in §1. **WebP, sRGB.** Verify
   byte budget (≤120 KB og, ≤90 KB heroes).
3. Save with the **exact filenames + paths** in §1, into the deploy worktree
   under `sfa_delivery/public_assets/img/`.
4. (Optional, P2) Generate items 10–12 if proceeding to the latent slots.
5. Notify team_100 when assets land → team_100 sets `modules.php` `hero_url` per
   module, commits, and runs the bundled deploy + L-GATE_V re-validation
   (per WP-UI-patch01 deferred sub-items).

**Quality bar:** all 9 share one visual family (same paper, same brush/ink
treatment, consistent saturation) so the card grid + share image read as one set.

---

## 4. Favicon (P2) derivation note
Derive from the SFA seedling mark (two-leaf sprout, leaf-green `#6f8a45`) on
paper `#f6f1e3`, centered, generous padding. Export `favicon.ico` (16/32/48),
`favicon-32.png`, `apple-touch-icon.png` (180×180, no transparency). Then add the
`<link rel="icon">` / `apple-touch-icon` tags to `sfa_delivery/templates/_layout.php`
(team_100 wires once assets exist).

---

## 5. Routing record
- og-default routed: `MSG-team100-to-team_00-MEDIA-og-default-PROMPT-2026-05-28.md`
- heroes routed: `MSG-team100-to-team_00-MEDIA-module-heroes-PROMPT-2026-05-28.md`
- This dossier consolidates both + adds the latent + favicon gaps for one handoff.
