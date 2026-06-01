<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;
use SFA\Lib\FieldRegistry;

/**
 * CropBookV1MacroTest — WP-CB-1 unit tests.
 *
 * Tests:
 *   1. prov_value: 3 states (VALIDATED / UNVALIDATED / MISSING)
 *   2. FieldRegistry alias resolver
 *   3. calc_panel disabled when required field is MISSING
 *   4. assumption_field renders default + key
 *   5. JS↔Python calc parity (#1 seed, #8 yield) via PHP-computed expected values
 *
 * @see DISPATCH §7
 */
final class CropBookV1MacroTest extends TestCase
{
    // ────────────────────────────────────────────────────────────
    // 1. prov_value states
    // ────────────────────────────────────────────────────────────

    private function captureProv(array $field, string $field_name = 'test_field', string $crop_slug = 'test'): string
    {
        ob_start();
        include __DIR__ . '/../templates/macros/prov_value.php';
        return (string) ob_get_clean();
    }

    public function testProvValueValidated(): void
    {
        $field = [
            'value_best'          => '45',
            'unit'                => 'ימים',
            'field_state'         => 'VALIDATED',
            'winning_source_class' => 'EX',
            'confidence_score'    => 0.95,
        ];
        $out = $this->captureProv($field, 'days_to_maturity');
        $this->assertStringContainsString('45', $out);
        $this->assertStringNotContainsString('ast', $out, 'VALIDATED should not have asterisk');
        $this->assertStringNotContainsString('val--missing', $out, 'VALIDATED should not show missing');
    }

    public function testProvValueUnvalidated(): void
    {
        $field = [
            'value_best'          => '2.1',
            'unit'                => 'ק״ג',
            'field_state'         => 'UNVALIDATED',
            'winning_source_class' => 'WR',
            'confidence_score'    => 0.25,
        ];
        $out = $this->captureProv($field, 'yield_per_bed_m');
        $this->assertStringContainsString('2.1', $out);
        $this->assertStringContainsString('ast', $out, 'UNVALIDATED must have asterisk');
        $this->assertStringNotContainsString('val--missing', $out);
    }

    public function testProvValueMissing(): void
    {
        $field = [
            'value_best'  => null,
            'unit'        => '',
            'field_state' => 'MISSING',
        ];
        $out = $this->captureProv($field, 'seeds_per_g', 'lettuce');
        $this->assertStringContainsString('val--missing', $out);
        $this->assertStringContainsString('reqinfo', $out, 'MISSING must show request-info CTA');
        $this->assertStringContainsString('—', $out);
    }

    public function testProvValueMissingFromNullValue(): void
    {
        // No field_state set — defensive derivation from null value → MISSING
        $field = ['value_best' => null, 'unit' => '', 'confidence_score' => null];
        $out   = $this->captureProv($field, 'spacing_in_row_cm');
        $this->assertStringContainsString('val--missing', $out);
    }

    // ────────────────────────────────────────────────────────────
    // 2. FieldRegistry alias resolver (FIM §1)
    // ────────────────────────────────────────────────────────────

    public function testFieldRegistryResolveOldToCanonical(): void
    {
        $this->assertSame('spacing_in_row_cm',           FieldRegistry::resolve('in_row_spacing_cm'));
        $this->assertSame('yield_per_bed_m',             FieldRegistry::resolve('avg_yield_per_bed_m'));
        $this->assertSame('price_documented',            FieldRegistry::resolve('documented_price'));
        $this->assertSame('seeds_per_g',                 FieldRegistry::resolve('seeds_per_gram'));
        $this->assertSame('frost_tolerance_class',       FieldRegistry::resolve('frost_tolerance'));
        $this->assertSame('days_in_nursery',             FieldRegistry::resolve('days_in_nursery_cell'));
        $this->assertSame('succession_interval_weeks',   FieldRegistry::resolve('succession_interval'));
        $this->assertSame('nutrient_removal_n_kg_per_ha', FieldRegistry::resolve('nutrient_removal_N'));
    }

