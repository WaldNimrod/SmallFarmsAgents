<?php
declare(strict_types=1);

namespace SFA\Tests;

use PDO;
use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use Slim\Psr7\Factory\ServerRequestFactory;

/**
 * ClassBRouteTest — WP-CB-UI-CLASSB AC-7 tests
 *
 * Tests:
 * 1. /account returns 200
 * 2. Market detail renders .pgraph + .phist
 * 3. Search groups results into book + market (.srch-group)
 * 4. Community is feed-less (no .community__feed, has .comm-manifest + .reqcard)
 * 5. Market detail rangesel 90/year buttons have is-disabled server-side
 * 6. Market detail mkt-disc class (not mk-disclaimer)
 * 7. Hub home has .modtile and .hub-grid
 * 8. About has .tier-row
 */
final class ClassBRouteTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        // Schema
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS crops (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, scientific_name TEXT, family_name_he TEXT, category TEXT, season TEXT, dtm_min INTEGER, dtm_max INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS crop_varieties (id INTEGER PRIMARY KEY, crop_id INTEGER, name TEXT, payload_json TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS cover_crops (id INTEGER PRIMARY KEY, name_he TEXT, name_en TEXT, category TEXT, sow_window TEXT, total_days_garden INTEGER, survives_winter INTEGER, notes TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, category TEXT, unit TEXT, last_price REAL, last_price_date TEXT, freshness_days INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS product_prices (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, price_date TEXT, price REAL, source TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS ingest_log (idempotency_key TEXT PRIMARY KEY, table_name TEXT, applied_at TEXT, row_count INTEGER, status TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT)');

        // Seed
        $this->pdo->exec("INSERT OR IGNORE INTO crops (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at) VALUES
            (1,'tomato','עגבנייה','Solanum','סולניים','vegetables','summer',70,95,'{}','2026-05-27')");
        $this->pdo->exec("INSERT OR IGNORE INTO products (id,slug,hebrew_name,category,unit,last_price,last_price_date,freshness_days,payload_json,last_pushed_at) VALUES
            (10,'tomato','עגבנייה','vegetable','kg',12.5,'2026-05-29',2,'{}','2026-05-27'),
            (11,'pepper','פלפל','vegetable','kg',8.5,'2026-05-25',6,'{}','2026-05-27')");
        $this->pdo->exec("INSERT OR IGNORE INTO product_prices (product_id,price_date,price,source) VALUES
            (10,'2026-05-28',11.9,'farm'),
            (10,'2026-05-27',12.1,'farm'),
            (10,'2026-05-26',11.5,'market'),
            (11,'2026-05-25',8.5,'market')");
    }

    /** AC-7: /account returns 200 */
    public function testAccountRouteReturns200(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/account');
        $res = $this->app->handle($req);
        $this->assertSame(200, $res->getStatusCode(), '/account should return 200');
        $this->assertStringContainsString('text/html', (string)$res->getHeaderLine('Content-Type'));
    }

    /** AC-7: account page has "בקרוב" labels */
    public function testAccountHasSoonLabels(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/account');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('בקרוב', $body, 'Account page must have "בקרוב" labels');
    }

    /** AC-7: account page has acct-wrap and setgroup */
    public function testAccountHasClassBComponents(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/account');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('class="acct-wrap"', $body, 'Account must have .acct-wrap');
        $this->assertStringContainsString('class="setgroup"', $body, 'Account must have .setgroup');
    }

    /** AC-7: market detail renders .pgraph section */
    public function testMarketDetailRendersGraph(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/market/tomato');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('pgraph', $body, 'Market detail must render .pgraph');
    }

    /** AC-7: market detail renders .phist history table */
    public function testMarketDetailRendersHistory(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/market/tomato');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('phist', $body, 'Market detail must render .phist table');
    }

    /** AC-7 + MINOR F-05: market detail has 90/year rangesel buttons marked is-disabled server-side */
    public function testMarketDetailDisabledRanges(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/market/tomato');
        $body = (string)$this->app->handle($req)->getBody();
        // Both disabled buttons must be in the template output
        $this->assertStringContainsString('is-disabled', $body, 'Market detail must have .is-disabled rangesel buttons');
        $this->assertStringContainsString('90י', $body, 'Market detail must include 90י label (disabled)');
    }

    /** AC-7 + MINOR F-02: rangesel shows 28י not 30 */
    public function testMarketDetailRangeLabel28Days(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/market/tomato');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('28י', $body, 'Range selector must show 28י (not 30)');
        $this->assertStringNotContainsString('30י', $body, 'Range selector must not show 30י');
    }

    /** AC-7 + MINOR F-01: market pages use .mkt-disc not .mk-disclaimer */
    public function testMarketDisclaimerClassBClass(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/market/tomato');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('mkt-disc', $body, 'Disclaimer must use .mkt-disc class');
    }

    /** AC-7 + MINOR F-01: market list also uses .mkt-disc */
    public function testMarketListDisclaimerClassBClass(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/market/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('mkt-disc', $body, 'Market list disclaimer must use .mkt-disc class');
    }

    /** AC-5 + AC-7: search groups results by book/market (.srch-group) */
    public function testSearchGroupedResults(): void
    {
        // Use URL-encoded Hebrew — ServerRequestFactory needs percent-encoded URI
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/search?q=' . urlencode('עגב'));
        $req = $req->withQueryParams(['q' => 'עגב']);
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('srch-group', $body, 'Search results must use .srch-group grouping');
    }

    /** AC-5: search uses <mark> for highlighting */
    public function testSearchUsesMarkHighlight(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/search?q=' . urlencode('עגב'));
        $req = $req->withQueryParams(['q' => 'עגב']);
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('<mark>', $body, 'Search must use <mark> for highlight');
    }

    /** AC-5: search no-match state uses .srch-nomatch */
    public function testSearchNoMatch(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/search?q=xyznotfound123');
        $req = $req->withQueryParams(['q' => 'xyznotfound123']);
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('srch-nomatch', $body, 'No-match search must show .srch-nomatch');
    }

    /** AC-7 + MINOR F-04: search product rows must NOT show fake price range */
    public function testSearchNoFakeRange(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/search?q=' . urlencode('פלפל'));
        $req = $req->withQueryParams(['q' => 'פלפל']);
        $body = (string)$this->app->handle($req)->getBody();
        // price_min = price_max = price_current (shim) — should NOT render range "X–Y"
        // The template should show single price only, not min–max range in the search row
        $this->assertStringNotContainsString('price_min', $body, 'Search must not expose raw price_min key');
        $this->assertStringNotContainsString('price_max', $body, 'Search must not expose raw price_max key');
    }

    /** AC-6 + MINOR F-06: community is feed-less (no .community__feed) */
    public function testCommunityIsFeedLess(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/community');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringNotContainsString('community__feed', $body, 'Community must be feed-less');
    }

    /** AC-6: community has .comm-manifest */
    public function testCommunityHasManifest(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/community');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('comm-manifest', $body, 'Community must have .comm-manifest');
    }

    /** AC-6: community has .reqcard */
    public function testCommunityHasReqcard(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/community');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('reqcard', $body, 'Community must have .reqcard');
    }

    /** AC-4: hub home has .hub-grid and .modtile */
    public function testHubHomeHasModtileGrid(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('hub-grid', $body, 'Hub home must have .hub-grid');
        $this->assertStringContainsString('modtile', $body, 'Hub home must have .modtile');
    }

    /** AC-4: hub home has .hub-manifest */
    public function testHubHomeHasManifest(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('hub-manifest', $body, 'Hub home must have .hub-manifest');
    }

    /** AC-6: about page has .tier-row */
    public function testAboutHasTierRows(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/about');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('tier-row', $body, 'About must have .tier-row');
    }

    /** AC-1 + MINOR F-07: layout loads classb.css on Class B routes */
    public function testLayoutLoadsClassbCssOnHub(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('classb.css', $body, 'Layout must load classb.css on hub route');
    }

    /** AC-1 + MINOR F-07: layout loads classb.js on Class B routes */
    public function testLayoutLoadsClassbJsOnHub(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('classb.js', $body, 'Layout must load classb.js on hub route');
    }

    /** AC-3: market list has freshness pill */
    public function testMarketListHasFreshnessPill(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/market/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('fresh', $body, 'Market list must render freshness pill');
    }

    // ── F-2 FIX: community banner <img> present, no bare beige box ──────────

    /** F-2 fix: community page renders .comm-banner with an <img> child */
    public function testCommunityBannerHasImg(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/community');
        $body = (string)$this->app->handle($req)->getBody();
        // The .comm-banner div must contain an <img — image must exist for the box to render
        $this->assertMatchesRegularExpression(
            '#comm-banner[^>]*>[\s]*<img#',
            $body,
            'Community .comm-banner must contain an <img> — no bare beige box allowed'
        );
    }

    /** F-2 fix: community page must NOT render .comm-banner without an <img> inside */
    public function testCommunityNoBareBeigeBannerBox(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/community');
        $body = (string)$this->app->handle($req)->getBody();
        // A bare box would match comm-banner" followed only by whitespace then </div>
        $this->assertDoesNotMatchRegularExpression(
            '#class="comm-banner[^"]*"\s*aria-hidden="true"\s*>\s*</div>#',
            $body,
            'Community must never render a .comm-banner without image content'
        );
    }

    // ── F-1 FIX: hub intro width container ───────────────────────────────────

    /** F-1 fix: hub home has .hub-home__inner max-width wrapper */
    public function testHubHomeHasInnerWrapper(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('hub-home__inner', $body, 'Hub home must have .hub-home__inner width-cap wrapper (F-1 fix)');
    }

    // ── F-6 FIX: footer has no self-link on /community ──────────────────────

    /** F-6 fix: footer "קהילה" is not an <a href="/community"> when on /community */
    public function testFooterNoSelfLinkOnCommunity(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/community');
        $body = (string)$this->app->handle($req)->getBody();
        // Footer self-link pattern: <a href="/community"> inside sh__foot region.
        // We check that href="/community" does NOT appear inside a footer <a> tag.
        // The simplest reliable check: the footer span with aria-current should be present
        // instead of a link.
        $this->assertStringContainsString('aria-current="page"', $body,
            'Footer קהילה must use aria-current="page" span (not <a>) when on /community (F-6 fix)');
    }

    // ── F-5 FIX: market table <th> has no inline style= ─────────────────────

    /** F-5 fix / WP-CB-MOBILE FIX 3: market list table is the .mkt-table 3-col,
     *  styled via CSS classes (no inline style= on <th>). */
    public function testMarketTableThHasNoInlineStyle(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/market/');
        $body = (string)$this->app->handle($req)->getBody();
        // FIX 3: dense 3-col .mkt-table replaces the old .ptable on the market list.
        $this->assertStringContainsString('mkt-table', $body, 'Market list table must use the .mkt-table 3-col (FIX 3)');
        // Must NOT have inline style on <th>
        $this->assertDoesNotMatchRegularExpression(
            '#<th\s[^>]*style=#',
            $body,
            'Market table <th> must not use inline style= attribute (F-5 fix)'
        );
    }

    /** WP-CB-MOBILE D1: market list default view is TABLE (server-rendered). */
    public function testMarketListDefaultsToTableView(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/market/');
        $body = (string)$this->app->handle($req)->getBody();
        // The audience switch must mark the table option active by default (D1).
        $this->assertMatchesRegularExpression(
            '#is-table[^"]*is-active#',
            $body,
            'Market default view must be TABLE — table option active server-side (D1)'
        );
        // The cards grid must be hidden by default (display:none) and table visible.
        $this->assertMatchesRegularExpression(
            '#pcard-grid"\s+data-aud-view="cards"\s+style="display:none#',
            $body,
            'Cards grid must be hidden by default when the table view is the default (D1)'
        );
    }

    /** WP-CB-MOBILE FIX 3: the market list disclaimer is a collapsible <details> (closed default). */
    public function testMarketListDisclaimerCollapsible(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/market/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertMatchesRegularExpression(
            '#<details class="mkt-disc#',
            $body,
            'Market list disclaimer must render as a collapsible <details class="mkt-disc"> (FIX 3)'
        );
        // CLOSED by default → the <details> must not carry the `open` attribute.
        $this->assertDoesNotMatchRegularExpression(
            '#<details class="mkt-disc[^"]*"[^>]*\sopen#',
            $body,
            'Market list disclaimer must be CLOSED by default (no open attribute)'
        );
        // LOCKED copy preserved verbatim.
        $this->assertStringContainsString('מה זה? מאיפה זה? למה זה?', $body, 'Disclaimer LOCKED heading must be preserved');
    }

    // ── F-7 FIX: nav class has no trailing space ─────────────────────────────

    /** F-7 fix: nav link class attributes must not have trailing spaces */
    public function testNavClassNoTrailingSpace(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        // Trailing space in class: class="is-calc " or class="is-market "
        $this->assertDoesNotMatchRegularExpression(
            '#class="is-(?:calc|market)\s+"#',
            $body,
            'Nav link class must not have trailing space (e.g. "is-calc ") — F-7 fix'
        );
    }

    // ── WP-CB-UI-patch01: hub full-width / Field-Log tile ────────────────────

    /** WI-2: hub home contains Field Log tile with יומן השדה text */
    public function testHubHomeHasFieldLogTitle(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('יומן השדה', $body,
            'Hub home must include the Field Log tile with "יומן השדה"');
    }

    /** WI-2: hub home Field Log tile has "בפיתוח" badge */
    public function testHubHomeHasFieldLogBadge(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('בפיתוח', $body,
            'Hub home Field Log tile must show "בפיתוח"');
    }

    /** WI-2: hub home Field Log tile carries is-dev class */
    public function testHubHomeFieldLogHasIsDevClass(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('is-dev', $body,
            'Hub home Field Log tile must have the is-dev CSS class');
    }

    /** WI-2: hub home Field Log tile has no href (non-clickable) */
    public function testHubHomeFieldLogHasNoHref(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        // The tile must be a <div>, not an <a> — verify no <a … is-dev … href
        $this->assertDoesNotMatchRegularExpression(
            '#<a[^>]+is-dev[^>]+href#',
            $body,
            'Field Log tile must NOT have an href — it is a non-clickable teaser div'
        );
    }

    /** WI-2: classb.css .hub-grid uses auto-fit (not auto-fill) */
    public function testClassbCssUsesAutoFit(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/classb.css');
        // Confirm the hub-grid line now uses auto-fit
        $this->assertMatchesRegularExpression(
            '#hub-grid[^}]*auto-fit#s',
            $css,
            'classb.css .hub-grid must use auto-fit for full-width tile row'
        );
        // Confirm the hub-grid line no longer uses auto-fill
        $this->assertDoesNotMatchRegularExpression(
            '#hub-grid[^}]*auto-fill#s',
            $css,
            'classb.css .hub-grid must not use auto-fill (replaced by auto-fit)'
        );
    }

    // ── WP-CB-UI-patch01: crop-book density ──────────────────────────────────

    /** WI-1: /crop-book/ returns HTTP 200 */
    public function testCropBookEntryReturns200(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/');
        $res = $this->app->handle($req);
        $this->assertSame(200, $res->getStatusCode(), '/crop-book/ must return 200');
    }

    /** WP-CB-UI-REDESIGN (WI-3): /crop-book/ is the filtered crop index —
     *  .lead header + .grid card grid; the old .cb-hero/.cb-paths entry hub is
     *  folded into the compact .book-subnav (questions/family/search preserved). */
    public function testCropBookEntryHasCardsGrid(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('class="grid"', $body,
            '/crop-book/ must render the .cc card grid');
        $this->assertStringContainsString('book-subnav', $body,
            '/crop-book/ must preserve entry navigation in .book-subnav (questions/family/search)');
    }

    /** A1: crop-book-v1.css .cards-grid uses team_35 restored minmax(168px,1fr) */
    public function testCropBookCssUsesCompactGrid(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/crop-book-v1.css');
        // A1 (patch01 regression restore): team_35 canonical value is minmax(168px,1fr).
        // The old assertion (≤128px) was enforcing the shrunken patch01 size — updated to
        // assert the restored team_35 value per WP-CB-UI-FIDELITY fix A1.
        $this->assertStringContainsString(
            'minmax(168px, 1fr)',
            $css,
            'crop-book-v1.css .cards-grid must use team_35 restored minmax(168px, 1fr) track'
        );
    }

    // ── WP-CB-UI-patch01 WI-3: hub copy + system-wide terminology ────────────

    /** WI-3: hub home audience card label is "גנן" (not "גינאי ביתי") */
    public function testHubHomeGardenerLabelIsGnan(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('גנן', $body,
            'Hub home audience card must use "גנן" (not "גינאי ביתי")');
        $this->assertStringNotContainsString('גינאי ביתי', $body,
            'Hub home must not contain the old label "גינאי ביתי"');
    }

    /** WI-3: hub home uses "חקלאי מקומי" (not "חקלאי קטן") */
    public function testHubHomeUsesLocalFarmerTerm(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('חקלאי מקומי', $body,
            'Hub home must contain "חקלאי מקומי"');
        $this->assertStringNotContainsString('חקלאי קטן', $body,
            'Hub home must not contain the old term "חקלאי קטן"');
    }

    /** WI-3: hub home uses "חקלאות מקומית" (not "חקלאות קטנה") */
    public function testHubHomeUsesLocalAgricultureTerm(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('חקלאות מקומית', $body,
            'Hub home must contain "חקלאות מקומית"');
        $this->assertStringNotContainsString('חקלאות קטנה', $body,
            'Hub home must not contain the old term "חקלאות קטנה"');
    }

    /** WI-3: /about has no customer-facing Tend integration copy */
    public function testAboutHasNoTendIntegrationCopy(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/about');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringNotContainsString('חיבור Tend', $body,
            '/about must not contain "חיבור Tend" integration teaser');
        $this->assertStringNotContainsString('חיבור ל-Tend', $body,
            '/about must not contain "חיבור ל-Tend" integration copy');
    }

    // ── WP-CB-UI-patch01 WI-4: hub CTA section ───────────────────────────────

    /** WI-4 / WP-CB-MOBILE FIX 5: hub home has the .cta CTA-system section */
    public function testHubHomeHasCtaSection(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('class="cta"', $body,
            'Hub home must have the .cta CTA-system section (FIX 5)');
        // All three CTA flavors present: data (primary) · suggest (form) · WhatsApp.
        $this->assertStringContainsString('cta--data', $body, 'Hub CTA must include the primary data card');
        $this->assertStringContainsString('cta--suggest', $body, 'Hub CTA must include the suggestion form card');
        $this->assertStringContainsString('cta--wa', $body, 'Hub CTA must include the WhatsApp (custom) card');
    }

    /** WI-4: the primary data CTA links to /community (complete-missing-data offer) */
    public function testHubCtaHasCommunityLink(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertMatchesRegularExpression(
            '#cta--data.*href="/community"#s',
            $body,
            'Hub primary data CTA must link to /community'
        );
    }

    /** WI-4: the WhatsApp CTA (custom/paid only) uses a wa.me link */
    public function testHubCtaHasWhatsAppLink(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertMatchesRegularExpression(
            '#cta--wa.*wa\.me#s',
            $body,
            'Hub CTA must contain a wa.me WhatsApp link in the custom (.cta--wa) card'
        );
    }

    /** WI-4 / CTA SYSTEM: the suggestion CTA is an inline FORM, never WhatsApp */
    public function testHubCtaSuggestIsForm(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        // The .cta--suggest card must contain a <form>, not a wa.me link.
        $this->assertMatchesRegularExpression(
            '#cta--suggest.*<form#s',
            $body,
            'Suggestion CTA must be an inline form (never WhatsApp)'
        );
    }

    /** WI-4: hub CTA has the complete-missing-data primary copy */
    public function testHubCtaHasContributionText(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('עזרו להשלים את המידע', $body,
            'Hub primary CTA must include the complete-missing-data offer text');
    }

    /** WI-4: hub CTA has the custom-solution (WhatsApp) copy */
    public function testHubCtaHasFeatureRequestText(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('פתרון מותאם לחווה', $body,
            'Hub CTA must include the custom-solution (WhatsApp) offer text');
    }

    // ── WP-CB-UI-patch01 WI-7: mobile horizontal overflow fixes ─────────────

    /** WI-7: market detail wraps .phist table in .phist-wrap for overflow-x:auto */
    public function testMarketDetailHistoryHasScrollWrapper(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/market/tomato');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('phist-wrap', $body,
            'Market detail must render .phist-wrap scroll container around .phist table (WI-7)');
    }

    /** WI-7: classb.css defines .phist-wrap with overflow-x:auto */
    public function testPhistwrapCssDefinition(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/classb.css');
        $this->assertMatchesRegularExpression(
            '#phist-wrap[^}]*overflow-x\s*:\s*auto#s',
            $css,
            'classb.css must define .phist-wrap with overflow-x:auto (WI-7)'
        );
    }

    /** WI-7: classb.css .pgraph__top uses flex-wrap to prevent rangesel overflow */
    public function testPgraphTopFlexWrap(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/classb.css');
        $this->assertMatchesRegularExpression(
            '#pgraph__top[^}]*flex-wrap\s*:\s*wrap#s',
            $css,
            'classb.css .pgraph__top must use flex-wrap:wrap so rangesel wraps on narrow screens (WI-7)'
        );
    }

    // ── F-REA-001: basket unit labels ────────────────────────────────────────

    /** F-REA-001: sfa_unit_label maps basket_large to לסל (not raw English) */
    public function testSfaUnitLabelBasketLarge(): void
    {
        // Load the template into a subprocess scope by requiring it with the helper present.
        // We call the function directly after inclusion. Guard against re-definition.
        if (!function_exists('sfa_unit_label')) {
            // Define the function from the source file — safe because PHPUnit runs each test
            // in the same process; function_exists guard in template prevents redefinition.
            require __DIR__ . '/../templates/pages/market_list.php';
        }
        $this->assertSame('לסל', sfa_unit_label('basket_large'),
            'F-REA-001: basket_large must map to לסל');
        $this->assertSame('לסל', sfa_unit_label('basket_medium'),
            'F-REA-001: basket_medium must map to לסל');
        $this->assertSame('לסל', sfa_unit_label('basket_small'),
            'F-REA-001: basket_small must map to לסל');
    }

    /** F-REA-001: sfa_unit_label hardened default — raw English snake_case returns ליחידה not לXxx */
    public function testSfaUnitLabelHardenedDefault(): void
    {
        if (!function_exists('sfa_unit_label')) {
            require __DIR__ . '/../templates/pages/market_list.php';
        }
        $result = sfa_unit_label('some_english_token');
        $this->assertSame('ליחידה', $result,
            'F-REA-001: unmapped English snake_case unit must return ליחידה, not לsome_english_token');
        // Existing Hebrew passthrough must still work
        $this->assertSame('לסל גדול', sfa_unit_label('סל גדול'),
            'Hebrew passthrough must still prepend ל');
        // Known units still work
        $this->assertSame('לק״ג', sfa_unit_label('kg'));
    }

    /** F-REA-001: market list page for a basket product does not leak raw English unit */
    public function testMarketListBasketProductNoEnglishUnit(): void
    {
        // Seed a basket product
        $this->pdo->exec("INSERT OR IGNORE INTO products
            (id,slug,hebrew_name,category,unit,last_price,last_price_date,freshness_days,payload_json,last_pushed_at)
            VALUES (50,'basket-mix','עשבי תיבול','baskets','basket_large',25.0,'2026-06-01',1,'{}','2026-06-01')");
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/market/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringNotContainsString('לbasket_large', $body,
            'F-REA-001: market list must not show raw לbasket_large');
        $this->assertStringContainsString('לסל', $body,
            'F-REA-001: market list must show לסל for basket_large products');
    }

    // ── F-REA-002: search results show watercolor art ────────────────────────

    /** F-REA-002: /crop-book/search result for a crop with watercolor has icon_url set */
    public function testSearchResultWatercolorPresentForKnownCrop(): void
    {
        // 'tomato' is in WC_ART map → icon_url should be populated
        $this->pdo->exec("INSERT OR IGNORE INTO crops
            (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at)
            VALUES (2,'tomato','עגבנייה','Solanum lycopersicum','סולניים','vegetables','summer',70,95,'{}','2026-06-01')");
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/search');
        $req  = $req->withQueryParams(['q' => 'עגבנייה']);
        $body = (string)$this->app->handle($req)->getBody();
        // crop_card renders img.crop-card__art when icon_url is set
        $this->assertStringContainsString('crop-card__art', $body,
            'F-REA-002: search result for tomato must render watercolor img (crop-card__art)');
        $this->assertStringContainsString('wc-tomato.png', $body,
            'F-REA-002: search result for tomato must include wc-tomato.png');
    }

    /** F-REA-002: /crop-book/search result for a crop with NO watercolor still renders (glyph fallback) */
    public function testSearchResultFallsBackToGlyphForUnknownCrop(): void
    {
        $this->pdo->exec("INSERT OR IGNORE INTO crops
            (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at)
            VALUES (99,'rare-herb','עשב נדיר','Rarus herbarius','','herbs','',null,null,'{}','2026-06-01')");
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/search');
        $req  = $req->withQueryParams(['q' => 'עשב נדיר']);
        $body = (string)$this->app->handle($req)->getBody();
        // Should NOT render crop-card__art (no watercolor), but page must still render
        $this->assertStringNotContainsString('crop-card__art', $body,
            'F-REA-002: crop with no watercolor must NOT render crop-card__art');
        $this->assertStringContainsString('gj-cropcard', $body,
            'F-REA-002: glyph fallback card must still render');
    }

    // ── F-REA-003: hub module tile eyebrows — no English mono module-id ───────

    /** F-REA-003: hub home must not show English mono module-id in tile title (CROP-BOOK etc.) */
    public function testHubHomeTileNoEnglishModuleId(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        // The <small>CROP-BOOK</small> etc. must have been removed from modtile__title
        $this->assertDoesNotMatchRegularExpression(
            '#modtile__title[^<]*<small>[A-Z\-]+</small>#',
            $body,
            'F-REA-003: modtile__title must not contain English-only <small> module-id badge'
        );
    }

    // ── Item 5: legacy /crop-book/table redirects ────────────────────────────

    /** Item 5: /crop-book/table?category=summer 301-redirects to /crop-book/?season=summer */
    public function testTableViewLegacySummerRedirects(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/table');
        $req = $req->withQueryParams(['category' => 'summer']);
        $res = $this->app->handle($req);
        $this->assertSame(301, $res->getStatusCode(),
            'Item 5: /crop-book/table?category=summer must 301-redirect');
        $this->assertStringContainsString('/crop-book/?season=summer', $res->getHeaderLine('Location'),
            'Item 5: redirect must go to /crop-book/?season=summer');
    }

    /** Item 5: /crop-book/table?category=fast 301-redirects to /crop-book/?dtm_max=60 */
    public function testTableViewLegacyFastRedirects(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/table');
        $req = $req->withQueryParams(['category' => 'fast']);
        $res = $this->app->handle($req);
        $this->assertSame(301, $res->getStatusCode(),
            'Item 5: /crop-book/table?category=fast must 301-redirect');
        $this->assertStringContainsString('/crop-book/?dtm_max=60', $res->getHeaderLine('Location'),
            'Item 5: redirect must go to /crop-book/?dtm_max=60');
    }

    /** Item 5: /crop-book/table?category=beginner 301-redirects to /crop-book/ */
    public function testTableViewLegacyBeginnerRedirects(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/table');
        $req = $req->withQueryParams(['category' => 'beginner']);
        $res = $this->app->handle($req);
        $this->assertSame(301, $res->getStatusCode(),
            'Item 5: /crop-book/table?category=beginner must 301-redirect');
        $this->assertStringContainsString('/crop-book/', $res->getHeaderLine('Location'),
            'Item 5: redirect must go to /crop-book/');
    }

    /** Item 5: /crop-book/table?category=vegetables (real botanical) still returns 200 */
    public function testTableViewRealCategoryNotRedirected(): void
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/table');
        $req = $req->withQueryParams(['category' => 'vegetables']);
        $res = $this->app->handle($req);
        $this->assertSame(200, $res->getStatusCode(),
            'Item 5: real botanical category must still return 200 (not redirected)');
    }
}
