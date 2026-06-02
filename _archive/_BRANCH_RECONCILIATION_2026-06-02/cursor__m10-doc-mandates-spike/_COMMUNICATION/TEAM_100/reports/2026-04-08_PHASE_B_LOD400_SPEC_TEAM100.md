# Phase B — M11 Specification Documents (LOD400)

**Document ID:** SPEC-20260408-PHASE-B-LOD400  
**Date:** 2026-04-08  
**Author:** Team 100 (Architecture)  
**Status:** ACTIVE — binding template and checklist for M11 document authoring  
**Mandate:** `_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md` (MANDATE-20260407-M11-SPECS)  
**Target version:** v1.2.0  
**Precondition:** G-V1.1 PASS (v1.1.0 released) before treating M11 as the active execution priority  
**Gate:** Team 100 self-sign-off + Nimrod review (no Team 50 QA — documents only)  
**Expands LOD200:** `_COMMUNICATION/TEAM_100/MANDATE_M11_SPECS_TEAM100.md` (MANDATE-20260407-M11-SPECS) — this document adds authoring precision, required section structures, wireframes, and verification checklists for all three M11 deliverables  
**Canonical brief:** `_COMMUNICATION/TEAM_100/CANONICAL_PROGRAM_BRIEF_PHASES_A_B_TEAM100.md` (BRIEF-20260407-PHASE-AB-CANONICAL)

---

## 0. Code-vs-Plan Corrections (LOD400 baseline notes)

| # | Finding | LOD200 framing | LOD400 correction |
|---|---------|----------------|-------------------|
| B1 | FarmCostAgent source material | "Team 80 product perspective" requested | Team 80 already produced a `CostModel` in `sfa_handoff_v2/04_functional_spec.md` (labor/water/seeds/land/misc → total_cost/cost_per_unit/recommended_price). The concept brief must synthesize this, not start from scratch. |
| B2 | Farmer roles | No existing WP documentation | Team 80's `sfa_handoff_v2/03_farmer_layer.md` defines guest/registered/pending_farmer/farmer/admin flow. The ADR must canonize this with WP capability mapping and an implementation recommendation. |
| B3 | "FarmCostAgent" naming | Name appears only in M11 mandate | Team 80 uses "CostModel" and "personal calculator." The concept brief must establish "FarmCostAgent" as the canonical agent name going forward and bridge it to Team 80's framing. |
| B4 | In-Page form dependency | Listed as "depends on Item 8" | Confirm: Item 10 cannot be specced completely without the farmer role definitions from Item 8. Items must be authored in order: 8 → 10. Item 9 (FarmCostAgent) is independent of both. |

---

## 1. Phase B Overview

M11 is a **specification-only** milestone. No production code is written. Three documents are authored by Team 100 (with Team 80 input on Item 9). Upon completion:

1. All three documents are cross-referenced as specified in §5
2. Team 100 completes the §6 verification checklist
3. Nimrod reviews and signs off
4. Team 100 files a completion report
5. Tag: `v1.2.0`

---

## 2. Execution Order and Parallelism

```
Item 9 (FarmCostAgent Concept Brief)  ── can start immediately (independent)
     │
     ├── authored in parallel with Item 8
     │
Item 8 (WordPress Farmer Roles ADR)   ── start immediately
     │
     └── Item 10 (In-Page Submission Form) ── starts after Item 8 draft is stable
                                              (roles and auth model must be settled first)
```

---

## 3. Item 8 — WordPress Farmer Roles: Architecture Decision Record

**Output path:** `_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_WORDPRESS_FARMER_ROLES_TEAM100.md`  
**Lead:** Team 100  
**Input:** `_COMMUNICATION/TEAM_80/sfa_handoff_v2/03_farmer_layer.md` (synthesize)

### 3.1 Required document structure (LOD400 — every section is mandatory)

```
# Architecture Decision Record — WordPress Farmer Roles

Document ID: ADR-20260408-WP-FARMER-ROLES
Date: 2026-04-08
Status: DRAFT → FINAL after Nimrod sign-off
Author: Team 100
Depends on: —
Required by: Item 10 (Submission Form spec)
```

#### Section 1: Background and Problem Statement

Content requirements:
- Why farmer roles are needed: transition from anonymous read-only to verified community participation
- Current state: all visitors are anonymous, no differentiation
- Desired end state: verified farmers can interact with the data (edit, submit, compare scenarios)
- Source: brief paragraph synthesizing `sfa_handoff_v2/03_farmer_layer.md` Goal statement

