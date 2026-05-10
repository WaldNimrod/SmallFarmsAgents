---
id: GCR_AOS_MESSAGING_INFRA_HARDENING_v1.0.0
type: GOVERNANCE_CHANGE_REQUEST
from: team_100 (smallfarmsagents)
to: team_100 (agents-os hub)
cc: team_00
date: 2026-05-10
version: v1.0.0
urgency: HIGH
target_files:
  - core/governance/team_100.md (no change — this is the addressee, not the target)
  - _aos/governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.4.0.md (likely → v1.5.0)
  - lean-kit/modules/team-messaging/scripts/msg_preflight.sh
  - .claude/commands/AOS_SendMail.md
  - .claude/commands/AOS_mail.md
  - lean-kit/modules/team-messaging/MSG-HUB.template.md
  - core/.env / core/.env.example
project: smallfarmsagents (spoke originator) → agents-os (hub-side action)
related_wps: AOS-V4.1-WP-MSG-INFRA-HARDENING (v1.4.0 predecessor); recommend new WP `AOS-V4.2-WP-MSG-AUTH-AND-ROUTING-FIX`
propagation_command: /AOS_gov-update
next_step: "Open AOS-V4.2-WP-MSG-AUTH-AND-ROUTING-FIX work package; team_100@agents-os authors LOD400 covering R1–R9 below; team_190 L-GATE_S; team_10 build; team_190 L-GATE_V; /AOS_gov-update propagation."
handoff_to: team_100
handoff_context_pointer: _COMMUNICATION/TEAM_100/GCR_AOS_MESSAGING_INFRA_HARDENING_2026-05-10_v1.0.0.md
---

# GCR — AOS Messaging Infrastructure Hardening (post-waldhomeserver migration)

**A canon refresh for inter-team messaging, mandate routing, and activation prompts after the AOS-v4 migration to waldhomeserver. Filed under Iron Rule #11 / ADR040 governance change procedure. Authority for execution: team_00 + team_100@agents-os only.**

---

## §1. Requesting Team

| Field | Value |
|-------|-------|
| Team ID | team_100 (in spoke `smallfarmsagents`, profile L0) |
| Role | Chief System Architect for `smallfarmsagents` |
| Engine | Claude Sonnet 4.6 declared / Opus 4.7 actual (mixed-mode session) |
| Branch | `claude/strange-mcnulty-651551`, HEAD `ccdf965` |
| Authority basis | Iron Rule #11 §"To request a governance change: file `GOVERNANCE_CHANGE_REQUEST` artifact in `_COMMUNICATION/team_XX/` → route to `team_100` in the hub" (CLAUDE.md spoke template) |

---

## §2. Executive summary

In the course of a multi-session WP004 build orchestration (S003 / SmallFarmsAgents) we relied on the canonical hub messaging stack — `/AOS_SendMail`, `/AOS_mail`, `msg_preflight.sh`, the FastAPI `/api/messaging/*` and `/api/prompts/generate` endpoints — and discovered **a chain of friction points and one outright protocol break** that block routine inter-team handoffs across the Mac ↔ waldhomeserver boundary.

Net effect for spoke teams: every L-GATE handoff degrades to a manual file-fallback path and requires the orchestrator to compose ad-hoc activation prompts. The canon-stipulated API path is unreachable for unprovisioned teams without an admin step that is undocumented in the spoke onboarding.

This GCR consolidates **9 empirical findings** (F-MSG-01..09) and proposes **9 graded recommendations** (R-MSG-01..09). Recommendations R-MSG-01..03 are CRITICAL/HIGH and unblock all other work. R-MSG-04..06 are MEDIUM (significantly reduce per-session friction). R-MSG-07..09 are LOW (cleanup and DX).

We recommend opening an explicit WP — tentatively `AOS-V4.2-WP-MSG-AUTH-AND-ROUTING-FIX` — and routing it through the standard L-GATE_S / L-GATE_B / L-GATE_V pipeline. The WP is bounded (no protocol re-design — only fixes) and should fit a NORMAL effort tier.

---

## §3. Scope and architecture context

The current ADR043 v1.4.0 (approved 2026-05-03) defines the canon for hub-mode inter-team messaging:
- §3.2 flat inbox layout (no `inbox/` subdir)
- §4 Branch Independence (`msg_deliver_file` pushes single-MSG to `origin/main` regardless of working branch)
- §5 API-First Pre-flight with HTTP 410 awareness (Mac legacy stub)
- §6 Multi-Domain Routing via `X-Project-Id` header
- §7 Single-MSG Archive endpoint
- §13 Continuation Prompt Standard (`next_step` / `handoff_to` / `handoff_context_pointer`)
- §15 Environment Variable Reference (three-tier `AOS_API_BASE` resolution)

