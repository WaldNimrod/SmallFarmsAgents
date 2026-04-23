# Agents — SmallFarmsAgents (OrganicMarketAgent)

## Default scope

You are in the **SmallFarmsAgents** repository: **OrganicMarketAgent** (SFA) — Python data hub, admin UI, PostgreSQL, uPress publish path for the **vegetable price index**.

**Public market index (end users):** the themed WordPress page (e.g. `https://www.nimrod.bio/smallfarmsagent/`) embeds **`public_report_body.html`** via `[sfagent_market_report]` + **`sfagent-base.css`** in the child theme — not the standalone `public_report.html` file alone. See [`documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md).

## Do not mix products

**Famely Neusletter**, **TikTrack**, and **agents-os** live in **other repositories** (and other systemd units on waldhomeserver). Do not commit their primary source reports or app code here.

- **Boundary reference:** [`documentation/external-references/CROSS_PROJECT_BOUNDARIES.md`](documentation/external-references/CROSS_PROJECT_BOUNDARIES.md)
- **Machine-level handoff (all products):** `~/Documents/_agent_comm/` — see [`documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md)

## AOS governance (read)

- **`_aos/context/PROJECT_CONTEXT.md`** — AOS + domain context; **ADR034** applies if/when AOS v3 DB holds structured AOS state.
- **`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`** — require **0 FAIL**; PASS/SKIP totals vary with lean-kit. **Current expected profile (2026-04-22, Team 190):** **26 PASS / 9 SKIP / 0 FAIL** (see [`_aos/context/PROJECT_CONTEXT.md`](_aos/context/PROJECT_CONTEXT.md) — full references).

## Full context

See [`.cursor/rules/project-context.mdc`](.cursor/rules/project-context.mdc) and [`docs/GLOSSARY.md`](docs/GLOSSARY.md).
