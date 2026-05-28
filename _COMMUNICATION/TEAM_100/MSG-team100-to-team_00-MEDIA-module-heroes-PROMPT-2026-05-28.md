# MSG — team_100 → team_00 : module hero prompts ready (×8)

- **From:** team_100 (Chief System Architect)
- **To:** team_00 (Principal)
- **Date:** 2026-05-28
- **Re:** WP-UI follow-up Item D — 8 module-card hero images

## Ask

The 8 mod-cards on `/` currently render the icon enlarged (no `<img>` hero).
Code wiring is now in place (`module_card.php` emits `.mod-card__hero` when
`hero_url` is set; `hub.css` reverts the icon to a corner badge automatically).
team_100 authored 8 generation prompts; team_100 does NOT generate media. Please:

1. Run each of the 8 copy-paste blocks in `MEDIA_PROMPT_module_heroes_v1.0.0.md`.
2. Export each **800×800, WebP q80, ≤90 KB**, **no text in image**.
3. Save with slug-exact filenames to `sfa_delivery/public_assets/img/heroes/`:
   `crop-book.webp, market.webp, calc.webp, planner.webp, clients.webp,
   inventory.webp, tend-bridge.webp, field-log.webp`.
4. Notify team_100 → team_100 sets `hero_url` per module in `modules.php`,
   commits + deploys.

## Prompt artifact

`_COMMUNICATION/TEAM_100/MEDIA_PROMPT_module_heroes_v1.0.0.md` — 8 copy-paste
blocks + shared spec + slug→file→palette table.

## Note on scope (IR#1 / IR#3)

Items A + D are visual-only and may re-trigger team_190 L-GATE_V on the next
deploy. team_100 will bundle the og-default + hero rollout into a single
validation pass once images land, rather than deploying piecemeal.
