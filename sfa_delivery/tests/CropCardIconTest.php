<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;

/**
 * CropCardIconTest — AC-U2-03, AC-U2-04 per LOD400_spec §5.
 *
 * Tests per-crop watercolor icon rendering in:
 *   - templates/macros/crop_card.php  (listing card)
 *   - templates/pages/book_crop.php   (detail page hero)
 *
 * Mirrors the pattern established by ModuleCardHeroTest.php.
 *
 * Runs in separate processes: this test eval-defines a stub SFA\Lib\Template
 * to let the page templates render in isolation. Without process isolation that
 * stub would shadow the real Template class for any later test in the same
 * process (e.g. RouteSmokeTest), causing spurious 500s. @preserveGlobalState
 * disabled avoids serializing the stubbed class back into child processes.
 *
 * @runTestsInSeparateProcesses
 * @preserveGlobalState disabled
 */
final class CropCardIconTest extends TestCase
{
    private string $cardMacroPath;
    private string $detailPagePath;

    protected function setUp(): void
    {
        $this->cardMacroPath  = dirname(__DIR__) . '/templates/macros/crop_card.php';
        $this->detailPagePath = dirname(__DIR__) . '/templates/pages/book_crop.php';
        $this->assertFileExists($this->cardMacroPath,  'crop_card.php must exist');
        $this->assertFileExists($this->detailPagePath, 'book_crop.php must exist');
    }

    // ── crop_card.php tests ──────────────────────────────────────────────────

    /**
     * AC-U2-03: when icon_url is set, crop_card renders a watercolor <img>.
     */
    public function testCardRendersImgWhenIconUrlSet(): void
    {
        $iconUrl = 'https://sfa.nimrod.bio/public_assets/img/icons/basil.webp';
        $html    = $this->renderCard([
            'slug'          => 'basil',
            'name_he'       => 'בזיליקום',
            'en_name'       => 'Basil',
            'icon_url'      => $iconUrl,
            'icon_svg'      => '',
            'family_tag_he' => '',
        ]);

        $this->assertStringContainsString('class="crop-card__art"', $html, 'AC-U2-03: .crop-card__art img must be present');
        $this->assertStringContainsString('<img', $html, 'AC-U2-03: must be an <img> element');
        $this->assertStringContainsString(htmlspecialchars($iconUrl, ENT_QUOTES, 'UTF-8'), $html, 'AC-U2-03: src must match icon_url');
        $this->assertStringContainsString('loading="lazy"', $html, 'AC-U2-03: img must have loading=lazy');
        $this->assertStringContainsString('decoding="async"', $html, 'AC-U2-03: img must have decoding=async');
        $this->assertStringContainsString('בזיליקום', $html, 'AC-U2-03: alt must contain crop name');
    }

    /**
     * AC-U2-04: when icon_url is empty string, crop_card falls back to SVG sprite.
     */
    public function testCardFallsBackToSvgWhenIconUrlEmpty(): void
    {
        $iconSvg = '<svg viewBox="0 0 24 24"><use href="#icon-leaf"></use></svg>';
        $html    = $this->renderCard([
            'slug'          => 'basil',
            'name_he'       => 'בזיליקום',
            'en_name'       => 'Basil',
            'icon_url'      => '',
            'icon_svg'      => $iconSvg,
            'family_tag_he' => '',
        ]);

        $this->assertStringNotContainsString('class="crop-card__art"', $html, 'AC-U2-04: crop-card__art must NOT appear when icon_url empty');
        $this->assertStringContainsString('gj-cropcard__icon', $html, 'AC-U2-04: SVG sprite wrapper must be present as fallback');
    }

    /**
     * AC-U2-04: when BOTH icon_url AND icon_svg are absent, falls back to #icon-leaf.
     */
    public function testCardFallsBackToLeafWhenBothAbsent(): void
    {
        $html = $this->renderCard([
            'slug'          => 'basil',
            'name_he'       => 'בזיליקום',
            'en_name'       => 'Basil',
            'icon_url'      => '',
            'icon_svg'      => '',
            'family_tag_he' => '',
        ]);

        $this->assertStringNotContainsString('class="crop-card__art"', $html, 'AC-U2-04: crop-card__art must NOT appear');
        $this->assertStringContainsString('#icon-leaf', $html, 'AC-U2-04: generic leaf icon must be present as ultimate fallback');
    }

    // ── book_crop.php (detail page) tests ───────────────────────────────────

    /**
     * AC-U2-03 (detail): detail hero renders the single .crophero section with crop name.
     *
     * WI-4 update: The legacy .cb-crop-hero section (with .cb-crop-hero__art / .cb-crop-hero__icon)
     * was removed in WP-CB-UI-FIDELITY. The new single hero is .crophero (class="crophero").
     * Art is controlled by $wc_art (watercolor PNG) or emoji fallback (.veg span) — NOT icon_url.
     * icon_url was only used in the removed legacy hero.
     */
    public function testDetailPageRendersImgWhenIconUrlSet(): void
    {
        $iconUrl = 'https://sfa.nimrod.bio/public_assets/img/icons/basil.webp';
        $html    = $this->renderDetailPartial([
            'slug'      => 'basil',
            'name_he'   => 'בזיליקום',
            'icon_url'  => $iconUrl,
            'icon_slug' => 'leaf',
        ]);

        // WI-4: single crophero section present with h1 crop name
        $this->assertStringContainsString('class="crophero"', $html, 'AC-U2-03: single .crophero section must be present in detail hero');
        $this->assertStringContainsString('<h1>', $html, 'AC-U2-03: detail hero must have h1 crop name');
        $this->assertStringContainsString('בזיליקום', $html, 'AC-U2-03: detail hero must render the Hebrew crop name');
    }