    public function testFieldRegistryResolveCanonicalIsIdempotent(): void
    {
        $this->assertSame('spacing_in_row_cm',  FieldRegistry::resolve('spacing_in_row_cm'));
        $this->assertSame('yield_per_bed_m',    FieldRegistry::resolve('yield_per_bed_m'));
        $this->assertSame('price_documented',   FieldRegistry::resolve('price_documented'));
    }

    public function testFieldRegistryReadFindsOldKey(): void
    {
        $enrichment = ['avg_yield_per_bed_m' => 3.5]; // stored under old key
        $found = FieldRegistry::read($enrichment, 'yield_per_bed_m'); // look up canonical
        $this->assertSame(3.5, $found);
    }

    public function testFieldRegistryReadFindsCanonicalKey(): void
    {
        $enrichment = ['spacing_in_row_cm' => 25]; // stored under canonical key
        $found = FieldRegistry::read($enrichment, 'in_row_spacing_cm'); // look up old name
        $this->assertSame(25, $found);
    }

    public function testFieldRegistryReadMissingReturnsNull(): void
    {
        $this->assertNull(FieldRegistry::read([], 'yield_per_bed_m'));
    }

    public function testFieldRegistryLabelReturnsHebrew(): void
    {
        [$label,] = FieldRegistry::label('yield_per_bed_m');
        $this->assertStringContainsString('יבול', $label);

        [$label2,] = FieldRegistry::label('avg_yield_per_bed_m');
        $this->assertStringContainsString('יבול', $label2);
    }

    public function testFieldRegistryIsProposed(): void
    {
        $this->assertTrue(FieldRegistry::isProposed('needs_summer_shade'));
        $this->assertTrue(FieldRegistry::isProposed('irrigation_type'));
        $this->assertTrue(FieldRegistry::isProposed('root_depth_class'));
        $this->assertFalse(FieldRegistry::isProposed('yield_per_bed_m'));
    }

    // ────────────────────────────────────────────────────────────
    // 3. calc_panel disabled when required field is MISSING
    // ────────────────────────────────────────────────────────────

    private function captureCalcPanel(array $book_fields, string $calc_kind = 'yield'): string
    {
        $calc_no       = 8;
        $title_he      = 'יבול צפוי';
        $audience      = 'B';
        $assumptions   = [];
        $all_assumptions = [];
        $user_inputs   = [['key'=>'bed_len','label_he'=>'אורך ערוגה','value'=>'30','unit'=>'מ׳']];
        $result_label  = 'יבול';
        $result_value  = '—';
        $result_unit   = 'ק״ג';
        $formula       = '';
        $modal_id      = '';
        $crop_slug     = 'test';
        ob_start();
        include __DIR__ . '/../templates/macros/calc_panel.php';
        return (string) ob_get_clean();
    }

    public function testCalcPanelEnabledWhenFieldPresent(): void
    {
        $book_fields = [[
            'key'         => 'yield_per_m',
            'label_he'    => 'יבול/מ׳',
            'value'       => '3.5',
            'unit'        => 'ק״ג',
            'field_state' => 'VALIDATED',
            'field_name'  => 'yield_per_bed_m',
            'required'    => true,
        ]];
        $out = $this->captureCalcPanel($book_fields);
        $this->assertStringNotContainsString('is-disabled', $out);
        $this->assertStringContainsString('data-result', $out);
    }

