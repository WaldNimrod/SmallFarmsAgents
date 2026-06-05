<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;

/**
 * CropCalendarMacroTest — AC-U4-10: render test for crop_calendar.php macro.
 *
 * Verifies:
 *   - Active months get the cb-calendar__month--active class.
 *   - Inactive months do NOT get the active class.
 *   - Activity-type Hebrew labels appear.
 *   - Empty calendar renders the empty-state element.
 *   - Notes appear when supplied.
 *
 * @runTestsInSeparateProcesses
 * @preserveGlobalState disabled
 */
final class CropCalendarMacroTest extends TestCase
{
    private string $macroPath;

    protected function setUp(): void
    {
        $this->macroPath = dirname(__DIR__) . '/templates/macros/crop_calendar.php';
        $this->assertFileExists($this->macroPath, 'crop_calendar.php must exist');
    }

    /**
     * Active months get the --active modifier; inactive months do not.
     */
    public function testActiveMonthsHighlighted(): void
    {
        // months[0]=Jan, [1]=Feb, [2]=Mar active; rest inactive.
        $months = array_fill(0, 12, false);
        $months[0] = true;
        $months[1] = true;
        $months[2] = true;

        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => '',
                'months'        => $months,
                'notes'         => '',
            ],
        ]);

        // Three active month cells
        $activeCount = substr_count($html, 'cb-calendar__month--active');
        $this->assertSame(3, $activeCount, 'Exactly 3 active month cells expected');

        // Total of 12 month cells
        $totalMonths = substr_count($html, 'cb-calendar__month');
        // Each active cell has TWO occurrences of the class token in the class attribute
        // ("cb-calendar__month cb-calendar__month--active"), so total = 12 base + 3 active = 15
        $this->assertGreaterThanOrEqual(12, $totalMonths, 'At least 12 month cells total');
    }

    /**
     * Activity-type Hebrew label is rendered.
     */
    public function testActivityLabelRendered(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'transplant',
                'season'        => 'summer',
                'region'        => '',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringContainsString('שתילה', $html, 'Hebrew label for transplant must appear');
    }

    /**
     * Empty calendar renders the empty-state element.
     */
    public function testEmptyCalendarRendersEmptyState(): void
    {
        $html = $this->render([]);

        $this->assertStringContainsString('cb-calendar__empty', $html, 'Empty calendar must render the empty-state class');
    }

    /**
     * Notes text appears when supplied.
     */
    public function testNotesAppear(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'winter',
                'region'        => 'IL_north',
                'months'        => array_fill(0, 12, false),
                'notes'         => 'זריעה תחת כיסוי בלבד',
            ],
        ]);

        $this->assertStringContainsString('זריעה תחת כיסוי בלבד', $html, 'Notes text must appear');
        $this->assertStringContainsString('צפון', $html, 'Zone region code must render its Hebrew label');
        $this->assertStringNotContainsString('IL_north', $html, 'Raw region code must never leak to the page');
    }

    /**
     * The generic default region (IL_general) renders its Hebrew label and the
     * raw token never leaks (mobile defect #2 — WP-CB-MOBILE v4 FIX 2 maps it
     * to "כל הארץ" rather than suppressing it).
     */
    public function testGenericRegionMapped(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => 'IL_general',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringNotContainsString('IL_general', $html, 'Generic region token must not leak raw');
        $this->assertStringContainsString('כל הארץ', $html, 'IL_general must render its Hebrew label');
    }

    /**
     * An unknown region code is suppressed rather than leaked raw.
     */
    public function testUnknownRegionSuppressed(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => 'IL_unmapped_zone',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringNotContainsString('IL_unmapped_zone', $html, 'Unknown region code must not leak raw');
        $this->assertStringNotContainsString('cb-calendar__region', $html, 'No region chip for an unmapped code');
    }

    /**
     * Seed activity label renders as "זריעה ישירה".
     */
    public function testSeedActivityLabel(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => '',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);

        $this->assertStringContainsString('זריעה ישירה', $html, 'Hebrew label for seed activity must appear');
    }

    /**
     * The season key is translated to Hebrew (WP-CB-MOBILE FIX 2b activity/season
     * maps) and the raw `spring`/`summer`/… token never leaks.
     */
    public function testSeasonMappedNoRawLeak(): void
    {
        $cases = [
            'spring' => 'אביב',
            'summer' => 'קיץ',
            'fall'   => 'סתיו',
            'winter' => 'חורף',
            'all'    => 'כל השנה',
        ];
        foreach ($cases as $key => $label) {
            $html = $this->render([
                [
                    'activity_type' => 'seed',
                    'season'        => $key,
                    'region'        => '',
                    'months'        => array_fill(0, 12, false),
                    'notes'         => '',
                ],
            ]);
            $this->assertStringContainsString($label, $html, "Season '$key' must render its Hebrew label");
            // Raw season key must not appear anywhere in visible/markup text.
            $this->assertStringNotContainsString($key, $html, "Raw season key '$key' must never leak");
        }
    }

    /**
     * The 'both' activity type renders a merged Hebrew label, never the raw key.
     */
    public function testBothActivityMappedNoRawLeak(): void
    {
        $html = $this->render([
            [
                'activity_type' => 'both',
                'season'        => 'all',
                'region'        => '',
                'months'        => array_fill(0, 12, false),
                'notes'         => '',
            ],
        ]);
        $this->assertStringContainsString('זריעה ושתילה', $html, "'both' must render its Hebrew label");
        // The activity_type key 'both' must never surface raw to the user.
        // (allow aria/labels in Hebrew only)
        $this->assertStringNotContainsString('"both"', $html, "Raw activity key 'both' must never leak as an attribute value");
        $this->assertStringNotContainsString('>both<', $html, "Raw activity key 'both' must never leak as visible text");
    }

    /**
     * No raw token (IL_*, seed/transplant/both, season keys) ever leaks, even
     * with every field populated at once.
     */
    public function testNoRawKeyLeaksAcrossAllFields(): void
    {
        $months = array_fill(0, 12, false);
        $months[3] = true;
        $html = $this->render([
            [
                'activity_type' => 'seed',
                'season'        => 'spring',
                'region'        => 'IL_general',
                'months'        => $months,
                'notes'         => 'הערה לדוגמה',
            ],
            [
                'activity_type' => 'transplant',
                'season'        => 'summer',
                'region'        => 'IL_north',
                'months'        => $months,
                'notes'         => '',
            ],
        ]);
        foreach (['IL_general', 'IL_north', 'IL_center', 'IL_south', 'MED_general',
                  'spring', 'summer', 'fall', 'winter'] as $raw) {
            $this->assertStringNotContainsString($raw, $html, "Raw key '$raw' must never leak to the page");
        }
        // The new .pcal grid is rendered.
        $this->assertStringContainsString('pcal__cells', $html, '.pcal grid must render');
    }

    /**
     * Render crop_calendar.php with $calendar variable, return HTML string.
     *
     * @param list<array<string,mixed>> $calendar
     */
    private function render(array $calendar): string
    {
        ob_start();
        try {
            include $this->macroPath;
        } finally {
            $html = ob_get_clean();
        }
        return (string)$html;
    }
}