    /**
     * AC-U2-04 (detail): when icon_url is empty, the single hero still renders.
     *
     * WI-4 update: The old .cb-crop-hero__icon fallback (SVG sprite) was removed.
     * Art fallback is now an emoji <span class="veg"> (via $art_html_v1 in crophero__art).
     * The legacy .cb-crop-hero section is gone — only .crophero remains.
     */
    public function testDetailPageFallsBackToSvgWhenIconUrlEmpty(): void
    {
        $html = $this->renderDetailPartial([
            'slug'      => 'basil',
            'name_he'   => 'בזיליקום',
            'icon_url'  => '',
            'icon_slug' => 'leaf',
        ]);

        // WI-4: single hero present; legacy icon box removed (no .cb-crop-hero__icon)
        $this->assertStringContainsString('class="crophero"', $html, 'AC-U2-04: .crophero single hero must be present');
        $this->assertStringNotContainsString('cb-crop-hero__icon', $html, 'AC-U2-04: legacy green icon box must NOT be present (WI-4 dedup)');
        // Art fallback: emoji span OR watercolor img in crophero__art
        $this->assertStringContainsString('crophero__art', $html, 'AC-U2-04: crophero__art art container must be present');
    }

    // ── C1: plural-slug art regression (patch01 recovery) ───────────────────

    /**
     * C1-regression: plural DB slugs must resolve to their watercolor PNG, not fall back
     * to the generic glyph. Guards against the patch01 singular-only map regression.
     *
     * We test by asserting the WC_ART constant directly via ReflectionClass so this
     * does NOT require a running DB or rendered template.
     *
     * @dataProvider pluralSlugArtProvider
     */
    public function testPluralSlugResolvesToWcArt(string $slug, string $expectedFile): void
    {
        $rc  = new \ReflectionClass(\SFA\Controllers\CropBookViewController::class);
        $map = $rc->getConstant('WC_ART');
        $this->assertIsArray($map, 'WC_ART constant must be an array');
        $this->assertArrayHasKey($slug, $map, "C1: plural slug '{$slug}' must be present in WC_ART");
        $this->assertSame($expectedFile, $map[$slug], "C1: '{$slug}' must map to '{$expectedFile}'");
    }

    /** @return array<string, array{string, string}> */
    public static function pluralSlugArtProvider(): array
    {
        return [
            'carrots'              => ['carrots',                      'wc-carrot.png'],
            'tomatoes'             => ['tomatoes',                     'wc-tomato.png'],
            'cucumbers'            => ['cucumbers',                    'wc-cucumber.png'],
            'onions'               => ['onions',                       'wc-onion.png'],
            'peppers'              => ['peppers',                      'wc-pepper.png'],
            'peas'                 => ['peas',                         'wc-pea.png'],
            'beets'                => ['beets',                        'wc-beet.png'],
            'radishes'             => ['radishes',                     'wc-radish.png'],
            'melons'               => ['melons',                       'wc-melon.png'],
            'leeks'                => ['leeks',                        'wc-leek.png'],
            'cherry-tomato'        => ['cherry-tomato',                'wc-tomato.png'],
            'summer-squash'        => ['summer-squash',                'wc-zucchini.png'],
            'onions-scallions'     => ['onions-scallions',             'wc-scallion.png'],
            'beans-default-pole-climbing-' => ['beans-default-pole-climbing-', 'wc-pole-bean.png'],
        ];
    }

    // ── Render helpers ───────────────────────────────────────────────────────

    /**
     * Render crop_card.php with the given $crop array and return buffered HTML.
     *
     * @param array<string,mixed> $crop
     */
    private function renderCard(array $crop): string
    {
        ob_start();
        try {
            include $this->cardMacroPath;
        } finally {
            $html = ob_get_clean();
        }
        return (string)$html;
    }

    /**
     * Render ONLY the cb-crop-hero section from book_crop.php by capturing
     * just the icon/hero area. We extract it from the buffered output since
     * the full page template requires a DB-backed Template::render().
     *
     * Technique: override SFA\Lib\Template::render to return $content only,
     * using a temporary stub approach via output buffering.
     *
     * @param array<string,mixed> $cropOverrides
     */
    private function renderDetailPartial(array $cropOverrides): string
    {
        $defaults = [
            'slug'          => 'test-crop',
            'name_he'       => 'בדיקה',
            'name_lat'      => 'Testus cropus',
            'en_name'       => 'Test Crop',
            'icon_slug'     => 'leaf',
            'icon_url'      => '',
            'description_he' => '',
            'family'        => null,
            'varieties'     => [],
            'knowledge_notes' => [],
            'timeline'      => null,
            'market_link'   => null,
        ];
        $crop = array_merge($defaults, $cropOverrides);

        // book_crop.php calls Template::render at the end. We need to stub it.
        // Check if stub already loaded; if not, load it inline.
        if (!class_exists('SFA\\Lib\\Template', false)) {
            // Define a minimal stub so book_crop.php can complete.
            // phpcs:ignore
            eval('namespace SFA\\Lib; class Template { '
                . 'public static function h(string $s): string { return htmlspecialchars($s, ENT_QUOTES, "UTF-8"); } '
                . 'public static function render(string $tpl, array $vars = []): string { return $vars["content"] ?? ""; } '
                . '}');
        }

        ob_start();
        try {
            include $this->detailPagePath;
        } finally {
            $html = ob_get_clean();
        }
        return (string)$html;
    }
}