The architecture migration from Mac-local API to waldhomeserver (Tailscale `100.125.98.56:8090`) is documented in §15.4 with explicit Mac-side env var setup. The Mac legacy stub at `127.0.0.1:8090` deliberately returns HTTP 410 (§5 Rule 4) to prevent silent writes to a dead DB.

**What works correctly:**
- §3.2 flat inbox layout — no friction observed.
- §4 `msg_deliver_file` — verified working in this session (`✓ MSG delivered via origin/main (fallback from branch=claude/strange-mcnulty-651551)`).
- §5 Rule 4 HTTP 410 detection — `msg_preflight.sh --verbose` correctly emits the redirect message.
- §13 continuation fields — used in our self-handoff artifacts and consumed correctly.
- The waldhomeserver API at `http://100.125.98.56:8090/api/system/health` returns HTTP 200.

**What is broken or under-specified — this GCR's subject matter:**
- §5 (auth model) — undocumented per-endpoint
- §5 (no-fallback-on-4xx rule) — over-strict
- §6 (`msg_detect_project_id` static map) — incomplete
- §15 (Mac key provisioning) — undocumented key delivery path
- (no §) Inter-domain MSG routing for cross-spoke addressing — not specified
- (no §) Branch-reference frontmatter for non-main mandates — not specified
- (no §) Activation prompt enrichment for WP-specific context — not specified

---

## §4. Empirical findings (F-MSG-01..09)

All findings are reproducible from a Mac Claude Code session in `smallfarmsagents` worktree `claude/strange-mcnulty-651551` against waldhomeserver `100.125.98.56:8090` (Tailscale online, API healthy) on 2026-05-10.

### F-MSG-01 — `ACTOR_KEY_NOT_CONFIGURED` blocks all team_100 messaging on Mac (CRITICAL)

```bash
$ msg_curl POST "/api/messaging/send" "$payload"
{"detail":{"code":"ACTOR_KEY_NOT_CONFIGURED",
 "message":"This team_id has no server-configured API key; contact admin.",
 "details":{"team_id":"team_100"}}}
```

**Reproducer:** any `POST /api/messaging/send` from a Mac session as `team_100` after correctly setting `AOS_API_BASE`, `AOS_ACTOR_TEAM_ID`, `AOS_PROJECT_ID`. The server's `AOS_V3_ACTOR_KEYS` does not contain a key for `team_100`. The expected `AOS_ACTOR_API_KEY` env var on the Mac side cannot be set because:
1. There is no documented retrieval path (where to read the key from).
2. There is no admin command to provision a key for an existing team.
3. ADR043 §15.4 instructs `export AOS_ACTOR_API_KEY=<value from waldhomeserver AOS_V3_ACTOR_KEYS>` — but does not specify how Mac-side agents obtain the value (SSH? File copy from waldhomeserver `/data/projects/agents-os/core/.env`? An `/api/actors/{team}/key` endpoint? None is canon).

**Impact:** Every API write call by team_100 from Mac fails 4xx → triggers the §5 Rule "DO NOT fallback on 4xx" → command exits with error → user must manually decide to fall back or abandon. In our session this happened on the very first `POST /api/messaging/send` of the session.

---

### F-MSG-02 — `/AOS_SendMail` "no-fallback-on-4xx" rule misclassifies auth/provisioning errors (HIGH)

ADR043 §5 step 3 says:
> **4xx** (client errors: bad schema, missing/invalid `X-Actor-Team-Id`, unknown project) → EXIT with actionable error. DO NOT fallback. These are programmer errors that a silent fallback would mask.

The taxonomy is right for genuine programmer errors (schema, header malformation). But `ACTOR_KEY_NOT_CONFIGURED` (and any `401/403` class returned by SEC-001 enforcement) is a **server-side provisioning state**, not a programmer error. The skill's strict no-fallback rule means an unprovisioned team cannot send any message via the canon path even though the file-fallback path is fully available, branch-safe, and auditable.

**Impact:** Compounds F-MSG-01 — even though `msg_deliver_file` would have delivered the MSG correctly, the skill's rule prevents reaching that path automatically.

---

### F-MSG-03 — `msg_detect_project_id` case statement is incomplete (HIGH)

Reading `lean-kit/modules/team-messaging/scripts/msg_preflight.sh::msg_detect_project_id`:

```bash
case "$remote_url" in
    *agents-os*)         echo "agents-os" ;;
    *TikTrack*|*tiktrack*) echo "tiktrack" ;;
    *EyalAmit*|*eyalamit*) echo "eyalamit" ;;
    *HobbitHome*|*hobbithome*) echo "hobbithome" ;;
    *Microgreens*|*microgreens*) echo "microgreens" ;;
    *AOS-Sandbox-Lean*) echo "aos-sandbox-lean" ;;
    *AOS-Sandbox-Full*) echo "aos-sandbox-full" ;;
    *agros-insite*)     echo "agros-insite" ;;
    *)                  echo "agents-os" ;;   # safe default
esac
```

