# LOD400 — SFA-S002-P001-WP006 — FTPS Upload Remediation (F-01 fix)

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP006
**Type:** LOD400_SPEC
**Status:** READY for L-GATE_BUILD
**Builder:** sfa_build (Sonnet, Team 10) — code work
**Production validator:** team_99 (deploy + smoke on waldhomeserver)
**QA:** Team 50
**Validator:** external (cross-engine — code merge to main)
**Priority:** P0 (blocking launch + active public regression)

---

## 1. Goal

Restore FTPS upload to uPress so the public price-index artifacts at `https://www.nimrod.bio/wp-content/uploads/market/` reflect the latest pipeline run (within 24 hours, ideally within minutes of pipeline completion).

team_99 Pass-1 verdict (2026-05-06) identified F-01 HIGH: `ftplib.FTP_TLS` does not negotiate TLS session reuse on data connections, so uPress responds 425 (or times out) on `STOR`. Public artifacts are stuck at `artifact_version=20260417_004822` — **19 days stale**.

---

## 2. Root cause (already known)

uPress requires **TLS session reuse on data connections**. Standard Python `ftplib.FTP_TLS` opens a fresh TLS session for each data transfer, which uPress rejects. The fix is a custom subclass — `ReusedSessionFTP_TLS` — that wraps the data socket using the control connection's existing TLS session.

**Reference implementation (working in production):**
- `/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/ftps_upload.py`
- `/Users/nimrod/Documents/shaked-wg-agent/tests/test_ftps_upload.py`

Per the docstring at the top of that file: *"Pattern copied from SmallFarmsAgents/organic_market_agent/publisher/ftps_upload.py"* — meaning **SFA originally had this pattern** but lost it (or it regressed). This WP restores it.

---

## 3. Acceptance Criteria

### AC-01 — `ReusedSessionFTP_TLS` subclass present in SFA
- `organic_market_agent/publisher/ftps_upload.py` defines a `ReusedSessionFTP_TLS` (or equivalently named) subclass of `ftplib.FTP_TLS` that overrides `ntransfercmd` (or `_open_datasock` / `prot_p` chain) to wrap the data socket using the control connection's `_sslobj` session.
- The implementation is **functionally equivalent** to the shaked-wg-agent reference. Builder may copy verbatim and adapt the namespace, OR derive independently — but must achieve the same effect.

### AC-02 — Code path uses the subclass
- `ftps_upload.py` upload entry point (`upload_to_upress` or equivalent) instantiates `ReusedSessionFTP_TLS`, NOT plain `FTP_TLS`.
- All `STOR`/`RETR`/`NLST` calls go through the subclass.

### AC-03 — Unit + integration tests
- `tests/test_ftps_upload.py` exists with test cases:
  - Subclass behaves correctly when control + data connections share session.
  - Connection retry/backoff respected (per existing constants).
  - Mock-based test for upload of `manifest.json` + `public_report.json` + `public_report.html` + `public_report_body.html`.
- `pytest tests/test_ftps_upload.py` passes.

### AC-04 — Smoke against staging or production confirms upload
- Builder uploads a single test file (e.g., a small `verify_ftps_<timestamp>.txt`) to `wp-content/uploads/market/` (or a sandbox path) using the new code.
- HTTP 200 fetch of the same URL within 60 seconds confirms upload landed.
- If staging credentials unavailable → smoke is performed by team_99 post-deploy (see §6 deployment hand-off).

### AC-05 — Production deployment (handed to team_99)
- After builder commits the fix and tests pass:
  - team_99 pulls offline branch on waldhomeserver
  - Runs `python -m organic_market_agent run_publisher --upload` manually
  - Verifies `https://www.nimrod.bio/wp-content/uploads/market/manifest.json` `artifact_version` updates to a timestamp from the past hour
  - Verifies `staleness_level == fresh` and `report_date` is current (not the placeholder `2099-08-12`)

### AC-06 — Sustained operation
- Next 2 daily cron runs (06:00 UTC) succeed end-to-end (ingest + publish + FTPS upload).
- `pipeline_alerts` shows zero `FTPS upload FAILED` entries in the 48 hours following deployment.
- WP003 Pass-2 verification re-runs and lifts AC-04 from FAIL to PASS.

### AC-07 — Documentation
- `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md` updated with a `## 6. FTPS troubleshooting` subsection if any new operator-facing behavior is added (only if necessary — minor).
- `CHANGELOG.md` `[Unreleased]` entry under `### Fixed` describing the F-01 resolution.

