# MSG — team_100 → team_00 : og-default media prompt ready

- **From:** team_100 (Chief System Architect)
- **To:** team_00 (Principal)
- **Date:** 2026-05-28
- **Re:** WP-UI follow-up Item A — Open Graph default share image

## Ask

`_layout.php` references `https://sfa.nimrod.bio/public_assets/img/og-default.webp`
but the file doesn't exist → social-share previews break. team_100 authored the
generation prompt (3 variants); team_100 does NOT generate media. Please:

1. Pick a variant from `MEDIA_PROMPT_og-default_v1.0.0.md` (Variant 1 = team_100
   recommendation) and paste it into your image-gen session
   (Midjourney / DALL-E / Imagen / Sora / Claude Desktop — your choice).
2. Export **1200×630, WebP q80, ≤120 KB**.
3. Save to `sfa_delivery/public_assets/img/og-default.webp` in the deploy worktree.
4. Notify team_100 → team_100 commits + deploys via `scripts/ftp_deploy_sfa_ui.sh`.

## Prompt artifact

`_COMMUNICATION/TEAM_100/MEDIA_PROMPT_og-default_v1.0.0.md` — 3 copy-paste blocks.