The remote URL `git@github.com:WaldNimrod/SmallFarmsAgents.git` matches **none** of the explicit patterns and falls through to the `agents-os` default — the **same class of bug** that motivated ADR043 v1.2.0 §6 (TikTrack-originated MSGs landing in agents-os, incident 2026-04-25). The §6 rule itself is correct; the helper that implements client-side resolution is silently broken for at least one registered spoke.

ADR043 §6 names 8 spokes ("agents-os, tiktrack, eyalamit, hobbithome, microgreens, aos-sandbox-lean, aos-sandbox-full, agros-insite"). `smallfarmsagents` is registered (per `_aos/projects.yaml` on the hub — the spoke runs against it daily) but is missing from the helper's static map.

**Reproducer:**
```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
source _aos/lean-kit/modules/team-messaging/scripts/msg_preflight.sh
echo "$(msg_detect_project_id)"
# Output: agents-os    ← WRONG, expected: smallfarmsagents
```

**Impact:** Without explicit `AOS_PROJECT_ID=smallfarmsagents` override, every `msg_curl` from a SmallFarmsAgents session injects `X-Project-Id: agents-os` and routes the artifact into the hub repo. This is precisely the silent-cross-domain-leak bug §6 was created to prevent.

The static case statement is also a maintenance hazard: every new spoke registration requires editing this helper. The `/api/projects` endpoint (referenced in `/AOS_SendMail` Phase 0b) already serves the canonical list — the helper should consume it.

---

### F-MSG-04 — Auth model differs across endpoints with no canon documenting which is which (MEDIUM)

Empirical:
| Endpoint | `X-Actor-Team-Id` | `X-Actor-Api-Key` | Behaviour |
|----------|-------------------|-------------------|-----------|
| `GET /api/system/health` | not required | not required | 200 OK (canon §9) |
| `GET /api/messaging/inbox` | required | required (when `AOS_V3_ACTOR_KEYS` set) | 4xx without key |
| `POST /api/messaging/send` | required | required (when `AOS_V3_ACTOR_KEYS` set) | 4xx without key |
| `GET /api/prompts/generate` | required | **NOT required** (in our test) | 200 OK with team-id only |

This last row was verified in this session: a GET to `/api/prompts/generate` with only `X-Actor-Team-Id` (no `X-Actor-Api-Key`) returned a full prompt body. So either `/api/prompts/generate` is unauthenticated by design, or `X-Actor-Api-Key` enforcement is inconsistent across endpoints.

**Impact:** Agents have no canonical reference to know which endpoints they can call without provisioning. The skills (`/AOS_SendMail`, `/AOS_mail`, `/AOS_gov-update`) all assume full auth. ADR043 §9 lists endpoints but not the auth requirements per endpoint. Without an auth matrix, every agent learns by trial-and-error.

---

### F-MSG-05 — `msg_preflight.sh` has no Tier-0 self-healing for the most common Mac mistake (MEDIUM)

The most frequent spoke-onboarding mistake (observed multiple times in our session): a Mac session does NOT export `AOS_API_BASE` before sourcing `msg_preflight.sh`. Tier-3 fallback hits `127.0.0.1:8090` → HTTP 410 → user discovers the canonical URL only through the verbose log message.

The fix that ADR043 §5 Rule 4 documents — emit an actionable error pointing at `100.125.98.56:8090` — is correct but reactive. A self-healing approach: if Tier-3 default is hit AND Tailscale is online (detectable via `tailscale status` exit 0 or DNS lookup of `100.125.98.56`), promote the URL automatically and emit an info-level "promoted" message.

**Impact:** First-call failure on every Mac session that hasn't manually exported `AOS_API_BASE`. ADR043 §15.4 directs the user to add `export AOS_API_BASE=...` to `~/.zshrc` — but cowork sessions, fresh worktrees, sandbox containers, and shared agent environments don't always inherit this setting.

---

### F-MSG-06 — No canon for "branch reference" frontmatter on MSGs that point to non-main artifacts (MEDIUM)

The `msg_deliver_file` design (§4) ensures the MSG itself is on `origin/main`. But the artifacts the MSG points to — mandates, dispatches, specs, build reports — frequently live on the **working branch** (`claude/{worktree-name}` or `offline/...`) and have not been merged to main.

In this session: the WP004 dispatch MSG-HUB-20260510-001 had `next_step` "Pull branch claude/strange-mcnulty-651551 and execute the 10-step build sequence" — encoded **in the body prose**, not in machine-readable frontmatter. A receiving agent who scans MSGs by frontmatter alone has no canonical field telling them which branch to fetch.

There is no mention of `mandate_branch:` (or `artifact_branch:`, `source_branch:`) in:
- `MSG-HUB.template.md` frontmatter
- `HUB_MSG_SCHEMA.json`
- ADR043 §3 / §13

