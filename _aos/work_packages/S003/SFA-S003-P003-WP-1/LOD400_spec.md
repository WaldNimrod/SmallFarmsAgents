# LOD400 — SFA-S003-P003-WP-1 — uPress Provisioning + Cloudflare DNS for sfa.nimrod.bio

**Date:** 2026-05-23
**Author:** team_100
**WP:** SFA-S003-P003-WP-1 — uPress dedicated subdomain provisioning
**Type:** LOD400_SPEC (admin / provisioning WP — team_00 self-executes)
**Status:** ELIGIBLE / L-GATE_E PASS
**Builder:** team_00 (Principal — admin tasks require human at uPress dashboard + Cloudflare)
**Validator:** team_00 (self-attest on completion)
**Effort:** SMALL (~0.5 day team_00 work + 1-2 days uPress response wait)
**Blocks:** WP-2, WP-3, WP-4 (all P003 work depends on this)

---

## §1 Goal

Provision the infrastructure substrate for `sfa.nimrod.bio` — a **dedicated subdomain** on the existing uPress account with:
- **No WordPress install** (raw PHP + MySQL hosting)
- **MySQL database** for SFA data
- **Same FTP credentials** as the existing nimrod.bio site (no re-provisioning of upload tooling)
- **Cloudflare DNS** pointing the subdomain at uPress origin with proxy enabled
- **HTTPS/TLS** active (Let's Encrypt or uPress-provided)

This is the foundation for everything else in P003. Once complete, team_100 hands WP-2 (Slim app skeleton) to sfa_build.

---

## §2 Constraints honored

- **uPress shared hosting** — work within whatever they allow on shared LAMP-style plan
- **Same account** as existing nimrod.bio (no new billing relationship unless uPress explicitly requires)
- **Same FTP credentials** as nimrod.bio (we spent significant effort getting these to work — DON'T re-derive)
- **Cloudflare** already manages nimrod.bio DNS — add subdomain to existing zone

---

## §3 The uPress checklist — questions for support OR self-discovery in uPress dashboard

Open uPress dashboard. Either find answers in the UI or ask uPress support via the support ticket / phone. Aim for **batch** the questions (one ticket, not one per question) to minimize back-and-forth.

### §3.1 Subdomain / site setup

| # | Question | Why we ask |
|---|----------|------------|
| Q1 | Can I create a subdomain `sfa.nimrod.bio` on my existing uPress account without installing WordPress on it? (We want raw PHP + MySQL hosting, no WP.) | Confirms uPress allows non-WP usage on subdomains. If "no, WP required" → we install minimal WP shell and load custom code via plugin (fallback option). |
| Q2 | If yes, what's the directory path on the server where subdomain files live? (`/home/nimrodbi/domains/sfa.nimrod.bio/public_html/`?) | Need this for FTP upload target. |
| Q3 | Are the existing FTP credentials (UPRESS_WP_APP_USER + UPRESS_WP_APP_PASS — or the SFTP credentials we use) valid for uploading files to this subdomain path? | If yes — zero re-provisioning. If no — need new credentials and that's painful. |
| Q4 | Is there additional cost for the subdomain on my current plan? If yes, how much? | Budget decision. |

### §3.2 PHP runtime

| # | Question |
|---|----------|
| Q5 | What PHP version is available on the subdomain? (We want PHP 8.1 or higher.) Can I select per-site? |
| Q6 | What PHP extensions are enabled by default? Specifically need: `pdo`, `pdo_mysql`, `mbstring`, `json`, `curl`, `intl`. |
| Q7 | What's the PHP `max_execution_time` and `memory_limit` per request? (We need at least 30s and 128MB.) |
| Q8 | Can I install Composer dependencies via FTP (uploading `vendor/` directory)? OR is there shell/SSH access to run `composer install`? |

### §3.3 MySQL database

| # | Question |
|---|----------|
| Q9 | Can I create a MySQL database for this subdomain? Same credentials/dashboard as for nimrod.bio's DB? |
| Q10 | Number of databases allowed on my plan? (Currently using 1 for nimrod.bio.) |
| Q11 | What MySQL version (5.7 / 8.0 / MariaDB 10.x)? — we need JSON column support (5.7.8+ or any MariaDB 10.2+). |
| Q12 | Storage quota for the new DB? (We expect to start ~50MB, grow to ~500MB over time.) |
| Q13 | Can the DB host accept connections from external IPs (e.g. waldhomeserver via Tailscale-exit IP), or only from localhost? — if external NOT allowed, our publisher will push via HTTPS to a PHP endpoint, which is fine. |

### §3.4 Web server / routing

| # | Question |
|---|----------|
| Q14 | Is `mod_rewrite` (Apache) or equivalent (nginx rewrites) available for clean URLs without `index.php` in the path? |
| Q15 | Can I configure custom 301/302 redirects (later, when we want to redirect www → subdomain)? |
| Q16 | Are there server-side caching layers I need to be aware of (like the ezcache that surprised us on www)? — and can I disable per-route if needed? |
| Q17 | What's the request bandwidth / monthly traffic limit? |

### §3.5 HTTPS / TLS

| # | Question |
|---|----------|
| Q18 | Does HTTPS automatically activate for the subdomain (Let's Encrypt) once DNS points correctly? Same as nimrod.bio? |

### §3.6 Cloudflare integration

| # | Question (for self-discovery in CF dashboard, not uPress) |
|---|------------|
| Q19 | What origin IP/hostname should sfa.nimrod.bio CNAME or A-record point at? (Check the existing www.nimrod.bio CNAME target in CF — likely same uPress origin.) |
| Q20 | CF proxy ON or OFF for the new subdomain? — ON for caching/DDoS, but verify origin TLS cert covers the subdomain (Let's Encrypt usually generates per-subdomain). |

---

## §4 Output deliverable

Write `_COMMUNICATION/team_00/UPRESS_PROVISIONING_RESULTS_2026-05-XX.md` capturing answers to Q1-Q20 plus:
- Subdomain path on uPress filesystem
- DB name + credentials (in env, not file — use config module pattern)
- PHP version + extensions confirmed
- DNS record created
- HTTPS validated (`curl -I https://sfa.nimrod.bio/` returns 200 or any non-DNS-error response)

---

## §5 Acceptance Criteria

| AC | Criterion | Evidence |
|----|-----------|----------|
| AC-01 | `https://sfa.nimrod.bio/` resolves to the uPress origin and returns a valid HTTP response (200 or 403 or 404 — any of these means DNS+TLS work) | `curl -sSI https://sfa.nimrod.bio/` |
| AC-02 | A test PHP file uploaded via FTP to the subdomain path is executable via HTTPS (`https://sfa.nimrod.bio/test.php` runs PHP) | Upload `<?php phpinfo();`, fetch, see PHP info page |
| AC-03 | MySQL DB exists and is accessible from PHP on the subdomain (test script does `new PDO(mysql:...)` successfully) | PHP test script |
| AC-04 | Same FTP credentials as the existing nimrod.bio site work for the subdomain upload, OR new credentials documented in env config module | written confirmation |
| AC-05 | Cloudflare proxy is active for sfa.nimrod.bio (verify CF dashboard) | screenshot or CF API check |
| AC-06 | Results document filed at `_COMMUNICATION/team_00/UPRESS_PROVISIONING_RESULTS_*.md` with answers to all 20 questions | file exists, frontmatter complete |
| AC-07 | `phpinfo()` test file REMOVED after AC-02 verification (security — don't leave it accessible) | `curl https://sfa.nimrod.bio/test.php` → 404 |

---

## §6 Fallback if uPress says "WP required"

If Q1 returns "no, you must install WordPress on any subdomain", switch to the documented fallback:
- Install minimum WordPress (one-click via uPress)
- Disable / remove every theme + plugin we don't need
- Load custom code via a single SFA plugin that hooks `template_redirect` to bypass WP rendering and serve our app directly
- Same MySQL DB; same PHP routes; same end result — just one wrapper layer of WP we ignore

This adds ~1-2 days to P003 and a bit of friction, but architecture stays the same. Probability uPress requires this: medium-high given their WP positioning.

---

## §7 Definition of Done

1. All 7 ACs PASS
2. team_00 has uploaded a test PHP file, hit it via HTTPS, and confirmed it runs
3. team_00 has connected to MySQL from PHP on subdomain successfully
4. Results document filed; team_100 reads it and unblocks WP-2 (LOD400 spec)
5. WP-1 marked COMPLETE / LOD500_LOCKED in roadmap; gate_history extended

---

## §8 Cross-references

- Decision record: `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- Triggering bug: `documentation/KNOWN_DEBT.md` §B.4 (now SUPERSEDED by P003)
- uPress runbook (current site): `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`
- UPRESS_FTPS_PROTOCOL canon (hub-side, propagated to spoke): `_aos/lean-kit/modules/12-home-server-infrastructure/runbooks/UPRESS_FTPS_PROTOCOL_v1.0.0.md`

---

*LOD400 spec v1.0.0 — authored 2026-05-23 by team_100.*
*Branch: `claude/gallant-elbakyan-727a60` · Commit: pending.*
