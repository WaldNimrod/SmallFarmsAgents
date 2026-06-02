# M10.4 R3 — Shell-store forensics (Team 10)

**Date:** 2026-04-05  
**Context:** Team 50 R2 T03 — SRC042, SRC055, SRC062, SRC069 returned `wait_for` timeouts, ~49–56kB HTML, no `pips-card-content`, parser 0 rows.

## Findings

1. **Initial HTML** includes `window._INITIAL_STORE_DATA_` (store metadata). For at least **SRC042 (brodavkameshek)** the JSON shows **`takingOrders: false`** and a **deleted / inactive plan** path in the same payload — the SPA often **does not render a priced catalog** while the storefront is closed to new orders, so **no `₪` in `document.body.innerText`** regardless of wait length (verified via Playwright in a headless environment).

2. **SRC055 (meshek27)** and **SRC062 (poli)** showed similar **no-₪** snapshots after extended waits; **SRC069 (solomon)** remained **no-₪** after scroll + long polling in the same environment (may vary by region or store state).

3. **Working stores** (e.g. `nimrod`, `cohen` on `/products`) reach **`₪` + `pips-card-content`** within ~8–15s with the same Playwright settings.

## Code / data response (R3)

- **Collector:** Ordered **welcome CTA clicks** (`extra_welcome_cta_names` before `dismiss_ok_button_name`) so open-state dialogs (e.g. **יאללה ממשיכים!**) dismiss before catalog load.
- **Collector:** **`currency_poll_timeout_ms`** — poll for price markers in `body.innerText` with **scroll nudges** after the primary `wait_for_selector` (covers slow Firestore hydration).
- **Migration `057`:** Applies **`currency_poll_timeout_ms: 120000`**, longer **`post_load_delay_ms`**, **`extra_welcome_cta_names`** for SRC042, and **`m10_4e`** cache-bust on entry URLs for the four codes.
- **Parser:** Price-anchor fallback allows slightly **larger text blocks** (350 chars) before skipping, for MUI grid cells.

## If T03 still fails after R3

Re-check `_INITIAL_STORE_DATA_.takingOrders` / store `active` on the **QA runner** at ingestion time. If stores are **closed**, extraction may legitimately be **0 rows** until they reopen — escalate to **Team 100** for source substitution or mandate waiver rather than infinite Playwright waits.
