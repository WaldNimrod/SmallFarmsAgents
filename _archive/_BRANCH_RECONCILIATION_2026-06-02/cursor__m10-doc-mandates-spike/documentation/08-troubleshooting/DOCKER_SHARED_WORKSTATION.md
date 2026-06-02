---
standard: 11.2
id: multi-project-docker
title: Multi-Project Docker Workstation (SmallFarmsAgents instance)
version: 1.0.0
date: 2026-04-09
instance_of: agents-os/lean-kit/modules/standards-conventions/MULTI_PROJECT_DOCKER_WORKSTATION_v1.0.0.md
---

# SmallFarmsAgents — Multi-Project Docker Workstation (AOS Standard 11.2)

This file is the **project-local instance** required by **AOS Standard 11.2**. The machine-readable canonical source lives in the **agents-os** repository and must be kept in lockstep when the registry changes:

**Canonical (do not fork policy):** `lean-kit/modules/standards-conventions/MULTI_PROJECT_DOCKER_WORKSTATION_v1.0.0.md`  
(typically checked out as `../agents-os/lean-kit/...` next to this repo on a developer workstation)

If the sections below diverge from that file, **the agents-os canonical file wins**; update this instance in the same change set as any registry edit.

---

## Policy (canonical — AOS Standard 11.2)

Every repository that runs local Docker services **must** publish **fixed, version-controlled host ports** for those services.

- Port values are defined in committed files (`docker-compose.yml`, `.env.example`, CLI defaults).
- Each project documents its ports in one canonical place: a table in their troubleshooting doc or README, plus their `.env.example`.
- **Port assignments are registered in the agents-os canonical document.** No new port may be used without updating the registry there.
- Ad-hoc port changes without updating the docs break teammates, CI, and QA evidence.

## Port Priority Rule (canonical)

**TikTrack is the primary project — its port assignments are immutable.**  
All other projects yield when a conflict with TikTrack exists.  
For conflicts between non-TikTrack projects: the established project keeps its port; the newer project re-assigns.

## AOS Multi-Project Port Registry (canonical)

All known port assignments for AOS-managed projects. **This table is the single source of truth** (reproduced from v1.0.0; verify against agents-os if in doubt).

| Project | Service | Host Port | Container Name | Notes |
|---------|---------|-----------|----------------|-------|
| TikTrack | PostgreSQL | **5432** | `tiktrack-postgres-dev` | IMMUTABLE (primary project) |
| TikTrack | API (FastAPI) | **8082** | — | IMMUTABLE |
| TikTrack | Frontend (Vite) | **8080** | — | IMMUTABLE |
| TikTrack + agents-os | AOS API (uvicorn) | **8090** | — | Shared by design — same engine |
| agents-os | PostgreSQL | **5434** | `aos-postgres-dev` | Moved from 5432 (TikTrack conflict, 2026-04-09) |
| agents-os | Dashboard static | **8099** | — | Clean |
| SmallFarmsAgents | PostgreSQL | **5433** | `oma-postgres` | Clean |
| SmallFarmsAgents | Admin UI (Flask) | **5001** | — | Clean |
| SmallFarmsAgents | Static viewer | **8081** | — | Moved from 8080 (TikTrack conflict, 2026-04-09) |

**Reserved / do not use:** 5432 (TikTrack PG), 8080 (TikTrack frontend), 8082 (TikTrack API), 8090 (AOS API).

---

## SmallFarmsAgents — implementation mapping (this repository)

| Requirement (AOS § Per-Project) | Location in this repo |
|-----------------------------------|------------------------|
| `docker-compose.yml` with explicit `ports:` and unique `container_name` | [`docker-compose.yml`](../../docker-compose.yml) — project name `smallfarmsagents` (Compose `name:`) |
| `.env.example` with canonical `DATABASE_URL` | [`.env.example`](../../.env.example) |
| Port table + troubleshooting | **This file** |
| `COMPOSE_PROJECT_NAME` / Compose project name | [`docker-compose.yml`](../../docker-compose.yml) top-level `name: smallfarmsagents` |

### This project’s connection string (reference)

`postgresql://oma:oma@127.0.0.1:5433/organic_market_agent`

### CLI / scripts defaults

| Service | Host port | Where defined |
|---------|-----------|---------------|
| PostgreSQL (Docker) | **5433** | `docker-compose.yml`, `scripts/docker_postgres.sh` |
| Admin UI | **5001** | `run_admin` default, `scripts/admin_server.sh` |
| Public viewer | **8081** | `run_viewer` default, `scripts/viewer_server.sh` |

---

## Workstation drift (common)

If `docker ps` shows **`tiktrack-postgres-dev` bound to `0.0.0.0:5433`**, that **conflicts** with SmallFarmsAgents (**5433**) and **does not match** the registry above (TikTrack PostgreSQL is registered on **5432**, not 5433). Fix TikTrack’s compose to use **5432** (or stop that container when working on SmallFarmsAgents). Likewise, any container using **8081** for a non-SFA service blocks this repo’s static viewer.

---

## Diagnostics (canonical)

Check who holds a port:

```bash
lsof -nP -iTCP:<port> -sTCP:LISTEN
```

List all running containers and their port bindings:

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Check for container name collisions:

```bash
docker ps -a --format "{{.Names}}" | sort
```

Quick probe for this repo’s three local ports:

```bash
./scripts/check_canonical_local_ports.sh
```

---

## This repository — additional troubleshooting

### Host port binding

Only **one** listener can own a host port. Symptoms: `connection refused`, “port is already allocated”, or wrong schema/data.

### `DATABASE_URL` mismatch

Align `.env` with **5433** and `organic_market_agent` when using this repo’s compose file.

### Named volumes

`oma_postgres_data` persists data. Recreating the container does not reset data unless the volume is removed.

### `pg_hba.conf` / client seen as bridge IP

Some setups show `no pg_hba.conf entry for host "172.23.x.x"` when connecting from the host to a published port. Confirm what owns **5433** (`docker ps`, `lsof`). If it is `oma-postgres`, verify from inside the container:

```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -c "SELECT 1"
```

If that works but host connections fail, treat as local Docker networking / `pg_hba` — coordinate with Team 20.

---

## Further reading (canonical document only)

Conflict resolution, registering new projects, and full governance text: **`MULTI_PROJECT_DOCKER_WORKSTATION_v1.0.0.md`** in agents-os `lean-kit/modules/standards-conventions/`.

---

*SmallFarmsAgents instance | AOS Standard 11.2 | aligns with MULTI_PROJECT_DOCKER_WORKSTATION v1.0.0*
