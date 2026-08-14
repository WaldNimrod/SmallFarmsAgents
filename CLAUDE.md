# CLAUDE.md — SmallFarmsAgents

<!--
  LEAN ENTRY CONTRACT v1.0.0 — pilot branch `pilot/lean-env` only, never merged to main.
  disposition: SUPERSEDES this file's AOS-CANONICAL-TEMPLATE v1.0.0 rendering (git log -- CLAUDE.md
  shows the prior version). Rewritten under the pilot's explicit IR#10/IR#11 exception; the durable
  form of this change is a hub renderer change, not a spoke hand-edit.

  WHAT INJECTS THIS FILE (resolved includes — the whole list, nothing hidden):
    1. This file is auto-loaded by the agent harness because it sits at the repo root. Nothing else
       in this repo is auto-loaded.
    2. This file mandates reading NO other file. Two commands are mandatory (§2); their output is
       your context, and both are small and derived.
    3. AGENTS.md, .cursorrules, _aos/context/*.md and documentation/** exist and are NOT required
       reading. They are indexed in §6 — open one only when §6 says it answers your question.
-->

## 1. Where you are

- **Repo:** `SmallFarmsAgents` · path `/Users/nimrod/Documents/AOS_V5/SmallFarmsAgents` · profile `L0`
- **Stack:** Python 3.11, Flask, PostgreSQL 15, Docker, SQLAlchemy 2.x + Alembic, httpx. Public delivery tier is Slim 4 / PHP 8 + PDO/MySQL. Playwright for SPA collectors.
- **`_aos/` is a read-only snapshot** of org-wide governance. Do not edit it. If a rule there blocks you, say so in your delivery report — do not work around it silently.

## 2. Session start — two commands, no reading list

```bash
# (a) your work package row — derive it, never read the whole roadmap
python3 -c "import yaml,sys; wp=sys.argv[1]; d=yaml.safe_load(open('_aos/roadmap.yaml')); r=[w for w in d['work_packages'] if w['id']==wp]; print(yaml.safe_dump(r[0], sort_keys=False, allow_unicode=True) if r else f'NO SUCH WP: {wp}')" <YOUR-WP-ID>

# (b) the test suite, exactly this invocation
.venv/bin/python3 -m pytest -m "not upress and not integration" -q
```

Known pre-existing baseline of (b): `1 failed, 1002 passed, 88 skipped, 25 deselected`. The one failure is `tests/crop_book/test_wp_upload_crop_book.py::test_dispatch_upload_crop_book_profile` and it is not yours. **Green = zero NEW failures.** (`.venv/bin/pytest` directly is broken — dead shebang from a repo move; use the `python3 -m` form above.)

Nothing else is required before you start work.

## 3. Rules that bind — each one mechanically checkable

| # | Rule | How it is checked |
|---|---|---|
| R1 | Every acceptance criterion cites the command that verifies it. A claim with no command is not evidence. | Read the AC: it either contains a runnable command or it fails. |
| R2 | Never read, print, or log the contents of any `.env*` file, and never put a secret in a command line. | `grep -nE 'cat .*\.env\|source .*\.env' <your diff>` → empty. Existence checks use `test -s`. |
| R3 | Nothing in a deploy path may destroy the deploy tree: no `git reset --hard`, no `git clean -fdx`, no `rm -rf` of the project dir, no delete-and-reclone. Untracked `.env` and `.venv` live there; destroying them is a known multi-hour outage class. | `grep -nE 'reset --hard\|clean -fdx\|rm -rf\|git clone' <your diff>` → hits must be comments or a disposable temp sandbox only. |
| R4 | A deploy is green only when the code that is **actually serving** is asserted equal to the code you pushed. A hook exit code, a log line, or a bare HTTP 200 is never sufficient. | The deploy path compares a served build SHA to the pushed SHA and fails loudly, non-zero, on mismatch. |
| R5 | Before adding a file, search for the one that already exists and edit it. A new file carries a one-line justification naming the search that returned zero. | `git diff --diff-filter=A --name-only <base>..` — every entry justified. |
| R6 | `spec_ref` values in `_aos/roadmap.yaml` are repo-internal paths that resolve. | `test -f "$(spec_ref)"` |
| R7 | The decisive validation gate is run by a different vendor's model than the one that built the change. You do not run it; the conductor does. Your job is to make it checkable. | Gate verdict names builder and validator engines explicitly. |
| R8 | English in all source, docs, and inter-team artifacts. Hebrew only in direct conversation and in product-name seed data. | — |

## 4. Domain rules — load-bearing, do not re-derive

- **⚠ Delivery & hosting canon (SSoT: `documentation/02-architecture/sfa-delivery-tier.md`). Three roles, never conflated:**
  - **Web host = uPress** (shared LAMP, `sfa.nimrod.bio`, Cloudflare edge). The **only** machine that serves end-user HTTP and hosts the live MySQL. The site must live here — never on the home server.
  - **Backend / pipeline host = waldhomeserver** (canonical Postgres SSoT, scrapers, agents, cron). **Never serves end users** — outbound HTTPS to the delivery tier only.
  - **Deploy / push origin** = whichever machine's current external IP is allowlisted on uPress. "Deploy host" means the machine you deploy *from*, not the machine that serves. Code → `lftp mirror` to uPress (`UI_DEPLOY_RUNBOOK.md`); data → `POST https://sfa.nimrod.bio/api/v1/ingest` (HMAC).
  - **⚠ The uPress FTPS allowlist is dynamic, per current external IP.** Port-21 FTPS accepts only allowlisted sources and home/office IPs are not static. To deploy from any machine, ask Nimrod to open that machine's current external IP — it takes seconds. The Mac can deploy directly (`bash scripts/ftp_deploy_sfa_ui.sh`). Symptom of a closed IP: TCP to `ftp.s1240.upress.link:21` **times out** → run `curl https://api.ipify.org` and ask. (HTTPS *data* ingest goes through Cloudflare and needs no allowlist — only FTPS *code* deploy does.)
- **Local port canon:** Postgres `5433` (`oma-postgres`), Admin `5001`, Viewer `8081`. Never `8080` or `5432` — other projects own those.
- **Deploy paths (current):** UI code → `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`. Data → `organic_market_agent/publisher/sfa_ingest_push.py`. **Superseded:** the WP-REST/FTPS/mu-plugin upload to `www.nimrod.bio` — that tier was retired 2026-05-28; do not revive it without a new decision record.
- **Dev/staging TLS is often invalid by design.** A cert error on a dev/staging URL is expected, not a defect; on production it is a real defect. Bypass flags (`curl -k`, `--ignore-certificate-errors`, `verify=False`) are dev-only.
- **`curl` alone never validates layout** — it sees HTML, not the rendered box model. Use a real browser probe for any layout/RTL/overflow check.

## 5. Where work is recorded

- Work packages and gate history: `_aos/roadmap.yaml` (derive your row with §2a; a spoke row is edited directly and committed — that commit is the audit record).
- Inter-team artifacts: `_COMMUNICATION/team_<id>/`.
- Ask before assuming: if a rule you need is missing here, that absence is a finding worth reporting, not a gap to fill by guessing.

## 6. Index — what exists, and the question it answers

| If you need… | Open | Not otherwise required |
|---|---|---|
| Product/ops background, parity sign-offs | `_aos/context/PROJECT_CONTEXT.md` | ✔ |
| Role framing for a builder/validator/architect seat | `_aos/context/ACTIVATION_*.md` | ✔ |
| The Cursor-engine rule set | `.cursorrules` | ✔ (not loaded by this harness) |
| A second short repo orientation | `AGENTS.md` | ✔ |
| Architecture, runbooks, troubleshooting | `documentation/` (start at `documentation/README.md`) | ✔ |
| Org-wide governance canon, directives, team charters | `_aos/governance/`, `_aos/methodology/` | ✔ |
| Deploy verification rules in full | `documentation/05-admin-and-operations/` | ✔ |

Everything in this table is optional. If you open one, say so in your delivery report — reading is a cost and we measure it.