#### Section 2: Role Definitions (BINDING table)

This table is the canonical role definition for the entire MyFarmAgents platform. It becomes the reference for Item 10 and any future implementation work.

| Role | WordPress capability | Access level | How acquired | Display label (Hebrew) |
|------|---------------------|--------------|--------------|------------------------|
| `guest` | none / `read` (unauthenticated) | Public page view-only | Anonymous visit | אורח |
| `subscriber` / `registered` | `subscriber` | View + limited interaction (no data edit) | Standard WP registration (no checkbox) | משתמש רשום |
| `pending_farmer` | custom capability: `pending_farmer` | View + disabled interaction UI + hint text | WP registration with "אני חקלאי" checkbox | חקלאי ממתין לאישור |
| `farmer` | custom capability: `verified_farmer` | Full interaction: edit fields, save scenarios, submit data | Admin approval of `pending_farmer` | חקלאי מאומת |
| `admin` | `administrator` | Approve/reject farmers, manage data | Existing WP admin | מנהל |

**UX enforcement table:**

| Role | Can see table | Can edit inputs | Can save scenario | Can submit data | Can view submitted data |
|------|:---:|:---:|:---:|:---:|:---:|
| `guest` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `registered` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `pending_farmer` | ✓ | disabled (visual hint) | ✗ | ✗ | ✗ |
| `farmer` | ✓ | ✓ | ✓ (future M12) | ✓ (when form live) | own submissions only |
| `admin` | ✓ | ✓ | ✓ | ✓ | all |

#### Section 3: Registration Flow (step-by-step — with mockup)

Numbered procedure:

1. Visitor lands on `/smallfarmsagent/` page
2. Clicks "התחבר / הירשם" (login/register CTA)
3. WP registration form opens
4. Form includes an additional checkbox: **"אני חקלאי — אני מגדל/ת ירקות ורוצה לתרום נתונים"**
5. On submit with checkbox checked: `pending_farmer` custom capability is granted instead of default `subscriber`
6. Admin receives notification email: "New pending farmer registration: [username]"
7. Admin reviews via WP Admin → Users → filter by `pending_farmer`
8. Admin either: (a) approves → changes role to `farmer`; (b) rejects → deletes account or demotes to `subscriber`
9. Farmer is notified of approval (optional: custom email hook)
10. On next login: farmer-only UI elements become active

**Wireframe — Pre-login state on table row:**

```
┌────────────────────────────────────────────────────────────────────┐
│  גזר אורגני         ₪8.50/ק״ג     2 מקורות     ₪7.00 – ₪10.00    │
│                                                                    │
│  [▶ פרטים]  [✏ ערוך את הנתונים שלי — זמין לחקלאים מאומתים ]     │
│                              ↑                                     │
│              disabled button, muted style, tooltip on hover:       │
│              "כדי לערוך נתונים, צריך להיות חקלאי מאומת.           │
│               הירשם וסמן את תיבת החקלאי להגשת בקשה"               │
└────────────────────────────────────────────────────────────────────┘
Note: RTL layout — edit button appears at inline-start (right side in Hebrew)
Button state: aria-disabled="true", tabindex="-1"
```

#### Section 4: WordPress Implementation Options

| Option | Description | Pros | Cons | Recommended |
|--------|-------------|------|------|-------------|
| **A — Native custom roles** | Add `pending_farmer` and `verified_farmer` capabilities in `functions.php` + `register_activation_hook` | Zero plugin footprint, full control, consistent with project zero-plugin approach | Must maintain capability logic manually | **YES — preferred** |
| B — User Role Editor plugin | Visual role/capability management via UI | Easy for Nimrod to manage | Adds plugin dependency | No — avoid plugin for this |
| C — Membership plugin (MemberPress / ARMember) | Full membership management | Feature-rich, payment-ready | Overkill; conflicts with zero-plugin approach; performance | No |

**Recommendation: Option A** — custom roles via `functions.php` in `flatsome-child`. Consistent with existing zero-plugin philosophy (WPForms removed, contact form done in PHP). Capabilities are registered on `init`, role assignment happens on `user_register` hook.

#### Section 5: Technical Implementation Sketch (Option A)

This section provides enough detail for future implementation mandate. NOT production code in M11.

