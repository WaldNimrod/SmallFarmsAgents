<?php
declare(strict_types=1);

namespace SFA\Tests;

use PDO;
use PHPUnit\Framework\TestCase;
use SFA\Bootstrap;
use Slim\Psr7\Factory\ServerRequestFactory;

/**
 * CropBookV1RouteTest — WP-CB-1 route smoke tests.
 *
 * Tests:
 *   - GET /api/v1/assumptions returns JSON with germination_rate + bed_width
 *   - POST /api/v1/contribute with kind=request-info returns 200
 *   - GET /crop-book/ with ?view=cards returns 200
 *   - GET /crop-book/ with ?view=table returns 200
 *   - GET /crop-book/{slug}/?depth=simple returns 200
 *   - GET /crop-book/{slug}/?depth=full returns 200
 *   - GET /crop-book/{slug}/?depth=drill returns 200
 *   - GET /calc/ returns 200 (dashboard)
 *
 * @see DISPATCH §7
 */
final class CropBookV1RouteTest extends TestCase
{
    private \Slim\App $app;
    private PDO $pdo;

    protected function setUp(): void
    {
        $this->app = Bootstrap::createApp();
        (require __DIR__ . '/../app/routes.php')($this->app);
        $this->pdo = $this->app->getContainer()->get(PDO::class);

        $this->pdo->exec('CREATE TABLE IF NOT EXISTS crops (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, scientific_name TEXT, family_name_he TEXT, category TEXT, season TEXT, dtm_min INTEGER, dtm_max INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS crop_varieties (id INTEGER PRIMARY KEY, crop_id INTEGER, name TEXT, payload_json TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, hebrew_name TEXT, category TEXT, unit TEXT, last_price REAL, last_price_date TEXT, freshness_days INTEGER, payload_json TEXT, last_pushed_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS product_prices (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, price_date TEXT, price REAL, source TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS ingest_log (idempotency_key TEXT PRIMARY KEY, table_name TEXT, applied_at TEXT, row_count INTEGER, status TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT)');
        $this->pdo->exec('CREATE TABLE IF NOT EXISTS cover_crops (id INTEGER PRIMARY KEY, name_he TEXT, name_en TEXT, category TEXT, sow_window TEXT, total_days_garden INTEGER, survives_winter INTEGER, notes TEXT)');

        $this->pdo->exec("INSERT OR IGNORE INTO crops (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at) VALUES
            (1,'lettuce','חסה','Lactuca sativa','חסתיים','vegetables','winter',45,60,'{}','2026-05-31'),
            (2,'radish','צנונית','Raphanus sativus','מצליבים','vegetables','spring',25,35,'{}','2026-05-31')");

        $this->pdo->exec("INSERT OR IGNORE INTO crop_varieties (id,crop_id,name,payload_json) VALUES (101,1,'Batavian','{}')");

        // Rich-payload crop — exercises the migrated Deep-panel sections
        // (companions/storage/harvest/agronomy + general notes + market_link +
        // timeline). Regression guard for the WP-CB-MOBILE crop-page 500:
        // crop_storage.php must NOT clobber the page-level $notes array (TypeError
        // on array_filter). Empty-payload crops never hit this path.
        $richPayload = json_encode([
            'companions' => [
                ['slug' => 'radishes', 'name_he' => 'צנונית', 'compatibility' => 'beneficial'],
                ['slug' => 'fennel',   'name_he' => 'שומר',   'compatibility' => 'antagonistic', 'notes' => 'מתחרה'],
            ],
            'storage'    => ['temp' => ['min' => 0, 'max' => 4], 'life_days' => ['min' => 7, 'max' => 14], 'notes' => 'אחסון בקירור'],
            'harvest'    => ['harvest_window_max_days' => 21],
            'agronomy'   => ['planting_method' => 'direct'],
            'notes'      => [
                ['note_type' => 'tip',     'body_text' => 'גידול קל',      'trust_tier' => 'PR'],
                ['note_type' => 'pest_disease', 'body_text' => 'כנימות', 'trust_tier' => 'WR'],
            ],
            'market_link' => ['slug' => 'richcrop', 'price_current' => 12.5, 'source_count' => 3],
            'timeline'    => ['prep_pct' => 10, 'grow_pct' => 70, 'harv_pct' => 20, 'harv_days' => 14, 'week_labels' => ['1', '2', '3']],
        ], JSON_UNESCAPED_UNICODE);
        $st = $this->pdo->prepare("INSERT OR IGNORE INTO crops (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at) VALUES (3,'richcrop','חסה עשירה','Lactuca sativa','חסתיים','vegetables','winter',45,60,?,'2026-05-31')");
        $st->execute([$richPayload]);
        $this->pdo->exec("INSERT OR IGNORE INTO crop_varieties (id,crop_id,name,payload_json) VALUES (301,3,'V1','{\"agronomy\":{\"days_to_maturity\":55}}')");
    }

    private function get(string $path): \Psr\Http\Message\ResponseInterface
    {
        $req = (new ServerRequestFactory())->createServerRequest('GET', $path);
        return $this->app->handle($req);
    }

    private function post(string $path, array $data): \Psr\Http\Message\ResponseInterface
    {
        $req = (new ServerRequestFactory())
            ->createServerRequest('POST', $path)
            ->withHeader('Content-Type', 'application/json')
            ->withParsedBody($data);
        return $this->app->handle($req);
    }

    // ── assumptions endpoint ──────────────────────────────────────

    public function testAssumptionsEndpointReturns200(): void
    {
        $res = $this->get('/api/v1/assumptions');
        $this->assertSame(200, $res->getStatusCode(), '/api/v1/assumptions must return 200');
    }

    public function testAssumptionsEndpointReturnsJson(): void
    {
        $res  = $this->get('/api/v1/assumptions');
        $body = json_decode((string)$res->getBody(), true);
        $this->assertIsArray($body);
        $this->assertArrayHasKey('germination_rate', $body, 'germination_rate must be in registry');
        $this->assertArrayHasKey('bed_width', $body,       'bed_width must be in registry');
    }

    public function testAssumptionsHasPostUrlForLaunchBlockers(): void
    {
        $res  = $this->get('/api/v1/assumptions');
        $body = json_decode((string)$res->getBody(), true);
        // Launch-blocking: germination_rate + bed_width MUST have post_url
        $this->assertNotNull($body['germination_rate']['post_url'],
            'germination_rate must have post_url (launch-blocking)');
        $this->assertNotNull($body['bed_width']['post_url'],
            'bed_width must have post_url (launch-blocking)');
    }

    // ── contribute endpoint ───────────────────────────────────────

    public function testContributeReturns200ForRequestInfo(): void
    {
        $res = $this->post('/api/v1/contribute', [
            'kind'       => 'request-info',
            'field_name' => 'seeds_per_g',
            'crop_slug'  => 'lettuce',
        ]);
        $this->assertSame(200, $res->getStatusCode());
        $body = json_decode((string)$res->getBody(), true);
        $this->assertTrue($body['ok'] ?? false);
    }

    public function testContributeReturns400ForUnknownKind(): void
    {
        $res = $this->post('/api/v1/contribute', [
            'kind' => 'unknown-kind',
        ]);
        $this->assertSame(400, $res->getStatusCode());
    }

    // ── crop-book index routes ────────────────────────────────────

    public function testBookIndexCardsView(): void
    {
        $res = $this->get('/crop-book/?view=cards');
        $this->assertSame(200, $res->getStatusCode(), 'Crop-book cards view must return 200');
        $html = (string)$res->getBody();
        $this->assertStringContainsString('aud__opt', $html, 'Must include audience switch');
    }

    public function testBookIndexTableView(): void
    {
        $res = $this->get('/crop-book/?view=table');
        $this->assertSame(200, $res->getStatusCode(), 'Crop-book table view must return 200');
        $html = (string)$res->getBody();
        $this->assertStringContainsString('ptable', $html, 'Table view must include .ptable');
    }

    // ── server-side filters (WP-CB-1-patch01) ─────────────────────

    public function testBookIndexFilterByFamily(): void
    {
        // Seed: lettuce=חסתיים, radish=מצליבים. Filter family=מצליבים → only radish.
        $res  = $this->get('/crop-book/?family=' . rawurlencode('מצליבים'));
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('צנונית', $html, 'family filter must keep radish');
        $this->assertStringNotContainsString('/crop-book/lettuce/', $html, 'family filter must drop lettuce');
    }

    public function testBookIndexFilterByDtmMax(): void
    {
        // lettuce dtm_max=60, radish dtm_max=35. dtm_max=40 → only radish.
        $res  = $this->get('/crop-book/?dtm_max=40');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('/crop-book/radish/', $html, 'dtm_max=40 keeps radish (35)');
        $this->assertStringNotContainsString('/crop-book/lettuce/', $html, 'dtm_max=40 drops lettuce (60)');
    }

    public function testBookIndexFilterByText(): void
    {
        $res  = $this->get('/crop-book/?q=' . rawurlencode('חסה'));
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('/crop-book/lettuce/', $html, 'q=חסה keeps lettuce');
        $this->assertStringNotContainsString('/crop-book/radish/', $html, 'q=חסה drops radish');
    }

    public function testBookIndexFilterEmptyStateStillShowsForm(): void
    {
        // No crop matches → empty-state + the filter form must still render (recoverable).
        $res  = $this->get('/crop-book/?q=' . rawurlencode('zzzznomatch'));
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('cb-empty', $html, '0-result must show empty-state');
        $this->assertStringContainsString('method="get"', $html, '0-result must still show filter form');
    }

    // ── /calc export (WP-CB-1-patch01) ────────────────────────────

    public function testCalcExportCsvReturnsCsv(): void
    {
        $res = $this->get('/calc/export.csv?crop=' . rawurlencode('עגבנייה') . '&beds=10&rows[' . rawurlencode('יבול כולל') . ']=' . rawurlencode('105 ק"ג'));
        $this->assertSame(200, $res->getStatusCode());
        $this->assertStringContainsString('text/csv', $res->getHeaderLine('Content-Type'));
        $this->assertStringContainsString('attachment', $res->getHeaderLine('Content-Disposition'));
        $body = (string)$res->getBody();
        $this->assertStringContainsString('עגבנייה', $body, 'CSV must include the crop');
        $this->assertStringContainsString('יבול כולל', $body, 'CSV must include summary rows');
    }

    public function testCalcExportCsvEmptyPlanStillValid(): void
    {
        $res = $this->get('/calc/export.csv');
        $this->assertSame(200, $res->getStatusCode(), 'empty plan still returns a valid CSV');
        $this->assertStringContainsString('text/csv', $res->getHeaderLine('Content-Type'));
    }

    public function testCalcExportPrintReturnsPrintHtml(): void
    {
        // WP-CB-UI-ALIGN R3: PDF print moved off the .pdf extension (uPress/Apache 404s
        // .pdf to Slim) to the extension-less /calc/print route. (Was /calc/export.pdf.)
        $res = $this->get('/calc/print?crop=' . rawurlencode('חסה') . '&beds=5');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('window.print', $html, 'print route returns a print-friendly auto-print page');
        $this->assertStringContainsString('חסה', $html, 'print sheet includes the crop');
    }

    // ── crop page depths ──────────────────────────────────────────

    /**
     * Regression: a crop carrying real payload (companions/storage/harvest/notes/
     * market_link/timeline) must render 200 at every depth. Guards the WP-CB-MOBILE
     * crop-page 500 (crop_storage.php clobbered the shared $notes array → array_filter
     * TypeError). Empty-payload crops did not exercise this path.
     */
    public function testBookCropRichPayloadRendersAllDepths(): void
    {
        foreach (['', '?depth=simple', '?depth=full', '?depth=deep'] as $q) {
            $res = $this->get('/crop-book/richcrop/' . $q);
            $this->assertSame(200, $res->getStatusCode(), "richcrop must render 200 for '$q'");
        }
    }

    public function testBookCropRichPayloadDeepShowsMigratedSections(): void
    {
        $res  = $this->get('/crop-book/richcrop/?depth=deep');
        $html = (string)$res->getBody();
        $this->assertStringContainsString('cb-storage', $html, 'storage section migrated into Deep');
        $this->assertStringContainsString('cb-companions', $html, 'companions migrated into Deep');
        $this->assertStringContainsString('אחסון בקירור', $html, 'storage notes render (not clobbering page notes)');
        $this->assertStringContainsString('גידול קל', $html, 'general public note surfaced in Deep');
    }

    public function testBookCropSimpleDepth(): void
    {
        // WP-CB-MOBILE Stage 2: Simple is now genuinely minimal — essentials
        // strip + calendar + one-key-per-topic keylist; the full stat block
        // (headvals) was intentionally removed (Simple ⊂ Full ⊂ Deep).
        $res  = $this->get('/crop-book/lettuce/?depth=simple');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('sh__depths', $html, 'Must include the header depth segmented control');
        $this->assertStringContainsString('class="ess"', $html, 'Simple depth must include the essentials chip strip');
        $this->assertStringContainsString('class="keylist"', $html, 'Simple depth must include the one-key-per-topic list');
        $this->assertStringNotContainsString('class="headvals"', $html, 'Simple depth must NOT carry the full stat block (Stage 2 IA)');
    }

    public function testBookCropFullDepth(): void
    {
        $res  = $this->get('/crop-book/lettuce/?depth=full');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('topic', $html, 'Full depth must include topic sections');
    }

    public function testFieldStateLightsUpFromVarietyPayload(): void
    {
        // F-UI-01: with NO crop_field_enrichment table (mirror reality), prov cues must
        // still light up from the default variety payload (agronomy + field_state).
        $this->pdo->exec("INSERT OR IGNORE INTO crops (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at) VALUES
            (9,'fui-crop','בדיקה','Test sp.','חסתיים','vegetables','winter',40,55,'{}','2026-06-01')");
        // default variety carries agronomy value + VALIDATED state for yield_per_bed_m.
        $payload = json_encode([
            'is_default'  => true,
            'agronomy'    => ['yield_per_bed_m' => 4.2, 'days_to_maturity' => 55],
            'field_state' => ['yield_per_bed_m' => 'VALIDATED', 'days_to_maturity' => 'VALIDATED'],
        ], JSON_UNESCAPED_UNICODE);
        $this->pdo->exec("INSERT OR IGNORE INTO crop_varieties (id,crop_id,name,payload_json) VALUES (901,9,'def'," . $this->pdo->quote($payload) . ")");

        $res  = $this->get('/crop-book/fui-crop/?depth=simple');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        // 4.2 yield must surface as a validated value (not "—" missing) in the headline values.
        $this->assertStringContainsString('4.2', $html, 'yield value from variety payload must render');
        $this->assertStringContainsString('pv-validated', $html, 'VALIDATED state from payload must drive the cue');
    }

    public function testBookCropDrillDepth(): void
    {
        // WP-CB-MOBILE Stage 2: legacy ?depth=drill is a back-compat alias for the
        // deepest view; controller normalises it to 'deep'. Still 200 + vtable.
        $res  = $this->get('/crop-book/lettuce/?depth=drill');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('vtable', $html, 'Drill (→deep) depth must include variety table');
    }

    public function testBookCropDeepDepth(): void
    {
        // WP-CB-MOBILE Stage 2: Deep is the canonical third state. Same topic
        // structure as Full (.topic) + the variety comparison table (.vtable)
        // + the EX/PR/WR source trust-hierarchy explainer.
        $res  = $this->get('/crop-book/lettuce/?depth=deep');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('vtable', $html, 'Deep depth must include the variety comparison table');
        $this->assertStringContainsString('data-depth-view="deep"', $html, 'Deep depth view container must render');
        $this->assertStringContainsString('היררכיית מקורות', $html, 'Deep depth must include the source trust-hierarchy explainer');
    }

    public function testBookCropDefaultDepth(): void
    {
        // No depth param — should default to simple
        $res  = $this->get('/crop-book/lettuce/');
        $this->assertSame(200, $res->getStatusCode());
    }

    /**
     * WP-CB-MOBILE Stage 2: Deep depth renders the per-datum variety range
     * (.rng) when ≥2 varieties carry distinct numeric values. The EX/PR/WR
     * source pill row is HONEST — it only renders when the crop's fields carry
     * a real winning_source_class. With the MySQL-mirror reality (values come
     * from the variety payload, source class ''), the source row is correctly
     * OMITTED rather than fabricated. This locks the no-fabrication contract.
     */
    public function testDeepDepthRendersVarietyRangeAndHonestSources(): void
    {
        $this->pdo->exec("INSERT OR IGNORE INTO crops (id,slug,hebrew_name,scientific_name,family_name_he,category,season,dtm_min,dtm_max,payload_json,last_pushed_at) VALUES
            (7,'deep-crop','עומק','Deepus sp.','חסתיים','vegetables','winter',40,58,'{}','2026-06-01')");
        // Two varieties with DISTINCT days_to_maturity → a real range 52–58.
        $v1 = json_encode([
            'is_default'  => true,
            'agronomy'    => ['days_to_maturity' => 52, 'yield_per_bed_m' => 3.6],
            'field_state' => ['days_to_maturity' => 'VALIDATED', 'yield_per_bed_m' => 'VALIDATED'],
        ], JSON_UNESCAPED_UNICODE);
        $v2 = json_encode(['agronomy' => ['days_to_maturity' => 58, 'yield_per_bed_m' => 3.2]], JSON_UNESCAPED_UNICODE);
        $this->pdo->exec("INSERT OR IGNORE INTO crop_varieties (id,crop_id,name,payload_json) VALUES
            (701,7,'נח 408'," . $this->pdo->quote($v1) . "),(702,7,'קייטנית'," . $this->pdo->quote($v2) . ")");

        $res  = $this->get('/crop-book/deep-crop/?depth=deep');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        // Range line present with the across-variety span (52–58 for DTM).
        $this->assertStringContainsString('class="rng"', $html, 'Deep depth must render the variety-range line when ≥2 varieties differ');
        $this->assertStringContainsString('52–58', $html, 'Deep range must reflect the across-variety min–max');
        // No fabricated provenance: payload-sourced values carry source class '' → no pill row.
        $this->assertStringNotContainsString('srcpill', $html, 'Source pills must NOT be fabricated when no winning_source_class exists');
    }

    // ── WI-7: mobile horizontal overflow responsive wrappers ──────

    /** WI-7: /crop-book/table wraps .dt-table in .dt-table-wrap for overflow-x:auto */
    public function testBookTableHasDtTableWrap(): void
    {
        $res  = $this->get('/crop-book/table');
        $this->assertSame(200, $res->getStatusCode(), '/crop-book/table must return 200');
        $html = (string)$res->getBody();
        $this->assertStringContainsString('dt-table-wrap', $html,
            '/crop-book/table must render .dt-table-wrap for horizontal-scroll at mobile (WI-7)');
    }

    /** WI-7: crop-book-deep.css defines .dt-table-wrap with overflow-x:auto */
    public function testDtTableWrapCssDefinition(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/crop-book-deep.css');
        $this->assertMatchesRegularExpression(
            '#dt-table-wrap[^}]*overflow-x\s*:\s*auto#s',
            $css,
            'crop-book-deep.css must define .dt-table-wrap with overflow-x:auto (WI-7)'
        );
    }

    /** WI-7: .dt-table has min-width to keep columns readable inside scroll container */
    public function testDtTableMinWidth(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/crop-book-deep.css');
        $this->assertMatchesRegularExpression(
            '#\.dt-table\b[^}]*min-width#s',
            $css,
            'crop-book-deep.css .dt-table must have min-width for scrollable columns (WI-7)'
        );
    }

    /** WI-7: /crop-book/{slug} simple depth renders .cb-crop-detail wrapper */
    public function testBookCropSimpleHasCropDetailWrapper(): void
    {
        $res  = $this->get('/crop-book/lettuce/?depth=simple');
        $this->assertSame(200, $res->getStatusCode());
        $html = (string)$res->getBody();
        $this->assertStringContainsString('cb-crop-detail', $html,
            '/crop-book/{slug} must render .cb-crop-detail container (WI-7 overflow guard)');
    }

    /** WI-7: crop-book-v1.css has overflow-x guard for .cb-crop-detail (hidden or clip) */
    public function testCropDetailOverflowGuard(): void
    {
        $css = file_get_contents(__DIR__ . '/../public_assets/css/crop-book-v1.css');
        $this->assertMatchesRegularExpression(
            '#cb-crop-detail[^}]*overflow-x\s*:\s*(hidden|clip)#s',
            $css,
            'crop-book-v1.css .cb-crop-detail must have overflow-x:hidden or overflow-x:clip guard (WI-7)'
        );
    }

    // ── calculator dashboard ──────────────────────────────────────

    /**
     * WP-CB-MOBILE FIX 6: /calc/ is the "define the question" builder.
     * The scope carries both states (ask|result) and the goal catalog.
     */
    public function testCalcDashReturns200(): void
    {
        $res  = $this->get('/calc/');
        $this->assertSame(200, $res->getStatusCode(), '/calc/ must return 200');
        $html = (string)$res->getBody();
        // scope + state machine
        $this->assertStringContainsString('id="calc-scope"', $html, 'Calc page must render the #calc-scope builder');
        $this->assertStringContainsString('data-calc-state="ask"', $html, 'Calc scope must start in the ask state');
        // ASK builder: 6-button goal grid + the "more" dropdown
        $this->assertStringContainsString('qb-goal--grid', $html, 'Calc ask state must render the .qb-goal--grid');
        $this->assertStringContainsString('id="qb-more"', $html, 'Calc ask state must render the .qb-more <select>');
        $this->assertStringContainsString('id="qb-go"', $html, 'Calc ask state must render the compute (.qb__go) button');
        // RESULT state: session, answer, breakdown, assumptions entry, export-all
        $this->assertStringContainsString('id="qb-session"', $html, 'Calc result state must render the .qb-session');
        $this->assertStringContainsString('id="qb-answer"', $html, 'Calc result state must render the .qb-answer');
        $this->assertStringContainsString('qb-assum__edit', $html, 'Calc result must expose the AssumptionField edit entry point');
        $this->assertStringContainsString('id="qb-export-pdf"', $html, 'Calc result must render the session export-all (PDF)');
        // hidden compute engine reuses the existing CALC registry
        $this->assertStringContainsString('id="qb-engine"', $html, 'Calc page must render the hidden #qb-engine compute panel');
    }

    /** FIX 6: the goal catalog must map all 14 calculators (6 primary + 8 dropdown). */
    public function testCalcGoalCatalogHasAllFourteen(): void
    {
        $html = (string)$this->get('/calc/')->getBody();
        $this->assertMatchesRegularExpression('#data-calc-goals=\'[^\']+\'#', $html,
            'Calc scope must carry the data-calc-goals catalog');
        if (preg_match('#data-calc-goals=\'([^\']+)\'#', $html, $m)) {
            $goals = json_decode(html_entity_decode($m[1], ENT_QUOTES), true);
            $this->assertIsArray($goals);
            $this->assertCount(14, $goals, 'Goal catalog must cover all 14 calculators');
            // Goals with live client-side CALC math are flagged not-soon with a non-empty kind.
            // WP-CB-CALC Phase A: transplants(#2) ported -> 7 live (was 6: seed/yield/revenue/pop/fert/beds).
            $live = array_values(array_filter($goals, static fn ($g) => !($g['soon'] ?? true) && ($g['kind'] ?? '') !== ''));
            $liveKinds = array_map(static fn ($g) => $g['kind'], $live);
            sort($liveKinds);
            $this->assertSame(
                ['beds', 'fert', 'pop', 'revenue', 'seed', 'transplants', 'yield'],
                $liveKinds,
                'Live CALC[kind] goals (WP-CB-CALC Phase A added transplants)'
            );
        }
    }

    // ── Decision A regression: season filter reads variety months, not crop payload ──

    /**
     * Regression test for Decision A bug fix (2026-06-04):
     * sowing_months lives in crop_varieties.payload_json['agronomy'], NOT in
     * crops.payload_json. Before the fix, season filter always returned 0 crops.
     *
     * Seeds:
     *   crop A (pepper, id=10)  → variety months [3,4,5]  → spring
     *   crop B (tomato, id=11)  → variety months [6,7,8]  → summer
     *   crop C (basil,  id=12)  → no variety month data   → no season match
     *
     * Asserts:
     *   ?season=summer → B present, A absent, C absent
     *   ?season=spring → A present, B absent, C absent
     */
    public function testSeasonFilterReadsVarietyMonths(): void
    {
        // Seed 3 extra crops with empty crop-level payload (months NOT in crop payload — mirrors real data).
        $this->pdo->exec("INSERT OR IGNORE INTO crops
            (id, slug, hebrew_name, scientific_name, family_name_he, category, season, dtm_min, dtm_max, payload_json, last_pushed_at)
            VALUES
            (10, 'pepper', 'פלפל',   'Capsicum annuum',  'סולניים', 'vegetables', 'annual', 60, 90, '{}', '2026-06-04'),
            (11, 'tomato', 'עגבנייה','Solanum lycopersicum','סולניים','vegetables','annual', 60, 90, '{}', '2026-06-04'),
            (12, 'basil',  'בזיליקום','Ocimum basilicum', 'שפתניים','herbs',       'annual', 60, 90, '{}', '2026-06-04')");

        // Variety for crop A (pepper): spring months [3,4,5] in agronomy.sowing_months.
        $springPayload = json_encode(['agronomy' => ['sowing_months' => [3, 4, 5]]]);
        // Variety for crop B (tomato): summer months [6,7,8].
        $summerPayload = json_encode(['agronomy' => ['sowing_months' => [6, 7, 8]]]);
        // crop C (basil): variety exists but has NO month data (empty agronomy).
        $noMonthPayload = json_encode(['agronomy' => []]);

        $this->pdo->exec("INSERT OR IGNORE INTO crop_varieties (id, crop_id, name, payload_json) VALUES
            (201, 10, 'Standard', " . $this->pdo->quote($springPayload) . "),
            (202, 11, 'Cherry',   " . $this->pdo->quote($summerPayload) . "),
            (203, 12, 'Genovese', " . $this->pdo->quote($noMonthPayload) . ")");

        // ── season=summer ──────────────────────────────────────────────────────────
        $resSummer = $this->get('/crop-book/?season=summer');
        $this->assertSame(200, $resSummer->getStatusCode());
        $htmlSummer = (string)$resSummer->getBody();
        // Crop B (tomato) must be present.
        $this->assertStringContainsString('/crop-book/tomato/', $htmlSummer,
            'season=summer: tomato (months [6,7,8]) must be in results');
        // Crop A (pepper, spring) must be absent.
        $this->assertStringNotContainsString('/crop-book/pepper/', $htmlSummer,
            'season=summer: pepper (months [3,4,5]) must NOT be in results');
        // Crop C (basil, no data) must be absent.
        $this->assertStringNotContainsString('/crop-book/basil/', $htmlSummer,
            'season=summer: basil (no month data) must NOT be in results');

        // ── season=spring ──────────────────────────────────────────────────────────
        $resSpring = $this->get('/crop-book/?season=spring');
        $this->assertSame(200, $resSpring->getStatusCode());
        $htmlSpring = (string)$resSpring->getBody();
        // Crop A (pepper) must be present.
        $this->assertStringContainsString('/crop-book/pepper/', $htmlSpring,
            'season=spring: pepper (months [3,4,5]) must be in results');
        // Crop B (tomato, summer) must be absent.
        $this->assertStringNotContainsString('/crop-book/tomato/', $htmlSpring,
            'season=spring: tomato (months [6,7,8]) must NOT be in results');
        // Crop C (basil, no data) must be absent.
        $this->assertStringNotContainsString('/crop-book/basil/', $htmlSpring,
            'season=spring: basil (no month data) must NOT be in results');
    }
}
