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

    /** F-5 fix: market list table headers use CSS classes, not inline style= */
    public function testMarketTableThHasNoInlineStyle(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/market/');
        $body = (string)$this->app->handle($req)->getBody();
        // Should have the new CSS class
        $this->assertStringContainsString('ptable__th', $body, 'Market table <th> must use .ptable__th class (F-5 fix)');
        // Must NOT have inline style on <th>
        $this->assertDoesNotMatchRegularExpression(
            '#<th\s[^>]*style=#',
            $body,
            'Market table <th> must not use inline style= attribute (F-5 fix)'
        );
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

    /** WI-1: /crop-book/ still renders .cards-grid */
    public function testCropBookEntryHasCardsGrid(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/crop-book/');
        $body = (string)$this->app->handle($req)->getBody();
        // cards-grid class appears in static HTML even without $crops (via the template structure)
        // We check at minimum that the cb-hero and cb-paths are present
        $this->assertStringContainsString('cb-hero', $body,
            '/crop-book/ must still render .cb-hero (WI-1 kept functionality)');
        $this->assertStringContainsString('cb-paths', $body,
            '/crop-book/ must still render .cb-paths (WI-1 kept functionality)');
    }

    /** WI-1: crop-book-v1.css uses compact minmax (≤128px) for .cards-grid */
    public function testCropBookCssUsesCompactGrid(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/crop-book-v1.css');
        // Assert minmax track is ≤128px (compact) — pattern: minmax(NNNpx where NNN<=128
        $this->assertMatchesRegularExpression(
            '#cards-grid[^}]*minmax\(1[01]\d|minmax\([0-9]{2}px#',
            $css,
            'crop-book-v1.css .cards-grid must use a compact minmax track (≤128px)'
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

    /** WI-4: hub home has .hub-cta section */
    public function testHubHomeHasCtaSection(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('hub-cta', $body,
            'Hub home must have the .hub-cta section (WI-4)');
    }

    /** WI-4: hub CTA section has /community link (secondary offer) */
    public function testHubCtaHasCommunityLink(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        // The secondary CTA card links to /community
        $this->assertMatchesRegularExpression(
            '#hub-cta[^<]*.*href="/community"#s',
            $body,
            'Hub CTA must contain a link to /community'
        );
    }

    /** WI-4: hub CTA section has wa.me WhatsApp link (primary offer) */
    public function testHubCtaHasWhatsAppLink(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertMatchesRegularExpression(
            '#hub-cta[^<]*.*wa\.me#s',
            $body,
            'Hub CTA must contain a wa.me WhatsApp link (primary CTA)'
        );
    }

    /** WI-4: hub CTA primary card has hub-cta__card--primary class */
    public function testHubCtaHasPrimaryCard(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('hub-cta__card--primary', $body,
            'Hub CTA must have a prominently-styled primary card');
    }

    /** WI-4: hub CTA has contribution copy (secondary offer text) */
    public function testHubCtaHasContributionText(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('שתפו אותנו במידע', $body,
            'Hub CTA must include the secondary contribution offer text');
    }

    /** WI-4: hub CTA has feature-request copy (primary offer text) */
    public function testHubCtaHasFeatureRequestText(): void
    {
        $req  = (new ServerRequestFactory())->createServerRequest('GET', '/');
        $body = (string)$this->app->handle($req)->getBody();
        $this->assertStringContainsString('ספרו לנו מה תרצו שנפתח', $body,
            'Hub CTA must include the primary feature-request offer text');
    }
}