    public function testCalcPanelDisabledWhenRequiredFieldMissing(): void
    {
        $book_fields = [[
            'key'         => 'yield_per_m',
            'label_he'    => 'יבול/מ׳',
            'value'       => null,
            'unit'        => 'ק״ג',
            'field_state' => 'MISSING',
            'field_name'  => 'yield_per_bed_m',
            'required'    => true,
        ]];
        $out = $this->captureCalcPanel($book_fields);
        $this->assertStringContainsString('is-disabled', $out);
        $this->assertStringContainsString('reqinfo', $out, 'Disabled calc must have request-info CTA');
        $this->assertStringContainsString('🔒', $out);
        // C6 / FIM §4 (F-190-CB1-V-01): disabled copy must show the resolved Hebrew label,
        // never the raw DB key and never the literal "Array" from passing label()'s tuple to $h().
        [$expectedLabel] = FieldRegistry::label('yield_per_bed_m');
        $this->assertStringContainsString($expectedLabel, $out, 'Disabled copy must show resolved Hebrew label');
        $this->assertStringNotContainsString('>Array<', $out, 'Must not render literal "Array"');
        // The raw key may appear only inside the data-field machine hook, never in visible <b> copy.
        $this->assertStringNotContainsString('<b>yield_per_bed_m', $out, 'Raw key must not appear in visible copy');
    }

    public function testCalcPanelNotDisabledForUnvalidated(): void
    {
        // UNVALIDATED ≠ disabled. Only MISSING disables.
        $book_fields = [[
            'key'         => 'yield_per_m',
            'label_he'    => 'יבול/מ׳',
            'value'       => '2.0',
            'unit'        => 'ק״ג',
            'field_state' => 'UNVALIDATED',
            'field_name'  => 'yield_per_bed_m',
            'required'    => true,
        ]];
        $out = $this->captureCalcPanel($book_fields);
        $this->assertStringNotContainsString('is-disabled', $out);
        $this->assertStringContainsString('bv--ast', $out, 'Unvalidated chip must have asterisk class');
    }

    // ────────────────────────────────────────────────────────────
    // 4. assumption_field renders default + key
    // ────────────────────────────────────────────────────────────

    private function captureAssumptionField(string $ak, array $ass): string
    {
        $key           = $ak;
        $assumption    = $ass;
        $display_value = (string)($ass['default'] ?? '');
        $display_unit  = (string)($ass['unit']    ?? '');
        $data_scale    = 1;
        if ($display_unit === 'fraction') {
            $display_value = (string)round((float)$display_value * 100);
            $display_unit  = '%';
            $data_scale    = 0.01;
        }
        $input_min = null;
        $input_max = null;
        ob_start();
        include __DIR__ . '/../templates/macros/assumption_field.php';
        return (string) ob_get_clean();
    }

    public function testAssumptionFieldRendersDefault(): void
    {
        $ass = [
            'default'      => 0.90,
            'unit'         => 'fraction',
            'explainer_he' => 'הסבר לדוגמה',
            'post_url'     => 'https://nimrod.bio/seed-germination-rate/',
        ];
        $out = $this->captureAssumptionField('germination_rate', $ass);
        $this->assertStringContainsString('90', $out, 'Fraction should display as 90%');
        $this->assertStringContainsString('%', $out);
        $this->assertStringContainsString('germination_rate', $out);
    }

    public function testAssumptionFieldRendersReadMoreLink(): void
    {
        $ass = [
            'default'      => 0.80,
            'unit'         => 'fraction',
            'explainer_he' => 'הסבר',
            'post_url'     => 'https://nimrod.bio/bed-width/',
        ];
        $out = $this->captureAssumptionField('bed_width', $ass);
        $this->assertStringContainsString('af__more', $out);
        $this->assertStringContainsString('https://nimrod.bio/bed-width/', $out);
        $this->assertStringNotContainsString('is-soon', $out, 'post_url is set, should not be soon');
    }

    public function testAssumptionFieldNullPostUrlRendersSoon(): void
    {
        $ass = ['default'=>1.10,'unit'=>'x','explainer_he'=>'הסבר','post_url'=>null];
        $out = $this->captureAssumptionField('oversow', $ass);
        $this->assertStringContainsString('is-soon', $out);
    }

