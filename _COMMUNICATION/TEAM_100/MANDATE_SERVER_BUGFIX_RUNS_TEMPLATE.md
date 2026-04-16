# MANDATE — SFA Server Bug Fix: /runs Jinja2 Template Error
**Date:** 2026-04-10
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Priority:** High
**Type:** Bug Fix + Server Deployment

---

## 1. Context

SmallFarmsAgents is now deployed and running on our home staging server **waldhomeserver**. All services are operational except one route that returns HTTP 500.

### Server Details
| Key | Value |
|-----|-------|
| Hostname | waldhomeserver |
| OS | Ubuntu 24.04.4 LTS |
| IP (LAN) | 10.100.102.2 |
| IP (Tailscale) | 100.125.98.56 |
| User | nimrodw |
| SFA path | /data/projects/smallfarmsagents |
| SFA service | `sudo systemctl start/stop/status sfa-admin` |
| SFA port | 5001 (Flask Admin) |
| SFA DB | PostgreSQL 15 on port 5433 (Docker: oma-postgres) |
| SFA venv | /data/projects/smallfarmsagents/.venv |

---

## 2. Bug Description

**Route:** `/runs`
**HTTP Status:** 500 Internal Server Error
**Error:** Jinja2 `TemplateSyntaxError`

```
jinja2.exceptions.TemplateSyntaxError: Encountered unknown tag 'else'.
Jinja was looking for 'endblock'.
```

**Root Cause:** The template `admin_ui/templates/runs.html` (or whichever template renders `/runs`) has an `{% else %}` tag inside a `{% block %}` that is not properly enclosed in an `{% if %}` block. Jinja2 interprets the `{% else %}` as an unknown tag because it expects `{% endblock %}` first.

**Example of the problem pattern:**
```jinja
{% block content %}
  {% if runs %}
    ... render runs ...
  {% else %}          <-- ERROR: Jinja thinks this closes the block
    No runs found.
  {% endif %}
{% endblock %}
```

This pattern should work, so the actual issue is likely a **missing `{% if %}` or mismatched `{% endif %}`** somewhere earlier in the template that causes Jinja's parser to get confused about nesting.

---

## 3. Fix Instructions

1. Open the template that renders `/runs` (likely `admin_ui/templates/runs.html`)
2. Check all `{% if %}` / `{% else %}` / `{% endif %}` blocks for proper nesting
3. Ensure every `{% if %}` has a matching `{% endif %}` BEFORE `{% endblock %}`
4. Check for any `{% for %}` / `{% endfor %}` mismatches too
5. Test locally: `flask --app admin_ui.app run --port 5001` and visit `/runs`

---

## 4. Server Deployment After Fix

### Option A: Push to GitHub, pull on server
```bash
# After fix is committed and pushed:
# SSH to server:
ssh nimrodw@10.100.102.2

# Or via Tailscale:
ssh nimrodw@100.125.98.56

cd /data/projects/smallfarmsagents
git pull
sudo systemctl restart sfa-admin

# Verify:
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/runs
# Expected: 200
```

### Option B: Communicate with server agent
The server runs a Claude Code agent (Team 61 — Server Operations).
Communication is via file-based messaging:

**From Mac:**
```bash
# Write a message to the server agent
# Place file in: ~/Documents/_agent_comm/outbox/MSG-YYYYMMDD-NNN.md
# Push: scp <file> nimrodw@10.100.102.2:~/agent_comm/inbox/
```

**On server:** The agent checks `/home/nimrodw/agent_comm/inbox/` for tasks.

**For this specific fix:** After pushing to GitHub, send a message to the server agent:
```markdown
## Subject
SFA: Pull latest and restart — /runs template fix

## Body
git pull in /data/projects/smallfarmsagents and restart sfa-admin.
Verify: curl http://127.0.0.1:5001/runs returns 200.
```

---

## 5. Verification Checklist

- [ ] `/runs` returns HTTP 200 (not 500)
- [ ] Runs page renders correctly in browser
- [ ] No other routes broken (spot check: `/`, `/products`, `/sources`)
- [ ] Fix committed to GitHub with descriptive message
- [ ] Server updated via `git pull` + `systemctl restart sfa-admin`
- [ ] Server agent confirms fix is live

---

## 6. Additional Server Info

**All 49 routes work except `/runs`.** The admin UI is fully functional:
- 67 products, 223 aliases, 20 sources in DB
- SMTP configured (agent@nimrod.bio via smtp.inbox.co.il:587)
- FTP configured (ftp.s887.upress.link)
- Playwright + Chromium installed
- Scheduler cron at 06:00 UTC daily

**Do not modify server .env or infrastructure.** Only application code changes via git.

---

*Mandate issued by Team 100 (Architecture) | 2026-04-10*
