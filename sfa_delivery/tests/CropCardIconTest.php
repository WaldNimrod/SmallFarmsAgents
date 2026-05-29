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
     * AC-U2-03 (detail): when icon_url is set, detail hero renders a watercolor <img>.
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

        $this->assertStringContainsString('class="crop-card__art', $html, 'AC-U2-03: crop-card__art img must be present in detail hero');
        $this->assertStringContainsString('<img', $html, 'AC-U2-03: detail hero must use <img>');
        $this->assertStringContainsString(htmlspecialchars($iconUrl, ENT_QUOTES, 'UTF-8'), $html, 'AC-U2-03: detail img src must match icon_url');
    }

    /**
     * AC-U2-04 (detail): when icon_url is empty, detail hero falls back to SVG sprite.
     */
    public function testDetailPageFallsBackToSvgWhenIconUrlEmpty(): void
    {
        $html = $this->renderDetailPartial([
            'slug'      => 'basil',
            'name_he'   => 'בזיליקום',
            'icon_url'  => '',
            'icon_slug' => 'leaf',
        ]);

        $this->assertStringNotContainsString('class="crop-card__art cb-crop-hero__art"', $html, 'AC-U2-04: detail watercolor img must NOT appear when icon_url empty');
        $this->assertStringContainsString('cb-crop-hero__icon', $html, 'AC-U2-04: SVG sprite span must be present as fallback');
        $this->assertStringContainsString('#icon-leaf', $html, 'AC-U2-04: SVG href must reference leaf icon');
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