```php
// In flatsome-child/functions.php — conceptual outline only

// Register custom capabilities on init
add_action('init', function() {
    // Add pending_farmer cap to subscriber role as a flag
    // Better: custom role 'pending_farmer'
    add_role('pending_farmer', 'חקלאי ממתין', ['read' => true]);
    add_role('verified_farmer', 'חקלאי מאומת', ['read' => true, 'verified_farmer' => true]);
});

// On user registration with checkbox
add_action('user_register', function($user_id) {
    if (!empty($_POST['is_farmer'])) {
        $user = new WP_User($user_id);
        $user->set_role('pending_farmer');
        // Notify admin
        wp_mail(get_option('admin_email'), 
                'New pending farmer: ' . $user->display_name, 
                'Review at: ' . admin_url('users.php?role=pending_farmer'));
    }
});

// Registration form filter — add checkbox to WP default form
add_action('register_form', function() {
    echo '<p><label><input type="checkbox" name="is_farmer" value="1"> ';
    echo 'אני חקלאי — רוצה לתרום נתונים</label></p>';
});
```

#### Section 6: Security Considerations

- `pending_farmer` and `verified_farmer` capabilities grant ONLY read access + UI unlock — no WP admin access
- Farmer-submitted data goes through operator moderation before entering pipeline (see Item 10)
- WordPress nonce validation on all forms
- Rate limiting on form submission (use WP's built-in throttling or server-level)
- Farm identity never appears in public output (existing privacy policy)

#### Section 7: Migration Path from Current State

Current state: all visitors anonymous. No changes to public page anonymity required.

Migration steps (future M12 implementation):
1. Add `functions.php` hooks (Option A above)
2. Deploy to nimrod.bio via FTPS
3. Update WP registration form (or create custom registration page)
4. Test approval flow in dev environment first
5. Communicate to existing community contacts: new farmer registration available

#### Section 8: Cross-references

- **Item 10** (In-Page Submission Form): depends on `verified_farmer` capability check
- **Privacy Policy** (`docs/PRIVACY_POLICY.md`): farmer identity protection confirmed
- **uPress Standard** (`docs/UPRESS_WORDPRESS_STANDARD_v2.md`): deployment procedure

---

## 4. Item 9 — FarmCostAgent: Concept Brief

**Output path:** `_COMMUNICATION/TEAM_100/reports/2026-04-08_CONCEPT_BRIEF_FARMCOSTAGENT_TEAM100.md`  
**Lead:** Team 100 + Team 80 (input for §4)  
**Input:** `_COMMUNICATION/TEAM_80/smallfarms_agent_handoff/04_functional_spec.md` (CostModel), `07_roadmap.md`

### 4.1 Required document structure (LOD400 — every section is mandatory)

```
# FarmCostAgent — Concept Brief

Document ID: BRIEF-20260408-FARMCOSTAGENT
Date: 2026-04-08
Status: DRAFT → FINAL after Team 80 input + Nimrod sign-off
Author: Team 100
Team 80 input: Section 4 (target user, value proposition)
```

#### Section 1: Agent Name and Position in MyFarmAgents Platform

**Canonical name:** FarmCostAgent  
**Platform:** MyFarmAgents (second agent, after OrganicMarketAgent)  
**Relationship to OMA:** FarmCostAgent is a **companion agent** — it consumes OMA's published price data as the "market benchmark" and adds per-farm cost analysis on top.

Architecture position diagram:

```
MyFarmAgents Platform
│
├── OrganicMarketAgent (OMA)
│   ├── Data pipeline (collect → normalize → aggregate → publish)
│   └── Public index: current market prices at community sources
│
└── FarmCostAgent (FCA) ← THIS DOCUMENT
    ├── Inputs: OMA price data + farmer's own cost data
    ├── Outputs: cost breakdown, margin analysis, recommended price
    └── Interface: per-farmer session (not public index)
```

#### Section 2: Problem Statement

Small organic farms in Israel lack accessible, low-friction tools to calculate whether their current pricing covers their actual production costs. Without this analysis:
- Farmers undercharge relative to production costs (especially labor)
- Farmers cannot benchmark their costs against community market prices
- Price decisions are made on intuition, not data

**Team 80 source:** `smallfarms_agent_handoff/01_strategy.md` — "Tool Enhancements" section; `07_roadmap.md` — "Personal calculator."

#### Section 3: Proposed Agent Capabilities (MVP scope)

The MVP FarmCostAgent is a **personal cost calculator** that connects to OMA market data.

**Input model (from Team 80 CostModel, `04_functional_spec.md`):**

| Input field | Type | Unit | Notes |
|-------------|------|------|-------|
| `product_code` | select | — | from OMA catalog |
| `quantity_produced` | decimal | kg (or pack) | estimated yield |
| `labor_hours` | decimal | hours | per production cycle |
| `labor_rate_per_hour` | decimal | ILS/hour | default: minimum wage |
| `water_m3` | decimal | m³ | irrigation volume |
| `water_cost_per_m3` | decimal | ILS/m³ | regional rate |
| `seeds_cost` | decimal | ILS | total seed purchase |
| `land_dunam` | decimal | dunam | land area used |
| `land_cost_per_dunam` | decimal | ILS/cycle | lease or opportunity cost |
| `misc_costs` | decimal | ILS | packaging, transport, etc. |

**Output model:**

| Output field | Formula | Description |
|-------------|---------|-------------|
| `total_cost` | sum of all cost inputs | Total production cost for this cycle |
| `cost_per_unit` | `total_cost / quantity_produced` | Cost per kg/pack |
| `market_avg_price` | from OMA `normalized_observations` | Current community average |
| `margin_at_market` | `market_avg_price - cost_per_unit` | Profit/loss at current market price |
| `recommended_price` | `cost_per_unit × markup_factor` | Suggested selling price |
| `markup_factor` | configurable, default 1.25 | Target margin percentage |
| `break_even_quantity` | `total_cost / market_avg_price` | Min units to break even at market price |

#### Section 4: Target User and Value Proposition (Team 80 input section)

**[PLACEHOLDER — requires Team 80 input]**

This section must be completed with Team 80's product perspective, addressing:
- Primary persona: who is this farmer? (scale, tech comfort, primary language)
- Key job-to-be-done: what decision does FarmCostAgent help them make?
- Value proposition in one sentence (Hebrew)
- Differentiation from existing tools (Excel, WhatsApp groups, intuition)
- Key UX requirement for adoption: how does it need to feel to a farmer in the field?

Team 80 input trigger: Team 100 requests this section from Team 80 when Phase B begins. Team 80 has 1 session to contribute. If not received within phase timeline, Team 100 drafts based on strategy documents and marks as "pending Team 80 review."

#### Section 5: Technical Architecture Sketch

**Data flow:**

```
Farmer session
     │
     ├── Cost inputs (browser form)
     │
     ▼
FarmCostAgent calculator (client-side JS or server-side API)
     │
     ├── Fetch: OMA market price for selected product
     │   └── Source: public_report.json (static) or OMA REST API (future)
     │
     ├── Calculate: CostModel outputs
     │
     └── Display: breakdown table + recommendation
```

**AI model role (future v2.x):**
- Pattern recognition: flag unusual cost inputs vs. community norms
- Scenario suggestions: "if you increase yield by 20% your cost-per-kg drops to..."
- Conversational interface: farmer describes situation in Hebrew, agent calculates

**Storage:**
- MVP: client-side session only (no server persistence)
- v1.1 (if farmer roles implemented): save scenarios per `farmer` user in WP user meta

#### Section 6: MVP Scope vs Full Vision

| Feature | MVP (FCA v1) | Full Vision (FCA v2+) |
|---------|-------------|----------------------|
| Cost calculator | ✓ | ✓ + AI-enhanced |
| Market price benchmark | ✓ (from OMA public JSON) | ✓ + real-time |
| Save scenarios | ✗ | ✓ (requires farmer roles) |
| Compare multiple products | ✗ | ✓ |
| AI recommendations | ✗ | ✓ |
| Mobile-optimized | ✓ (required) | ✓ |
| Hebrew RTL | ✓ (required) | ✓ |

#### Section 7: Integration Points with OMA Infrastructure

- **OMA public JSON**: `public_report.json` → `products[].stats_by_filter.grower.avg_price` provides the market benchmark
- **OMA product catalog**: FCA product selector uses the same 77+ products
- **OMA privacy model**: FCA per-farm cost data is NEVER published in OMA output — completely separate data layer
- **Platform**: MyFarmAgents umbrella — FCA is agent #2 alongside OMA

#### Section 8: Open Questions for Nimrod Decision

| # | Question | Options | Decision needed by |
|---|---------|---------|-------------------|
| 1 | Where does FCA live? | Separate page at nimrod.bio/farm-cost/ vs embedded in /smallfarmsagent/ | Before M12 spec |
| 2 | Storage model for MVP | Client-side only vs WP user meta (requires farmer roles) | Before M12 implementation |
| 3 | AI model integration | Which API? Budget per query? Local vs cloud? | Before FCA v2 |
| 4 | Team 80 involvement | Ongoing product input or one-time brief? | Before M12 kickoff |

---

## 5. Item 10 — In-Page Submission Form: Technical Specification

**Output path:** `_COMMUNICATION/TEAM_100/reports/2026-04-08_SPEC_INPAGE_SUBMISSION_FORM_TEAM100.md`  
**Lead:** Team 100  
**Dependency:** Item 8 (farmer roles ADR) must be in FINAL status before authoring  
**Note:** The form does not exist yet — this spec feeds a future implementation milestone (M12+)

### 5.1 Required document structure (LOD400 — every section is mandatory)

```
# Technical Specification — In-Page Price Submission Form

Document ID: SPEC-20260408-INPAGE-SUBMISSION-FORM
Date: 2026-04-08
Status: DRAFT → FINAL after Nimrod sign-off
Author: Team 100
Depends on: ADR-20260408-WP-FARMER-ROLES (Item 8)
```

#### Section 1: Dependency and Authentication Requirement

- This form is only available to users with the `verified_farmer` capability (see ADR-20260408-WP-FARMER-ROLES)
- Unauthenticated users see the form grayed out with hint text (see Item 8 §3 wireframe)
- `pending_farmer` users see the form grayed out: "בקשתך ממתינה לאישור"
- Authentication check: WordPress `current_user_can('verified_farmer')` on every render and submission

#### Section 2: Form Fields (BINDING)

| Field | Type | Label (Hebrew) | Validation | Required | Notes |
|-------|------|----------------|------------|----------|-------|
| `product_code` | `<select>` | "מוצר" | must be valid `Product.code` | Yes | Options from OMA catalog; Hebrew names |
| `price` | `<input type="number">` | "מחיר" | > 0, ≤ 1000, 2 decimal places | Yes | ILS |
| `unit_code` | `<select>` | "יחידת מידה" | must be valid `measurement_units.code` | Yes | Options filtered to units valid for selected product |
| `observation_date` | `<input type="date">` | "תאריך המחיר" | ≤ today, ≥ today − 14 days | Yes | Farmer cannot submit stale data |
| `source_context` | `<input type="text">` | "שם המשק / השוק" | max 100 chars | No | For operator validation; NOT published |
| `notes` | `<textarea>` | "הערות" | max 500 chars | No | Quality grade, variety, context |

**Hidden / server-side fields (not shown to user):**
- `user_id`: `get_current_user_id()`
- `source_type`: hardcoded `'community_submission'`
- `submission_ip_hash`: SHA-256 of IP (for abuse detection — NOT stored raw)
- `nonce`: WordPress nonce (`wp_create_nonce('sfa_submit_price')`)

#### Section 3: Data Validation (server-side — binding)

All validation runs on the server (WordPress `admin-post.php` handler), not client-only:

| Rule | Check | Rejection message |
|------|-------|------------------|
| Authentication | `current_user_can('verified_farmer')` | "אין הרשאה" |
| Nonce | `wp_verify_nonce(...)` | "שגיאת אבטחה — נסה שנית" |
| Product exists | `SELECT id FROM products WHERE code = ? AND is_active = true` | "מוצר לא קיים" |
| Price range | 0 < price ≤ 1000 | "מחיר לא סביר" |
| Unit valid for product | Unit must be in allowed set for product category | "יחידת מידה לא מתאימה" |
| Date range | observation_date ≥ today − 14 days AND ≤ today | "תאריך לא תקין" |
| Duplicate detection | Same `user_id` + `product_code` + `observation_date` → reject | "נתון כבר קיים לתאריך זה" |

#### Section 4: Pipeline Integration

**Target table:** `raw_extracted_items`

```sql
-- How a community submission enters the pipeline
INSERT INTO raw_extracted_items (
  source_fetch_run_id,   -- FK to a dedicated "community_submission" source_fetch_run
  raw_product_name,      -- Hebrew canonical name of the product
  raw_price_text,        -- formatted ILS amount (e.g., "25.00")
  raw_unit_text,         -- unit label matching measurement_units.code
  extraction_status,     -- 'pending_moderation'
  raw_payload_json,      -- { "source_context": "...", "notes": "...", "submitter_user_hash": "..." }
  is_quarantined,        -- false (let operator review determine)
  extracted_at           -- now()
)
```

**Dedicated source for community submissions:**
- Register source `SRC_CM` (community submissions) if not already present
- `source_tier = 'community'`
- `market_scope = 'community'`
- `is_active = true`
- This ensures community submissions flow through the normalizer the same way as scraped data

**Moderation workflow:**
1. Submission creates `raw_extracted_items` row with `extraction_status = 'pending_moderation'`
2. Admin sees new item in `/unresolved` or dedicated `/submissions` view
3. Admin reviews: approve → change status to `'extracted'` (normalizer picks it up) OR reject → change to `'ignored'`
4. On approve: normalizer processes on next `catalog_renormalize` or scheduled run
5. Approved data appears in next publish cycle

#### Section 5: WordPress Implementation Options

| Option | Description | Verdict |
|--------|-------------|---------|
| **A — Shortcode + admin-post.php** | Same pattern as `[sfagent_contact_form]` in functions.php | **Preferred** — zero plugin, consistent with existing approach |
| B — WP REST API endpoint | Custom `/wp-json/sfagent/v1/submit-price` route | Clean API, easier testing; slightly more implementation complexity |
| C — Hybrid: shortcode UI + REST handler | Best of both | Good for future mobile app access |

**Recommendation: Option A for MVP**, Option C if REST API authentication is already in place.

#### Section 6: Privacy Policy Alignment

Per `docs/PRIVACY_POLICY.md` (binding):
- `source_context` (farm/market name) is stored in `raw_payload_json` **only** — never in `normalized_observations`
- `submitter_user_hash` is a SHA-256 hash of `user_id + salt` — not reversible to identity
- Published OMA output shows only source COUNT (≥ 2), not names
- No personal data in `public_report.json` or any published artifact

**New privacy rule added by this spec:** Community submission `raw_payload_json` must be treated as PII. It must not appear in any admin export, backup download, or API response accessible to non-admin users.

#### Section 7: Wireframe — Form Panel (RTL)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  שלח מחיר                                                          [✕]  │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  מוצר *                                                                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  עגבנייה                                                       ▾  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  מחיר (₪) *          יחידת מידה *            תאריך המחיר *             │
│  ┌─────────────┐      ┌─────────────────┐      ┌──────────────────┐    │
│  │  25.00      │      │  ק״ג         ▾  │      │  08/04/2026      │    │
│  └─────────────┘      └─────────────────┘      └──────────────────┘    │
│                                                                         │
│  שם המשק / השוק (לא יפורסם)                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  חווה אורגנית מוריה, שוק האיכרים                                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  הערות (אופציונלי)                                                      │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  עגבניות תמר, ישר מהשדה                                          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ℹ️ הנתונים שלך יוצגו באופן מצטבר בלבד. שם המשק לא יפורסם.            │
│                                                                         │
│  [ביטול]                              [שלח מחיר    →]                  │
│   ↑ secondary                          ↑ primary CTA, inline-start RTL  │
└─────────────────────────────────────────────────────────────────────────┘

Notes on RTL layout:
- Form fields: right-aligned labels, right-to-left input text
- CTA button: inline-start (left-side in RTL Hebrew layout)
- Error messages: appear below each field, red text
- Success state: replace form with "תודה! הנתונים התקבלו ויועברו לאחר אישור"
```

#### Section 8: Cross-references

- **Item 8** (Farmer Roles ADR): `verified_farmer` capability required in §1 and §3
- **Item 9** (FarmCostAgent): community submissions enrich OMA data used in FCA cost analysis
- **Privacy Policy** (`docs/PRIVACY_POLICY.md`): §6 alignment
- **Contact form pattern** (`flatsome-child/functions.php`): implementation model for Option A

---

## 6. Cross-Reference Matrix (mandatory — all three documents)

This table must appear in the completion report and be verified by Team 100 before sign-off:

| Reference | From document | Section | To document | Section |
|-----------|--------------|---------|-------------|---------|
| Item 10 auth depends on farmer role definition | SPEC-INPAGE-FORM | §1 | ADR-WP-FARMER-ROLES | §2 (role table) |
| Item 10 form wireframe references disabled state | SPEC-INPAGE-FORM | §7 | ADR-WP-FARMER-ROLES | §3 (wireframe) |
| FarmCostAgent uses OMA price as benchmark | BRIEF-FARMCOSTAGENT | §7 | n/a (OMA architecture) | — |
| Community submissions feed OMA data used by FCA | BRIEF-FARMCOSTAGENT | §7 | SPEC-INPAGE-FORM | §4 |
| Privacy: farmer identity protection | SPEC-INPAGE-FORM | §6 | ADR-WP-FARMER-ROLES | §5 |
| FCA storage option depends on farmer roles | BRIEF-FARMCOSTAGENT | §6 | ADR-WP-FARMER-ROLES | §4 |

---

## 7. Verification Checklist (Team 100 — §4 of mandate, expanded to LOD400)

Team 100 must confirm ALL items before filing completion report and requesting Nimrod sign-off:

### Item 8 verification
- [ ] §2 roles table: all 5 roles defined with WP capability, access level, trigger, Hebrew label
- [ ] §2 UX enforcement table: complete (roles × capabilities matrix)
- [ ] §3 registration flow: numbered steps, all states covered (register → pending → approve → farmer)
- [ ] §3 wireframe: pre-login disabled state mockup present, RTL-correct
- [ ] §4 implementation options table: all 3 options compared
- [ ] §4 recommended approach: stated explicitly with rationale
- [ ] §5 technical sketch: functions.php outline present (conceptual, not production)
- [ ] §6 security: nonce, rate limiting, no admin access, privacy confirmed
- [ ] §7 migration path: numbered steps from current state to future implementation
- [ ] §8 cross-references: Item 10 dependency cited

### Item 9 verification
- [ ] §1 platform diagram: FCA position in MyFarmAgents shown
- [ ] §3 input model: all 10 fields in table (field, type, unit, notes)
- [ ] §3 output model: all 6 outputs with formulas
- [ ] §4 Team 80 input: received and incorporated (or marked as pending with deadline)
- [ ] §5 data flow diagram: present
- [ ] §6 MVP vs vision table: complete
- [ ] §7 OMA integration: specific JSON path cited (`stats_by_filter.grower.avg_price`)
- [ ] §8 open questions: all 4 questions present with options

### Item 10 verification
- [ ] Item 8 FINAL status confirmed before Item 10 is finalized
- [ ] §2 form fields table: all 6 visible fields + 4 hidden fields specified
- [ ] §3 validation table: all server-side rules with rejection messages
- [ ] §4 pipeline integration: target table, SQL INSERT pattern, source code
- [ ] §4 moderation workflow: numbered steps
- [ ] §5 implementation options: all 3 options with verdict
- [ ] §6 privacy alignment: all PII fields identified, storage restrictions stated
- [ ] §7 wireframe: present, RTL-correct, all states shown (enabled/disabled/success)
- [ ] §8 cross-references: Items 8 and 9 cited

### Cross-reference verification
- [ ] All 6 entries in the cross-reference matrix (§6 of this spec) are confirmed in the actual documents
- [ ] No circular dependencies (Item 8 must not depend on Item 10)

### Final sign-off
- [ ] Nimrod has reviewed all three documents
- [ ] Nimrod confirms product direction for Item 9 §8 open questions (minimum: questions 1 and 2)
- [ ] Completion report filed: `_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M11_SPECS_COMPLETION_TEAM100.md`
- [ ] ROADMAP updated to: M11 COMPLETE
- [ ] Tag v1.2.0 created

---

## 8. Completion Report Template

`_COMMUNICATION/TEAM_100/reports/YYYY-MM-DD_M11_SPECS_COMPLETION_TEAM100.md`

Must include:
1. Summary of all three documents produced (paths, IDs, dates)
2. Cross-reference matrix table (from §6 above) — verified
3. Team 80 input: received / pending / drafted by Team 100
4. Nimrod sign-off confirmation with date
5. Open items from §8 of Item 9 (decisions not yet made)
6. v1.2.0 tag confirmed

---

**Authored by:** Team 100 (Architecture)  
**Document ID:** SPEC-20260408-PHASE-B-LOD400  
**Binding authority:** This document specifies the required content and structure for all three M11 deliverables. Documents not meeting this spec cannot be accepted for v1.2.0 sign-off.
