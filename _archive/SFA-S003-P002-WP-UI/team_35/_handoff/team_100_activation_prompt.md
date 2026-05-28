# Team_100 Activation — SFA Public Web UI (sfa.nimrod.bio)

> **Copy this prompt into a fresh team_100 (AOS Chief System Architect) session.**
> It activates team_100 to register the work package, file a roadmap entry, and
> route the design handoff to team_110 for LOD200/LOD400 spec authoring.

---

## You are team_100 (AOS Chief System Architect)

A new design handoff has arrived from **team_35 (design — Claude Sonnet 4.6)**
for a follow-up work package in the `SFA-S003-P002` program:

> **`SFA-S003-P002-WP-UI` — SFA standalone public web UI at `sfa.nimrod.bio`**
> Build the public-facing SFA web application as a new **Flask Blueprint**
> inside the existing `organic_market_agent` codebase, served at
> `sfa.nimrod.bio` without WordPress chrome. Mobile-first; desktop is an
> additive layout. Replaces the legacy nimrod.bio Elementor + mu-plugin
> embedding pattern (which keeps working in parallel until team_00 retires it).

The package is the design layer — not the spec. team_100 owns roadmap
registration and routing; team_110 owns LOD200/LOD400 spec authoring.

---

## Where the package lives

```
_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/handoff_LOD300_v1.2.0/
├── README.md                          ← orient here
├── HANDOFF_LOD300.md                  architecture + mapping to existing Flask code
├── DESIGN_TOKENS.md                   canonical CSS tokens
├── COMPONENTS.md                      catalog of every UI component with DOM
├── TEMPLATES.md                       Jinja2 page templates + routing map
├── MODULES_REGISTRY.yaml              SOURCE OF TRUTH — 8 modules + 5 tiers
├── IMPLEMENTATION_PLAN.md             10-phase plan, ~20h to first deploy
├── team_110_activation_prompt.md      drop into the next team_110 session
└── design/                            live design canvas (open in browser)
```

team_35 designed the system as **platform-neutral**. The architecture mapping
in `HANDOFF_LOD300.md` is Flask + Jinja2 + SQLAlchemy + nginx + gunicorn —
matching the existing codebase. The new Blueprint is `organic_market_agent.sfa_app/`,
parallel to the existing `admin/` (port 5001) and `crop_book/` (Blueprint in admin).

---

## Verified codebase context

Read for orientation before routing:

| File | What it tells you |
|------|-------------------|
| `organic_market_agent/admin/__init__.py` | `create_app()` factory pattern — sfa_app must mirror but auth-less |
| `organic_market_agent/crop_book/views.py` | Existing `crop_book_bp` Blueprint, 3 routes, semantic SSoT for filter logic — sfa_app reuses |
| `organic_market_agent/crop_book/models.py` | `Crop`, `CropVariety`, `CropVarietySourceValue` — read-only access |
| `organic_market_agent/publisher/` | Static JSON publisher (for nimrod.bio WP-embed) — NOT touched |
| `wordpress/mu-plugins/sfagent-*.php` | Legacy WP-embed pattern — NOT touched, keep running |
| `_aos/roadmap.yaml` (lines 791+) | `SFA-S003-P002-WP-B*` family already closed (data foundation). WP-UI is new sibling. |

---

## Your job in this session — 4 steps

### Step 1 — Roadmap registration

Per Iron Rule #4 (single-writer roadmap, ADR034 R2), team_100 is the only
team that may add a new WP to `_aos/roadmap.yaml`. Add:

```yaml
- id: SFA-S003-P002-WP-UI
  label: "SFA public web UI — sfa.nimrod.bio (Flask Blueprint, standalone shell)"
  status: PLANNED
  track: A
  effort: LARGE
  current_lean_gate: L-GATE_E
  lod_status: LOD100
  created_at: "2026-05-26"
  milestone_ref: "S003"
  depends_on: ["SFA-S003-P002-WP-B1"]                    # data foundation
  brief_ref: "_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/handoff_LOD300_v1.2.0/HANDOFF_LOD300.md"
  spec_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD200_spec.md"   # to be authored by team_110
  notes: "Public-facing SFA web app at sfa.nimrod.bio. New Flask Blueprint
    organic_market_agent.sfa_app/ (gunicorn:5002). Mobile-first. 14 routes,
    8 modules registry, 3-tier UX language. Design LOD300 delivered by
    team_35 2026-05-26. team_110 to author LOD200/LOD400."
  profile: L0
```

Use the API per Iron Rule #7 / ADR034 R2 if the AOS v3 DB is online; otherwise
use ADR034 R9 direct-edit (this is an L2 spoke WP — `SNNN-PNNN-WP*` format).

### Step 2 — File the team_110 activation handoff

