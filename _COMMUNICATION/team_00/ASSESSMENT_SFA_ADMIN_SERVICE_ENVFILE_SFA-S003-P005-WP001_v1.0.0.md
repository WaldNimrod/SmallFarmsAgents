---
id: ASSESSMENT_SFA_ADMIN_SERVICE_ENVFILE_SFA-S003-P005-WP001_v1.0.0
type: ASSESSMENT
deliverable: D4
wp: SFA-S003-P005-WP001
branch: pilot/arm-b
date: 2026-08-14
question: "Should the hard `EnvironmentFile=` (no '-' prefix) in sfa-admin.service be softened for SFA?"
verdict: "NO — keep it hard. Two adjacent changes recommended instead."
---

# D4 — `sfa-admin.service` EnvironmentFile: keep hard, do not soften

## The unit under discussion (facts pack §5, verbatim)

```ini
[Service]
Type=simple
User=nimrodw
WorkingDirectory=/data/projects/smallfarmsagents
ExecStart=/data/projects/smallfarmsagents/.venv/bin/python3 -m flask --app organic_market_agent.admin:create_app run --host 127.0.0.1 --port 5001
Restart=always
RestartSec=5
EnvironmentFile=/data/projects/smallfarmsagents/.env
```

`EnvironmentFile=` with no `-` prefix means: **if the file is missing or unreadable, the
unit fails to start.** `EnvironmentFile=-/path` is the optional form, where a missing file
is silently ignored and the process starts with those variables simply absent.

## Verdict: NO — do not soften.

### 1. Softening removes the alarm, not the fault

The capra-mio precedent is cited as the reason to consider softening, so it is worth being
exact about what went wrong there: an untracked `.env` was **destroyed by a deploy that
re-cloned the tree**. The hard `EnvironmentFile=` did not cause that; it *reported* it, in
the loudest available way, five seconds after it happened. Had the directive been soft, the
service would have started, answered `200` on `/`, and served with an empty configuration —
and the outage would have been discovered later, by a user, with the cause a day further
from the effect.

The real fix for that failure class is the one this WP implements: **the deploy path must
not destroy the deploy tree** (R3 — the D2 hook contains no `reset --hard`, no
`clean -fdx`, no `rm -rf`, no re-clone, and the D5 dry run asserts untracked files survive
every scenario). With that fix in place, softening the unit buys nothing and costs the
alarm.

### 2. For *this* app, a config-less start is worse than no start

`organic_market_agent.admin:create_app` reads `ADMIN_SECRET_KEY` from the environment and
**falls back to the literal `"dev-secret-change-me"`** when it is absent
(`organic_market_agent/admin/__init__.py`). The DB URL comes from the same env. A soft
`EnvironmentFile=` on a machine whose `.env` went missing therefore produces a *running*
admin app signing session cookies with a publicly-known development key and pointing at
whatever DB default is compiled in. That is not degraded service — it is a security-
relevant misconfiguration that presents as healthy.

Fail-fast is the correct posture precisely because this unit's missing-config behaviour is
silent-and-wrong rather than loud-and-broken.

### 3. Softening would manufacture a false green in the deploy path we just fixed

`/api/health` (D1) deliberately answers without touching the database, so that "which code
is this process running" stays answerable when a dependency is down. Combine a soft
`EnvironmentFile=` with that endpoint and you get: `.env` gone → service starts anyway →
`/api/health` returns the correct new `build_sha` → the D2 hook prints **DEPLOY VERIFIED**
on a service that cannot reach its database. R4 says a deploy is green only when the code
actually serving is asserted equal to the code pushed; that assertion would still be true
— and the deploy would still be a lie. Keeping the unit hard means that scenario ends as a
restart failure (hook exit 22) or an unreachable probe (exit 23), both red.

### 4. What the hard form actually costs, and how this WP pays it

The genuine downside is real and should not be waved away: `Restart=always` + `RestartSec=5`
+ a hard `EnvironmentFile=` is an unbounded 5-second crash loop that spams the journal and
never self-heals. Two adjacent changes remove that cost without giving up fail-fast:

**(a) Already delivered — the hook checks before it restarts.** The D2 hook's pre-flight
runs `test -s "$ENV_FILE"` **before** the pull and before the restart, and aborts with exit
20 if the file is missing or empty:

> `required env file …/.env is missing or empty — refusing to restart sfa-admin into a
> crash loop`

The old process keeps serving; nothing is mutated (dry-run scenario S5 asserts the deploy
tree HEAD is unchanged after the abort). Existence and size only — the file's content is
never read, printed or logged (R2). This converts "deploy pushes the service into a crash
loop" into "deploy refuses to start and says why", which is the outcome softening was
reaching for, obtained without blinding the unit.

**(b) Recommended, one line, conductor's call — bound the loop.** Add to `[Service]`:

```ini
StartLimitIntervalSec=60
StartLimitBurst=3
```

systemd then stops retrying after 3 failures in 60s and leaves the unit in `failed`, where
`systemctl status` states the reason once instead of scrolling it forever. This is a change
to `/etc/systemd/system/sfa-admin.service` — outside a builder's reach (no server access)
and outside the WP's K=6, so it is filed here as a recommendation, not delivered as a
change.

## Not recommended (considered and rejected)

- **Soften to `EnvironmentFile=-…`** — rejected for reasons 1–3 above.
- **Split into a hard `.env` plus a soft second file** — no current need; adds a second
  config surface for no gain.
- **Move secrets into inline `Environment=KEY=VALUE`** — actively worse: it exposes values
  to `systemctl show`/`cat` for any local user, whereas the current unit contains zero
  inline `Environment=` lines (facts pack §5) and `.env` is mode `600`.

## Optional follow-up, noted not delivered

The health endpoint prefers `AOS_BUILD_SHA` and falls back to `git rev-parse HEAD` read at
process start. The env form is the stronger evidence (it is stamped by the deploy path
rather than derived from the tree). If that is wanted later, the clean shape is a **soft,
deliberately optional** second file — `EnvironmentFile=-/data/projects/smallfarmsagents/.deploy_build_sha`
— written by the hook just before the restart. Soft is correct *there* precisely because
its absence must not stop the service: it is telemetry, not configuration. That asymmetry
is the whole answer to this question — the `-` prefix belongs on files the app can live
without, and `.env` is not one of them.