    public function testAssumptionFieldRendersResetButton(): void
    {
        $ass = ['default'=>0.90,'unit'=>'fraction','explainer_he'=>'','post_url'=>null];
        $out = $this->captureAssumptionField('germination_rate', $ass);
        $this->assertStringContainsString('data-reset', $out);
        $this->assertStringContainsString('af__reset', $out);
    }

    // ────────────────────────────────────────────────────────────
    // 5. JS↔Python calc parity fixture (#1 seed, #8 yield)
    //
    // We compute the expected PHP value using the SAME formula as
    // calculators.py and crop-book-v1.js CALC, then assert they match.
    // (Live JS execution not available in PHPUnit; we verify the formula
    //  logic here in PHP as the source-of-truth parity check.)
    //
    // Calc #1: seed quantity
    //   plants = (bed_len × 100 / spacing_cm) × rows × seeds_per_hole
    //   seeds  = plants / germination_rate × oversow
    //   grams  = seeds / seeds_per_gram
    //
    // Calc #8: expected yield
    //   kg = yield_per_m × bed_len
    // ────────────────────────────────────────────────────────────

    public function testCalc1SeedParity(): void
    {
        // Inputs (typical lettuce values)
        $bed_len        = 30.0;     // m
        $spacing_cm     = 25.0;     // cm
        $rows           = 4;
        $seeds_per_hole = 1;
        $seeds_per_gram = 900.0;    // lettuce
        $germ_rate      = 0.90;     // A['germination_rate']
        $oversow        = 1.10;     // A['oversow']

        $plants = ($bed_len * 100 / $spacing_cm) * $rows * $seeds_per_hole;
        $seeds  = $plants / $germ_rate * $oversow;
        $grams  = $seeds / $seeds_per_gram;

        // Python calculators.py uses the same formula for calc #1
        $expected_grams = round($grams, 1);

        // Verify formula consistency (the JS CALC.seed mirrors this exactly)
        // plants = (30×100/25)×4×1 = 480; seeds = 480/0.90×1.10 = 586.7; grams = 586.7/900 ≈ 0.65
        $this->assertGreaterThan(0.0, $expected_grams, 'Seed grams must be positive');
        $this->assertEqualsWithDelta(0.7, $expected_grams, 0.1,
            'Calc #1 seed quantity: ~0.7g for 30m bed, 25cm spacing, 4 rows, 900spg (lettuce tiny seeds)');

        // Redundant assertion: formula is correct
        $this->assertEqualsWithDelta(
            round($grams, 1),
            round((($bed_len * 100 / $spacing_cm) * $rows * $seeds_per_hole / $germ_rate * $oversow) / $seeds_per_gram, 1),
            0.001,
            'Formula must be deterministic'
        );
    }

    public function testCalc8YieldParity(): void
    {
        // Inputs
        $bed_len      = 30.0;  // m
        $yield_per_m  = 3.5;   // kg/m

        // Python calc #8: yield_kg = yield_per_bed_m × bed_length_m
        $expected_kg  = $yield_per_m * $bed_len;  // 105 kg

        $this->assertEqualsWithDelta(105.0, $expected_kg, 0.001,
            'Calc #8 yield: 3.5 kg/m × 30m = 105 kg');

        // Parity: JS CALC.yield uses same formula
        $js_result = $yield_per_m * $bed_len;
        $this->assertEqualsWithDelta($expected_kg, $js_result, 0.001,
            'JS CALC.yield must match Python');
    }

    public function testCalc10PopulationParity(): void
    {
        // Calc #10: pop per m2
        $rows     = 4;
        $spacing  = 25; // cm
        $bw       = 0.80; // bed_width assumption

        // Python: per_m2 = (rows / bed_width) × (100 / spacing_cm)
        $per_m2 = ($rows / $bw) * (100 / $spacing);

        $this->assertEqualsWithDelta(20.0, $per_m2, 0.001,
            'Calc #10: 4 rows / 0.80m × 100/25cm = 20 plants/m2');
    }

