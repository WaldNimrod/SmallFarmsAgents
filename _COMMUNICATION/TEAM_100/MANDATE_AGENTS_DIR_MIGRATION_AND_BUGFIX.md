# MANDATE — SFA: /agents/ Migration + /runs Bug Fix
**Date:** 2026-04-10
**From:** Team 100 (Architecture) via Nimrod
**To:** Team 10 (Feature Dev)
**Priority:** High
**Type:** Bug Fix + FTP Migration

---

## 1. Architecture Decision: /agents/ Root Directory

**Nimrod has decided:** All AOS-managed projects that publish to nimrod.bio will upload to a shared `/agents/` directory with a `.htaccess` that bypasses WordPress URL routing.

```
nimrod.bio/agents/
  .htaccess              ← RewriteEngine Off
  sfa/                   ← SmallFarmsAgents output
    assets/
    data/
    index.html
  newsletter/            ← Famely Neuslettr
  tiktrack/              ← Future
```

### SFA Migration Required

**Current:** SFA uploads to `wp-content/uploads/market/`
**New:** SFA must upload to `/agents/sfa/`

This means:
1. Update FTP upload path in the SFA code (wherever `wp-content/uploads/market/` is referenced)
2. The WordPress page (ID 91325, "MyFarmAgents — Market Report") has **53 hardcoded references** to `wp-content/uploads/market/` paths (icons, data files). These need to change to `/agents/sfa/`.

### New FTP Credentials

A new FTP account has been configured on the server for the `/agents/` root:

**Environment variables (already configured on server):**
```
WP_FTP_HOST=ftp.s887.upress.link
WP_FTP_USER=AgentsRoot@nimrod.bio
WP_FTP_PASS=<configured on server, not in git>
WP_FTP_ROOT=/agents/sfa/
```

**Important:** The existing FTPS credentials (`FTPS_HOST` etc.) may still be needed for backward compatibility during migration. The new `WP_FTP_*` vars give access to the WordPress root, allowing creation of `/agents/` and `.htaccess`.

### .htaccess Setup

Before SFA can serve from `/agents/sfa/`, someone needs to create `/agents/.htaccess` on the WordPress server:

```apache
# Bypass WordPress for /agents/ directory
RewriteEngine Off
```

This can be done via FTP using the new `WP_FTP_*` credentials. The server team (Team 61) can do this if instructed.

---

## 2. Bug Fix: /runs Jinja2 Template Error

**Route:** `/runs`
**HTTP Status:** 500 Internal Server Error
**Error:** `jinja2.exceptions.TemplateSyntaxError: Encountered unknown tag 'else'. Jinja was looking for 'endblock'.`

**Root Cause:** Template `runs.html` has a mismatched `{% if %}` / `{% else %}` / `{% endif %}` nesting inside a `{% block %}`.

**Fix:** Check all block/if nesting in the runs template. Every `{% if %}` needs a matching `{% endif %}` before `{% endblock %}`.

---

## 3. Server Details

| Key | Value |
|-----|-------|
| Hostname | waldhomeserver |
| IP (LAN) | 10.100.102.2 |
| IP (Tailscale) | 100.125.98.56 |
| User | nimrodw |
| SFA path | /data/projects/smallfarmsagents |
| SFA port | 5001 (Flask Admin) |
| SFA DB | PostgreSQL 15, port 5433, container: oma-postgres |

---

## 4. How to Deploy & Test on Server

### After pushing fixes to GitHub:

**Option A — Tell the server agent directly:**

Write a message file and push it:
```bash
cat > /tmp/deploy-msg.md << 'EOF'
# Agent Communication Message
---
id: MSG-YYYYMMDD-NNN
from: mac
to: server
date: YYYY-MM-DD HH:MM
type: task
priority: high
expects_response: true
---

## Subject
SFA: Pull latest and redeploy

## Body
1. cd /data/projects/smallfarmsagents && git pull
2. source .venv/bin/activate && pip install -e ".[dev]"
3. sudo systemctl restart sfa-admin
4. Verify: curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/runs (expect 200)
5. Test FTP upload to /agents/sfa/ using WP_FTP_* credentials from .env
6. Report results
EOF

scp /tmp/deploy-msg.md nimrodw@10.100.102.2:~/agent_comm/inbox/
```

**Option B — SSH directly:**
```bash
ssh nimrodw@100.125.98.56
cd /data/projects/smallfarmsagents
git pull
sudo systemctl restart sfa-admin
curl http://127.0.0.1:5001/runs
```

### Server Agent Communication Protocol
- **Inbox:** `nimrodw@10.100.102.2:~/agent_comm/inbox/` — push messages here via SCP
- **Outbox:** `nimrodw@10.100.102.2:~/agent_comm/outbox/` — pull responses from here
- **Format:** MSG-YYYYMMDD-NNN.md with YAML frontmatter
- The server agent reads inbox when prompted with `/mail`

---

## 5. Verification Checklist

- [ ] `/runs` returns HTTP 200
- [ ] FTP upload works to `/agents/sfa/` using `WP_FTP_*` credentials
- [ ] `/agents/.htaccess` created with `RewriteEngine Off`
- [ ] `nimrod.bio/agents/sfa/index.html` accessible via browser (not 404)
- [ ] WordPress page 91325 updated: all 53 references changed from `wp-content/uploads/market/` to `/agents/sfa/`
- [ ] All fixes committed and pushed to GitHub
- [ ] Server agent confirms deployment via `/mail`

---

*Mandate issued by Team 100 (Architecture) via Nimrod | 2026-04-10*