In its absence, every orchestrator improvises. Cross-engine receivers (team_190 / Cursor / Codex) often have to be told the branch in the activation prompt body — which works but is bespoke per WP.

**Impact:** MSGs pointing to in-flight artifacts on feature branches require manual human translation by the receiving session (or the orchestrator). The whole point of ADR043 §4 was to make MSG delivery branch-independent — the corollary should be that the MSG itself names the artifact's home branch when it is not `main`.

---

### F-MSG-07 — Cross-domain MSG delivery via file-fallback is unspecified (MEDIUM)

ADR043 §6 defines multi-domain routing for the **API path**: `X-Project-Id` resolves the target spoke and the API writes into that spoke's `_COMMUNICATION/`.

For the **file-fallback path** (§4), there is no equivalent. `msg_deliver_file` writes to the current repo's `_COMMUNICATION/` and pushes to that repo's `origin/main`. If a spoke session needs to file an MSG to the hub team_100 (this very GCR's situation!), there is no canon path for cross-domain delivery without API access.

In practice this session resolves it by the orchestrator manually writing to `/Users/nimrod/Documents/agents-os/_COMMUNICATION/team_100/MSG-HUB-...` — bypassing the canon.

**Impact:** Cross-domain GCRs and any other inter-spoke MSG depend on API uptime. When the API is reachable but the team is unprovisioned (F-MSG-01), there is no path at all — the file-fallback writes to the wrong repo.

---

### F-MSG-08 — Activation prompt API returns identity/governance only — no WP-specific context (MEDIUM)

`GET /api/prompts/generate?type=onboard_agent&team_id=team_10&wp_id=...&session_task=...` returns the team contract + AOS Iron Rules + "session task" (the literal string we passed in). It does NOT include:
- The WP's LOD400 ACs
- The locked-files list (per AC-16-style invariants)
- The mandate path
- The branch reference
- The acceptance criteria summary

For an L-GATE_B build dispatch — the most common AOS hand-off — the prompt is structurally right (governance + identity) but operationally insufficient. Every orchestrator augments it with WP-specific context, either inline (this session's TEAM_190_ACTIVATION_PROMPT_R2.md) or in a separate DISPATCH file that the prompt points to.

**Impact:** The "canonical short message displayed for copy-paste" goal that motivated this GCR cannot be achieved with the current `/api/prompts/generate` output for L-GATE_B / L-GATE_V dispatches. The prompt is governance-grade canon (good) but lacks the per-WP overlay (a gap).

The current workaround is to put the WP-specific overlay in the MSG body and instruct the receiver to read both. This works but doubles the source-of-truth for the receiving session.

---

### F-MSG-09 — Sequence-number computation for `MSG-HUB-YYYYMMDD-NNN` is ad-hoc (LOW)

The `NNN` suffix must be unique-per-day and the sender computes it client-side. There is no helper:
- `msg_preflight.sh` does not expose a `msg_next_id` function.
- `MSG-HUB.template.md` frontmatter says `id: MSG-HUB-YYYYMMDD-NNN` — placeholder.
- The API endpoint `POST /api/messaging/send` could compute it server-side, but skills currently pass a pre-computed id (file-fallback path).

In this session I `ls`'d the inbox folder and used `001` because none existed for the day. Race conditions between concurrent senders are possible.

**Impact:** Low. NNN collision is rare (concurrent sends from the same team to the same recipient on the same day). But the convention is leaky and would benefit from a single-line helper or server-side allocation in the API path.

---

## §5. Recommendations (R-MSG-01..09)

### R-MSG-01 (CRITICAL) — Provision API keys for all canonical teams; document the key delivery path

**Rationale:** Resolves F-MSG-01.

**Proposed change:**
1. Add a one-time admin operation: `POST /api/admin/actors/{team_id}/issue-key` (or similar) that generates a key, persists into `AOS_V3_ACTOR_KEYS`, and returns the key once (plaintext) to the caller.
2. Document the Mac-side retrieval workflow in ADR043 §15.4: either (a) `ssh waldhomeserver 'grep team_100 /data/projects/agents-os/core/.env | cut -d= -f2'`, (b) a CLI subcommand in the AOS Cowork toolkit, or (c) Apple Keychain lookup if keys are pre-distributed.
3. Pre-provision keys for the canonical agent teams: `team_00`, `team_100`, `team_10`, `team_50`, `team_90`, `team_110`, `team_190`, `team_191`, `team_99`, plus any spoke-specific aliases.
4. Add a `cli/aos-keymap` doctor command on Mac that probes `/api/actors/me` (or equivalent) for the current `AOS_ACTOR_TEAM_ID` and reports auth status.

**Impact:** every team's API path becomes usable. R-MSG-02 (next) becomes a defensive-only fallback rather than the routine path.

---

### R-MSG-02 (HIGH) — Refine §5 "no-fallback-on-4xx" rule to allow file-fallback on auth/provisioning errors

**Rationale:** Resolves F-MSG-02. The strict rule is correct for schema/header errors but misclassifies provisioning errors.

**Proposed change to ADR043 §5 step 3 / Rule 4 / new Rule 5:**

> **Rule 5 (auth-class fallback):** The following 4xx error codes MUST trigger file-fallback delivery (with a visible warning) rather than EXIT:
> - `ACTOR_KEY_NOT_CONFIGURED`
> - HTTP 401 / 403 (auth missing or rejected)
> - `MISSING_ACTOR_HEADER` only when caller is non-interactive — interactive sessions should still EXIT with the actionable "set X-Actor-Team-Id" message.
>
> All other 4xx codes (`UNKNOWN_PROJECT`, `INVALID_PAYLOAD`, schema errors) retain the strict no-fallback semantics: these are programmer errors, fallback would mask them.
>
> **Visible warning format:**
> ```
> ⚠ API auth unavailable ({code}) — falling back to file delivery.
>   Cause: server has no key for team_{id}. Admin: provision via POST /api/admin/actors/{id}/issue-key.
>   This MSG WILL be delivered to origin/main, but no DB record will be created.
> ```
> The non-API delivery state SHOULD be tracked in `_COMMUNICATION/_log/messages.log` for later reconciliation.

**Skill update:** `/AOS_SendMail` Phase 3 step 2 must be edited to honor the new rule.

---

### R-MSG-03 (HIGH) — Replace `msg_detect_project_id` static case statement with `/api/projects` dynamic resolution

**Rationale:** Resolves F-MSG-03. The current static map is incomplete and a maintenance hazard.

**Proposed change to `lean-kit/modules/team-messaging/scripts/msg_preflight.sh`:**

```bash
msg_detect_project_id() {
  if [ -n "${AOS_PROJECT_ID:-}" ]; then echo "$AOS_PROJECT_ID"; return 0; fi

  # Tier 1: cached lookup (avoid network on every call)
  local cache="${HOME}/.cache/aos/project_remote_map.tsv"
  local remote_url
  remote_url=$(git config --get remote.origin.url 2>/dev/null || echo "")
  if [ -n "$remote_url" ] && [ -r "$cache" ]; then
    local hit
    hit=$(awk -F'\t' -v u="$remote_url" '$2~u || u~$2 {print $1; exit}' "$cache")
    if [ -n "$hit" ]; then echo "$hit"; return 0; fi
  fi

  # Tier 2: fetch from API (refreshes cache)
  if [ -n "${AOS_API_BASE:-}" ] && curl -fsS --max-time 2 \
       "${AOS_API_BASE}/api/projects" -o /tmp/aos_projects.json 2>/dev/null; then
    mkdir -p "$(dirname "$cache")"
    jq -r '.projects[] | "\(.id)\t\(.git_remote)"' /tmp/aos_projects.json > "$cache" 2>/dev/null
    local hit
    hit=$(awk -F'\t' -v u="$remote_url" '$2~u || u~$2 {print $1; exit}' "$cache")
    if [ -n "$hit" ]; then echo "$hit"; return 0; fi
  fi

  # Tier 3: hardcoded fallback list (current behaviour) + smallfarmsagents
  case "$remote_url" in
    *agents-os*)         echo "agents-os" ;;
    *SmallFarmsAgents*|*smallfarmsagents*) echo "smallfarmsagents" ;;
    *TikTrack*|*tiktrack*) echo "tiktrack" ;;
    *EyalAmit*|*eyalamit*) echo "eyalamit" ;;
    *HobbitHome*|*hobbithome*) echo "hobbithome" ;;
    *Microgreens*|*microgreens*) echo "microgreens" ;;
    *AOS-Sandbox-Lean*) echo "aos-sandbox-lean" ;;
    *AOS-Sandbox-Full*) echo "aos-sandbox-full" ;;
    *agros-insite*)     echo "agros-insite" ;;
    *)
      echo "agents-os"   # last-resort default; emit warning
      [ "${_MSG_PREFLIGHT_VERBOSE:-0}" -eq 1 ] && \
        echo "⚠ msg_detect_project_id: unknown remote '$remote_url' — defaulting to 'agents-os' (likely wrong)" >&2
      ;;
  esac
}
```

**Side-effect:** the `/api/projects` endpoint (referenced in `/AOS_SendMail` Phase 0b) becomes the canonical SSoT for spoke registration. The static fallback list in the helper becomes a transition aid.

---

### R-MSG-04 (MEDIUM) — Document the per-endpoint auth matrix as a new ADR043 §16

**Rationale:** Resolves F-MSG-04.

**Proposed addition to ADR043 (new §16 — "Endpoint Auth Matrix"):**

| Endpoint | `X-Actor-Team-Id` | `X-Actor-Api-Key` | `X-Project-Id` | Notes |
|----------|-------------------|-------------------|----------------|-------|
| `GET /api/system/health` | — | — | — | Public probe, no auth |
| `GET /api/projects` | required | optional | — | Public spoke registry; key recommended in production |
| `POST /api/messaging/send` | required | **required when `AOS_V3_ACTOR_KEYS` set** | optional (default `agents-os`) | Multi-domain per §6 |
| `GET /api/messaging/inbox` | required | required | optional | Same |
| `POST /api/messaging/archive` | required | required | optional | Per §7 |
| `GET /api/prompts/generate` | required | optional (current behaviour — TBD whether by design) | — | Onboarding prompts |
| `POST /api/governance/sync` | required (`team_00` or `team_100` only) | required | optional | Per ADR040 / IR#12 |
| `POST /api/admin/actors/*` | required (`team_00` only) | required | — | Key provisioning per R-MSG-01 |

Also clarify: `/api/prompts/generate` SHOULD require `X-Actor-Api-Key` for parity (or be explicitly documented as a public-by-design endpoint). Decide and codify.

---

### R-MSG-05 (MEDIUM) — Add Tier-0 self-healing to `msg_preflight.sh` for Tailscale-detected waldhomeserver

**Rationale:** Resolves F-MSG-05.

**Proposed change to `_probe_api()` in `msg_preflight.sh`:**

After Tier-3 default is set but before the first probe:

```bash
# Tier-0 self-healing: if Tier-3 default is in use AND Tailscale is online,
# promote canonical waldhomeserver URL automatically.
if [ "$AOS_API_BASE" = "http://127.0.0.1:8090" ] && \
   ! [ -e /etc/aos-server-host ]; then     # marker file present on waldhomeserver only
  if command -v tailscale >/dev/null 2>&1 && \
     tailscale status >/dev/null 2>&1; then
    if curl -fsS --max-time 1 http://100.125.98.56:8090/api/system/health >/dev/null 2>&1; then
      AOS_API_BASE=http://100.125.98.56:8090
      [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ] && \
        echo "ℹ promoted AOS_API_BASE → ${AOS_API_BASE} (Tailscale + canonical health probe)"
    fi
  fi
fi
```

Cost: zero on waldhomeserver (marker file `/etc/aos-server-host` skips the block). On Mac, two extra fast checks (Tailscale presence + a 1-second health probe).

---

### R-MSG-06 (MEDIUM) — Add `mandate_branch` / `artifact_branch` frontmatter to the canonical MSG-HUB schema

**Rationale:** Resolves F-MSG-06.

**Proposed change to `MSG-HUB.template.md` frontmatter and `HUB_MSG_SCHEMA.json`:**

Add optional fields:

```yaml
mandate_branch:    # canonical branch where the artifact in `handoff_context_pointer` lives. OMIT if main.
artifact_paths:    # list of additional paths the receiving agent should fetch from `mandate_branch`. Optional.
```

**Semantics:**
- If `mandate_branch` is set, receiving session MUST run `git fetch origin {mandate_branch}` before reading `handoff_context_pointer`.
- If absent, default = `main`.
- `artifact_paths` is a YAML list (max 5 entries) of additional file paths on `mandate_branch` that the receiver should be aware of (e.g. spec, dispatch, build report).

**Update to ADR043 §13** (continuation prompt standard):
> Add `mandate_branch` as an OPTIONAL field on all formal artifacts. When the artifact body lives on a non-main branch, this field MUST be set. Receiving agents MUST honor the branch reference when locating the artifact.

**Implications for `/AOS_mail`:** when reading an MSG with `mandate_branch != main`, the skill should auto-emit:
```
ℹ this MSG references branch '{mandate_branch}' — fetch with: git fetch origin {mandate_branch}
```

---

### R-MSG-07 (MEDIUM) — Specify cross-domain MSG delivery for the file-fallback path

**Rationale:** Resolves F-MSG-07.

**Proposed change to ADR043 §6 (new §6.1 — "Cross-domain file-fallback delivery"):**

When a spoke session needs to deliver an MSG to a different domain (typically a spoke→hub GCR), and the API path is unavailable:

1. The sender writes the MSG to its own `_COMMUNICATION/{to_team}/MSG-HUB-{date}-{nnn}.md` (audit trail in spoke).
2. The sender ALSO writes a copy to the target domain's local clone path:
   `{target_domain.local_path}/_COMMUNICATION/{to_team}/MSG-HUB-{date}-{nnn}.md`
   (resolved via `/api/projects` or the static spoke registry).
3. The sender invokes a new helper `msg_deliver_file_cross_domain <spoke_msg_path> <target_domain_msg_path>` that commits + pushes BOTH copies to BOTH `origin/main` repos.
4. Receiving session in the target domain sees the MSG via standard inbox scan.

**Caveat:** this requires both repos to be locally cloned and writable. For environments where this is not the case (e.g. a sandbox), the sender MUST fall through to API-only and fail loudly if the API is unauthenticated.

**Helper signature:**
```bash
msg_deliver_file_cross_domain() {
  local local_msg="$1"   # spoke audit copy
  local remote_root="$2" # target domain's local repo root
  local remote_msg
  remote_msg="${remote_root}/$(echo "$local_msg" | sed -E 's,^.*/_COMMUNICATION/,_COMMUNICATION/,')"
  cp "$local_msg" "$remote_msg"
  msg_deliver_file "$local_msg"      # local spoke push
  ( cd "$remote_root" && msg_deliver_file "${remote_msg#${remote_root}/}" )  # target push
}
```

---

### R-MSG-08 (MEDIUM) — Extend `/api/prompts/generate` with WP-specific overlay parameters

**Rationale:** Resolves F-MSG-08.

**Proposed extension to the API:**

```
GET /api/prompts/generate
  ?type=onboard_agent
  &team_id=team_10
  &wp_id=SFA-S003-P001-WP004
  &session_task=L-GATE_B build
  &mandate_path=_COMMUNICATION/TEAM_100/SFA-S003-P001-WP004/DISPATCH_sfa_build_2026-05-10_v1.0.0.md   ← NEW
  &mandate_branch=claude/strange-mcnulty-651551                                                       ← NEW
  &spec_path=_aos/work_packages/S003/SFA-S003-P001-WP004/LOD400_spec.md                              ← NEW
  &locked_files_glob=_aos/**,*.lock                                                                  ← NEW
```

Server-side: if these params are set, the response prompt template injects a **§"WP context"** block at the top with the values, BEFORE the team identity / governance section. The receiving agent reads this first.

**Backward compatibility:** all new params optional; current callers continue to work unchanged.

**Implementation note:** the prompt rendering is template-driven — adding placeholder substitutions is mechanical.

---

### R-MSG-09 (LOW) — Add `msg_next_id` helper to `msg_preflight.sh`

**Rationale:** Resolves F-MSG-09.

**Proposed addition:**

```bash
msg_next_id() {
  local team_id="${1:-${AOS_ACTOR_TEAM_ID:-}}"
  local target_team_id="${2:-$team_id}"
  local date_stamp="${3:-$(date -u +%Y%m%d)}"
  local repo_root
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  local inbox_dir="${repo_root}/_COMMUNICATION/${target_team_id}"
  local last
  last=$(ls "${inbox_dir}/MSG-HUB-${date_stamp}-"*.md 2>/dev/null \
         | sed -E "s,.*/MSG-HUB-${date_stamp}-([0-9]+)\.md,\1," \
         | sort -n | tail -1)
  printf "MSG-HUB-%s-%03d\n" "$date_stamp" "$(( (last:-0) + 1 ))"
}
```

Usage:
```bash
msg_id=$(msg_next_id team_100 team_10)   # → MSG-HUB-20260510-002
```

The API path could expose the same logic via a `POST /api/messaging/next-id` endpoint, but the local helper covers the file-fallback path which is the more common need.

---

## §6. Test plan (per-recommendation acceptance evidence)

| Recommendation | Acceptance check |
|----------------|------------------|
| R-MSG-01 | `curl -H "X-Actor-Team-Id: team_100" -H "X-Actor-Api-Key: ..." {API}/api/messaging/send -d ...` returns 200 from a fresh Mac session that has run only the documented onboarding step. |
| R-MSG-02 | `/AOS_SendMail` invocation with deliberate auth-class 4xx (e.g. `team_999` with no key) emits warning + delivers via file-fallback + creates audit log entry. Same invocation with malformed payload (e.g. missing `subject`) still EXITs without fallback. |
| R-MSG-03 | `cd ~/Documents/SmallFarmsAgents && msg_detect_project_id` returns `smallfarmsagents`. Same in TikTrack, HobbitHome, Microgreens. Adding a new spoke + restarting the API → `msg_detect_project_id` resolves it without code change (cache refresh). |
| R-MSG-04 | ADR043 §16 added; `validate_aos.sh` Check (new) confirms presence of the matrix. Each row has a smoke test in `tests/api/test_endpoint_auth_matrix.py`. |
| R-MSG-05 | Fresh Mac session without `AOS_API_BASE` exported: sourcing `msg_preflight.sh --verbose` emits `ℹ promoted AOS_API_BASE → http://100.125.98.56:8090` and proceeds via API path. |
| R-MSG-06 | New MSG written with `mandate_branch: claude/foo` is delivered; receiver running `/AOS_mail` sees the branch hint and the suggested `git fetch` command. |
| R-MSG-07 | Spoke session writes a GCR with cross-domain delivery; the GCR appears on both `origin/main` of the spoke and `origin/main` of `agents-os` after one helper invocation. |
| R-MSG-08 | `GET /api/prompts/generate?...&mandate_path=...&mandate_branch=...` returns a prompt with a top-level §"WP context" block naming both. The block is omitted when those params are absent (backward compat). |
| R-MSG-09 | `msg_next_id team_100 team_10` returns a correctly-formatted, sequenced id. Two concurrent invocations within the same second produce different ids (filesystem `ls` is stable per-call). |

---

## §7. Impact assessment

| Question | Answer |
|----------|--------|
| Affects other teams | YES — every team that uses `/AOS_SendMail`, `/AOS_mail`, or the `/api/messaging/*` endpoints. R-MSG-01 specifically requires team_00 + admin action. |
| Requires context refresh broadcast | YES — after `/AOS_gov-update` propagation, every active session should pull updated `_aos/lean-kit/modules/team-messaging/scripts/msg_preflight.sh` and `.claude/commands/AOS_SendMail.md`. |
| Backward compatible | MOSTLY YES. R-MSG-02 (relaxed 4xx fallback) is a behaviour change but only opens a new path that was previously blocked — no existing path changes. R-MSG-06 (new optional frontmatter) is additive. R-MSG-03 (helper rewrite) preserves the static-fallback behaviour as a tier. R-MSG-08 adds new optional params. R-MSG-01 is purely additive (provisioning). The only non-back-compat change is R-MSG-04's documented decision on `/api/prompts/generate` auth — explicit decision required. |
| Migration path | Per-recommendation; most are fully forward (no migration). R-MSG-01 requires a one-time admin step per team. R-MSG-03 requires updating `msg_preflight.sh` snapshots in every spoke (`/AOS_gov-update` handles this). |
| Risks | LOW. The biggest risk is that R-MSG-02's relaxed fallback could mask future genuine 4xx-class auth bugs. Mitigation: the visible warning (per the proposed text) is mandatory, and the audit log records the bypass. |

---

## §8. Precise prompt for AOS team_100

> Open work package `AOS-V4.2-WP-MSG-AUTH-AND-ROUTING-FIX`. Author LOD400 spec covering the 9 recommendations R-MSG-01..09 in this GCR. Effort: NORMAL (mostly mechanical fixes; the one design decision is whether `/api/prompts/generate` should require `X-Actor-Api-Key` — that's a single-line approval at L-GATE_S).
>
> Build sequence (suggested order; team_100 may re-arrange):
> 1. R-MSG-04 (auth matrix doc) — unblocks the rest by clarifying intent.
> 2. R-MSG-01 (key provisioning + admin endpoint).
> 3. R-MSG-02 (relaxed §5 Rule 5).
> 4. R-MSG-03 (`msg_detect_project_id` rewrite).
> 5. R-MSG-05 (Tier-0 self-healing).
> 6. R-MSG-06 (`mandate_branch` frontmatter + schema update).
> 7. R-MSG-07 (cross-domain file-fallback helper).
> 8. R-MSG-08 (`/api/prompts/generate` overlay params).
> 9. R-MSG-09 (`msg_next_id` helper).
>
> Bump ADR043 → v1.5.0 with the §16 Endpoint Auth Matrix and §6.1 Cross-Domain File-Fallback. Update changelog.
>
> Validate via team_190 cross-engine (Iron Rule #1) at L-GATE_V. After PASS, run `/AOS_gov-update` to propagate to all spokes. Notify originating spoke (this GCR's `from`) via `MSG-team100-to-team100-AOS-V4.2-MSG-INFRA-COMPLETE`.

---

## §9. Approval checklist

- [ ] team_100 (agents-os) reviewed
- [ ] team_00 approved
- [ ] WP `AOS-V4.2-WP-MSG-AUTH-AND-ROUTING-FIX` opened
- [ ] LOD400 authored, L-GATE_S PASS
- [ ] Build complete, L-GATE_V PASS
- [ ] `/AOS_gov-update` executed; all spokes synced
- [ ] Smallfarmsagents (originating spoke) notified

---

## §10. Empirical session evidence (for traceability)

This GCR is supported by the working transcript of session `claude/strange-mcnulty-651551` (HEAD `ccdf965` at filing). Specific evidence pointers:

- `git log --oneline` from `feee36c..ccdf965` — the WP004 round-trip that exercised the messaging stack.
- `_COMMUNICATION/team_10/MSG-HUB-20260510-001.md` — successful file-fallback delivery (canonical helper worked).
- `msg_curl POST /api/messaging/send` 4xx response captured at 17:47Z — F-MSG-01 reproducer.
- `msg_detect_project_id` returning `agents-os` for `SmallFarmsAgents` clone — F-MSG-03 reproducer.

The GCR author is Claude Opus 4.7 acting as `team_100@smallfarmsagents` (engine override per session activation; declared identity = Claude Sonnet 4.6).

---

*GCR | AOS messaging infrastructure hardening | filed 2026-05-10 | smallfarmsagents → agents-os | urgency HIGH | recommends new WP AOS-V4.2-WP-MSG-AUTH-AND-ROUTING-FIX*