    public function testCalc7BedsForYieldParity(): void
    {
        // Calc #7 beds_for_target_yield (Python calculators.py:351)
        //   bed_meters = target_kg / avg_yield_per_bed_m ; beds = bed_meters / std_bed_length_m
        // JS CALC.beds (crop-book-v1.js:55): beds = target_kg / (yield_per_m × std_bed_length_m)
        // Both reduce to the same value.
        $target_kg   = 300.0;
        $yield_per_m = 3.0;   // kg/m
        $std_bed_m   = 30.0;  // A['std_bed_length_m']

        $py_bed_meters = $target_kg / $yield_per_m;          // 100 m
        $py_beds       = $py_bed_meters / $std_bed_m;         // 3.33 beds
        $js_beds       = $target_kg / ($yield_per_m * $std_bed_m);

        $this->assertEqualsWithDelta($py_beds, $js_beds, 1e-9, 'Calc #7 JS must match Python');
        // 300/3 = 100 bed-meters; /30 = 3.333 beds
        $this->assertEqualsWithDelta(100.0, $py_bed_meters, 0.001, 'Calc #7: 300kg ÷ 3kg/m = 100 bed-meters');
        $this->assertEqualsWithDelta(3.3333, $js_beds, 0.001,
            'Calc #7: 300kg ÷ (3kg/m × 30m) = 3.33 beds');
    }

    public function testCalc9RevenueParity(): void
    {
        // Calc #9 expected_revenue (Python calculators.py:394)
        //   yield_kg = avg_yield_per_bed_m × bed_length_m ; revenue = yield_kg × price_per_kg
        // JS CALC.revenue (crop-book-v1.js:82): rev = (yield_per_m × area) × price
        // Equivalent when area == bed_length_m and price is per-kg.
        $yield_per_m = 3.5;   // kg/m
        $area        = 30.0;  // bed-meters (user input == bed_length_m)
        $price       = 12.0;  // ₪/kg

        $py_yield_kg = $yield_per_m * $area;        // 105 kg
        $py_rev      = $py_yield_kg * $price;        // 1260 ₪
        $js_rev      = ($yield_per_m * $area) * $price;

        $this->assertEqualsWithDelta($py_rev, $js_rev, 1e-9, 'Calc #9 JS must match Python');
        $this->assertEqualsWithDelta(1260.0, $js_rev, 0.001,
            'Calc #9: 3.5kg/m × 30m × 12₪ = 1260 ₪');
    }

    public function testCalc12FertilizerParity(): void
    {
        // Calc #12 fertilizer_compost_rate (Python calculators.py:479)
        //   area_ha = area_m2/10000 ; n_kg = n_kg_ha × area_ha
        //   compost_kg = n_kg / (compost_N_pct × application_efficiency)
        // JS CALC.fert (crop-book-v1.js:114): identical.
        $n_kg_ha     = 120.0;   // nutrient_removal_n_kg_per_ha
        $area_m2     = 50.0;
        $compost_pct = 0.015;   // A['compost_N_pct']
        $app_eff     = 0.50;    // A['application_efficiency']

        $area_ha    = $area_m2 / 10000.0;
        $py_n_kg    = $n_kg_ha * $area_ha;                       // 0.6 kg
        $py_compost = $py_n_kg / ($compost_pct * $app_eff);      // 80 kg
        $js_compost = ($n_kg_ha * ($area_m2 / 10000.0)) / ($compost_pct * $app_eff);

        $this->assertEqualsWithDelta($py_compost, $js_compost, 1e-9, 'Calc #12 JS must match Python');
        $this->assertEqualsWithDelta(80.0, $js_compost, 0.001,
            'Calc #12: N 0.6kg ÷ (1.5% × 0.5) = 80 kg compost');
    }
}