Copy the design package into `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-UI/` and file a handoff
MSG mirroring `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/HANDOFF_v1.0.0.md`:

```
_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-UI/
├── HANDOFF_v1.0.0.md                  team_100 → team_110 (this MSG)
├── ACTIVATION_PROMPT.md               copy of team_110_activation_prompt.md
└── (design package referenced by path, not duplicated)
```

The MSG follows ADR043 v1.5.0 schema and references:
- `expects_response: true`
- `handoff_to: team_110`
- `next_step: "Author LOD200 + LOD400 specs at _aos/work_packages/S003/SFA-S003-P002-WP-UI/"`

### Step 3 — GCR pre-analysis (optional but recommended)

Identify locked files that the build will touch:

| File | Status | Likely change | GCR? |
|------|--------|---------------|------|
| `organic_market_agent/models/*` | LOD500_LOCKED (WP-A, WP-B1) | Read-only | **no** |
| `organic_market_agent/crop_book/views.py` | LOD500_LOCKED (WP003) | Read-only — reuses filter logic | **no** |
| `organic_market_agent/crop_book/models.py` | LOD500_LOCKED (WP-B1) | Read-only | **no** |
| `organic_market_agent/admin/__init__.py` | active | Possibly mount `sfa_app` as sub-app | **possible — flag for team_110** |
| New: `organic_market_agent/sfa_app/*` | new tree | Authored fresh | **no** |
| New table: `community_contributions` | migration 049 | Additive | **no GCR (additive)** |

If team_110 finds a need to extend `CropVariety` with a new field (e.g. `taste_rating`
shown in design CB5), that becomes a GCR_1 for `models.py`. Flag at LOD200.

### Step 4 — Advisory routing to team_00

The design package contains 8 open questions (§6 of HANDOFF_LOD300.md). Of those,
4 are **strategic** and require team_00 advisory before LOD400 lock:

| Q | Topic | team_00 input needed |
|---|-------|---------------------|
| Q1 | Sub-domain `sfa.nimrod.bio` final? | confirm |
| Q5 | Variety `taste_rating` field — add via GCR? | yes/no |
| Q7 | Calculator (β) scope — WP-UI1 or split WP-UI3? | scope decision |
| Q8 | WhatsApp number `054-7776770` confirmation | placeholder yes/no |

File: `_COMMUNICATION/TEAM_00/SFA-S003-P002-WP-UI/ADVISORY_REQUEST_v1.0.0.md`

---

## Iron-rule reminders

- **Iron Rule #4** — single-writer roadmap. team_100 only.
- **Iron Rule #1** — cross-engine validation. team_100 routes; team_110 specs;
  team_10/sub-agent builds; team_190 validates. No collapsing.
- **Iron Rule #6** — artifact communication. All inter-team via `_COMMUNICATION/`.
- **ADR045** — if team_110 receives `execution_authority: full`, the mandate
  delegates roadmap closure steps. Decide here whether to grant it or hold default.
- **GCR_3** — any modification to existing `crop_book/views.py` or
  `crop_book/templates/*` requires a formal GCR. The design avoids this by
  building a separate `sfa_app` Blueprint that **calls** the existing models.

---

## Boundaries

- DO write to `_COMMUNICATION/team_100/`, `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-UI/`, and `_aos/roadmap.yaml`.
- DO NOT author the LOD200/LOD400 specs — that's team_110.
- DO NOT touch the design files — that's team_35 (file a MSG if anything is unclear).
- DO NOT modify locked files under `crop_book/`, `publisher/`, `models/`.

---

## Done criteria for this session

- [ ] WP `SFA-S003-P002-WP-UI` registered in `_aos/roadmap.yaml` with `status: PLANNED`, `lod_status: LOD100`
- [ ] Design package copied to `_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/handoff_LOD300_v1.2.0/`
- [ ] `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-UI/HANDOFF_v1.0.0.md` filed (team_100 → team_110)
- [ ] `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-UI/ACTIVATION_PROMPT.md` populated from the design package
- [ ] team_00 advisory request filed for 4 strategic questions (Q1, Q5, Q7, Q8)
- [ ] (optional) GCR pre-analysis filed at `_COMMUNICATION/team_100/SFA-S003-P002-WP-UI/GCR_ANALYSIS_v1.0.0.md`
- [ ] Roadmap commit pushed (`AOS_ACTOR_TEAM_ID=team_100`) and DB-sync run if `core/governance/` modified
- [ ] Session does NOT start LOD200 authoring — that's the next team_110 session

---

## Done

End your team_100 session here. The next session is team_110, activated by the
ACTIVATION_PROMPT you just filed.

---

*Activation prompt issued 2026-05-26 by team_35 (design — Claude Sonnet 4.6).*
*Routes design LOD300 → team_100 → team_110 per ADR045 / Iron Rule #1.*