---

## 4. Files in scope

### UPDATE
- `organic_market_agent/publisher/ftps_upload.py` — restore/add `ReusedSessionFTP_TLS` subclass; route uploads through it
- `tests/test_ftps_upload.py` — CREATE if missing OR UPDATE existing
- `CHANGELOG.md` `[Unreleased]` — Fixed section
- `documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md` — only if operator-facing behavior changes

### REFERENCE (read-only — do NOT modify)
- `/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/ftps_upload.py`
- `/Users/nimrod/Documents/shaked-wg-agent/tests/test_ftps_upload.py`

### DO NOT TOUCH
- DB schema / migrations
- Collectors
- Public templates / CSS (WP004 territory)
- WP005 / WP001 / WP002 territory

---

## 5. Implementation notes

### Subclass pattern (from shaked-wg-agent reference)
The pattern is roughly:

```python
class ReusedSessionFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS subclass that reuses the control TLS session for data connections.
    Required by uPress's FTPS server."""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            session = self.sock.session
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=session,
            )
        return conn, size
```

Builder must read the actual reference file for the canonical version including any retry/backoff/timeout adjustments.

### Env variables (already in `.env.example`)
- `UPRESS_SFTP_HOST` (despite name, this is FTPS, not SFTP)
- `UPRESS_SFTP_USER`
- `UPRESS_SFTP_PASS`
- `UPRESS_UPLOAD_PATH=wp-content/uploads/market`
- `UPRESS_PUBLIC_BASE=https://www.nimrod.bio`

### WAN context (informational)
waldhomeserver is on **IPv6-only WAN (Bezeq be fiber)**. clatd provides IPv4 NAT64 emulation for outbound connections. team_99 fixed the IPv4 routing on 2026-05-06 (clatd restored after Tailscale exit-node removal). The remaining issue is purely the TLS-session-reuse protocol incompatibility — not network reachability.

---

## 6. Deployment hand-off (sfa_build → team_99)

After AC-01..AC-04 satisfied and committed:
1. sfa_build pushes offline branch with the fix.
2. team_100 issues a follow-up MSG to team_99 (separate aos_mail) requesting deploy + verification per AC-05+AC-06.
3. team_99 self-attests OPS deployment per their contract Push Authority + ADR044 §1; files DEPLOY_LOG in `_COMMUNICATION/team_99/SFA-S002-P001-WP006/`.
4. WP006 closes (L-GATE_V external) once both AC-05 and AC-06 PASS.

---

## 7. Test plan

### Unit
- Mock `ftplib.FTP.ntransfercmd` and verify `ssl.wrap_socket` is called with the control connection's session.
- Mock retry behavior (3 attempts with backoff 5/10/20).

### Integration
- Optional: docker-compose with a local FTPS server that requires session reuse (probably out of scope for this WP — defer to manual smoke).

### Manual smoke
- Upload a 100-byte test file to `wp-content/uploads/market/_verify_<timestamp>.txt` from the offline branch tip.
- Curl-fetch and confirm 200.

### Production smoke (team_99)
- Manual `run_publisher --upload` on waldhomeserver.
- Verify public manifest update.

---

## 8. Risks

| Risk | Mitigation |
|------|-----------|
| Reference impl in shaked-wg-agent has diverged from what uPress currently accepts | Builder verifies smoke first; if subclass fails, escalate to team_100 for re-spec |
| Credentials missing in dev env | Builder's local smoke is optional — production smoke is the canonical PASS check |
| Subclass conflicts with M10 spike's `ftps_upload.py` changes (CONFLICT-LIKELY in WP001 audit) | WP006 lands first; WP001 builder reconciles in their merge step (already noted in WP001 LOD400 §3 AC-04) |

---

## 9. Sprint estimate

**SMALL (1–2 days)** — root cause known, reference implementation available, fix is a focused subclass restoration + tests + smoke.

---

## 10. References

- WP003 Pass-1 verification report: `_COMMUNICATION/team_99/SFA-S002-P001-WP003/VERIFICATION_REPORT_v1.0.0.md` (F-01 evidence)
- Reference impl: `/Users/nimrod/Documents/shaked-wg-agent/shaked_wg_agent/publisher/ftps_upload.py`
- Reference tests: `/Users/nimrod/Documents/shaked-wg-agent/tests/test_ftps_upload.py`
- Program package: `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md`

---

*LOD400 ready. L-GATE_E + L-GATE_S fast-tracked (PASS in same session) given known root cause + active public regression.*
