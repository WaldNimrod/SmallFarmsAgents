<?php
declare(strict_types=1);

namespace SFA\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

/**
 * AssumptionsController — WP-CB-1 API endpoints.
 *
 * GET  /api/v1/assumptions  — serves the ASSUMPTIONS registry as JSON.
 *   PHP array mirrors assumptions.py ASSUMPTIONS (canonical SSoT; this is a
 *   static read-only mirror, refreshed manually when assumptions.py changes).
 *
 * POST /api/v1/contribute   — lightweight community-funnel capture.
 *   kind="request-info" {field_name, crop_slug} → append to log file.
 *   Returns 200 always (marketing/community funnel, no triage UI).
 *
 * @see FIELD_INTERFACE_MAP_v1.0.0.md §3
 * @see TEMPLATES-delta.md §1 (route map)
 */
final class AssumptionsController
{
    /**
     * ASSUMPTIONS registry — mirrors assumptions.py ASSUMPTIONS (WP-CB-1 SSoT).
     * Scalars + table keys (tray_cells, hardiness_offset).
     * Updated manually when the Python SSOT changes (LOCKED backend).
     *
     * @var array<string, array{default:mixed,unit:string,explainer_he:string,post_url:string|null}>
     */
    private const ASSUMPTIONS = [
        'germination_rate' => [
            'default'      => 0.90,
            'unit'         => 'fraction',
            'explainer_he' => 'כמה מהזרעים שאתה זורע צפויים לנבוט? ברירת המחדל 90% מתאימה לזרעים רעננים. זרעים ישנים עשויים לנבוט פחות.',
            'post_url'     => 'https://nimrod.bio/blog/seed-germination-rate/',
        ],
        'bed_width' => [
            'default'      => 0.80,
            'unit'         => 'm',
            'explainer_he' => 'רוחב הערוגה בה אתה עובד. ברירת המחדל שלנו 80 ס״מ — תקן JM Fortier.',
            'post_url'     => 'https://nimrod.bio/blog/garden-bed-width-80cm/',
        ],
        'oversow' => [
            'default'      => 1.10,
            'unit'         => 'x',
            'explainer_he' => 'כמות הזרעים לזרות מעבר לצורך כמרווח ביטחון. 1.10 = 10% יותר.',
            'post_url'     => null,
        ],
        'std_bed_length_m' => [
            'default'      => 30.0,
            'unit'         => 'm',
            'explainer_he' => 'אורך ערוגה סטנדרטי לחישובים. ברירת מחדל 30 מטר.',
            'post_url'     => null,
        ],
        'compost_N_pct' => [
            'default'      => 0.015,
            'unit'         => 'fraction',
            'explainer_he' => 'אחוז חנקן (N) בקומפוסט. ברירת מחדל 1.5%. בדוק ניתוח קומפוסט לערך מדויק.',
            'post_url'     => null,
        ],
        'application_efficiency' => [
            'default'      => 0.50,
            'unit'         => 'fraction',
            'explainer_he' => 'שיעור הנטרול הביולוגי של חנקן הקומפוסט בעונה הראשונה. ברירת מחדל 50%.',
            'post_url'     => null,
        ],
        'rotation_gap_seasons' => [
            'default'      => 3,
            'unit'         => 'seasons',
            'explainer_he' => 'כמה עונות לחכות לפני שחוזרים לאותה משפחה בוטנית באותה ערוגה.',
            'post_url'     => null,
        ],
        'tray_cells' => [
            'default'      => 128,
            'unit'         => 'cells',
            'explainer_he' => 'מספר תאים במגש משתלה סטנדרטי. ברירת מחדל 128.',
            'post_url'     => null,
        ],
        'hardiness_offset' => [
            // Table: frost_tolerance_class → days_offset before last/first frost
            'default' => [
                'hardy'       => 42,
                'half_hardy'  => 14,
                'tender'      => 0,
                'very_tender' => -7,
            ],
            'unit'         => 'days',
            'explainer_he' => 'כמה ימים לפני (או אחרי) גבול הכפור ניתן לשתול, לפי עמידות לקרה.',
            'post_url'     => null,
        ],
    ];

    /**
     * GET /api/v1/assumptions
     * Returns the assumptions registry as JSON. CORS-open.
     */
    /**
     * GET /assumptions — WP-CB-UI-REDESIGN (WI-6): the standalone "הנחות היסוד שלי"
     * editor. Renders the ASSUMPTIONS registry as grouped, searchable rows with
     * community defaults + per-field "used-in" chips. Local overrides persist
     * client-side (localStorage 'sfa.assumptions'); the page never mutates the
     * locked calc engine. Display value/unit are derived from the canonical
     * default + a small presentation map.
     */
    public function page(Request $request, Response $response): Response
    {
        // Presentation map: key → [group, label_he, unit_he, used_in[], display×factor].
        // 'f' = factor applied to the canonical default for human display (e.g. fraction→%).
        $pres = [
            'germination_rate'       => ['g' => 'זרעים ונביטה', 'l' => 'אחוז נביטה',          'u' => '%',     'f' => 100, 'used' => ['זרעים', 'עלות זרעים']],
            'oversow'                => ['g' => 'זרעים ונביטה', 'l' => 'מקדם ביטחון לזרעים',   'u' => '×',     'f' => 1,   'used' => ['זרעים', 'שתילים']],
            'tray_cells'             => ['g' => 'זרעים ונביטה', 'l' => 'תאים במגש משתלה',      'u' => 'תאים', 'f' => 1,   'used' => ['שתילים']],
            'bed_width'              => ['g' => 'ערוגה ושטח',   'l' => 'רוחב ערוגה',           'u' => 'ס״מ',  'f' => 100, 'used' => ['זרעים', 'שתילים', 'צפיפות', 'יבול']],
            'std_bed_length_m'       => ['g' => 'ערוגה ושטח',   'l' => 'אורך ערוגה סטנדרטי',   'u' => 'מ׳',   'f' => 1,   'used' => ['יבול', 'הכנסה']],
            'compost_N_pct'          => ['g' => 'דישון',        'l' => 'אחוז חנקן בקומפוסט',   'u' => '%',     'f' => 100, 'used' => ['דישון']],
            'application_efficiency' => ['g' => 'דישון',        'l' => 'יעילות שחרור חנקן',    'u' => '%',     'f' => 100, 'used' => ['דישון']],
            'rotation_gap_seasons'   => ['g' => 'סבב ואקלים',   'l' => 'מרווח סבב גידולים',    'u' => 'עונות','f' => 1,   'used' => ['סבב גידולים']],
        ];
        $groupIcon = [
            'ערוגה ושטח'   => 'i-grid',
            'זרעים ונביטה' => 'i-sprout',
            'דישון'        => 'i-compost',
            'סבב ואקלים'   => 'i-repeat',
        ];

        $groups = [];
        foreach ($pres as $key => $p) {
            $def = self::ASSUMPTIONS[$key]['default'] ?? null;
            if (!is_numeric($def)) { continue; }
            $disp = (float)$def * (float)$p['f'];
            $dispStr = rtrim(rtrim(number_format($disp, 2, '.', ''), '0'), '.');
            $groups[$p['g']]['icon'] = $groupIcon[$p['g']] ?? 'i-gear';
            $groups[$p['g']]['rows'][] = [
                'key'       => $key,
                'label'     => $p['l'],
                'explainer' => (string)(self::ASSUMPTIONS[$key]['explainer_he'] ?? ''),
                'unit'      => $p['u'],
                'used'      => $p['used'],
                'value'     => $dispStr,
                'post_url'  => self::ASSUMPTIONS[$key]['post_url'] ?? null,
            ];
        }

        $html = \SFA\Lib\Template::render('pages/assumptions', ['groups' => $groups]);
        $response->getBody()->write($html);
        return $response->withStatus(200)->withHeader('Content-Type', 'text/html; charset=utf-8');
    }

    public function list(Request $request, Response $response): Response
    {
        $payload = json_encode(self::ASSUMPTIONS, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        $response->getBody()->write((string)$payload);
        return $response
            ->withStatus(200)
            ->withHeader('Content-Type', 'application/json; charset=utf-8')
            ->withHeader('Access-Control-Allow-Origin', '*')
            ->withHeader('Cache-Control', 'public, max-age=3600');
    }

    /**
     * POST /api/v1/contribute
     * Accepts kind="request-info" {field_name, crop_slug}.
     * Appends to a JSONL log file; returns 200.
     */
    public function contribute(Request $request, Response $response): Response
    {
        $body = (string)$request->getBody();
        $data = json_decode($body, true);
        if (!is_array($data)) {
            $data = (array)($request->getParsedBody() ?? []);
        }

        $kind       = (string)($data['kind']       ?? '');
        $field_name = (string)($data['field_name'] ?? '');
        $crop_slug  = (string)($data['crop_slug']  ?? '');

        // Validate kind
        if ($kind !== 'request-info') {
            $response->getBody()->write(json_encode(['error' => 'unsupported kind'], JSON_UNESCAPED_UNICODE));
            return $response->withStatus(400)->withHeader('Content-Type', 'application/json; charset=utf-8');
        }

        // Sanitize
        $field_name = preg_replace('/[^a-z0-9_]/', '', strtolower($field_name)) ?? '';
        $crop_slug  = preg_replace('/[^a-z0-9-]/', '', strtolower($crop_slug))  ?? '';

        // Append to JSONL log (lightweight funnel, no triage UI)
        $entry = json_encode([
            'ts'         => date('c'),
            'kind'       => $kind,
            'field_name' => $field_name,
            'crop_slug'  => $crop_slug,
            'ip_hash'    => substr(md5((string)($_SERVER['REMOTE_ADDR'] ?? '')), 0, 8),
        ], JSON_UNESCAPED_UNICODE) . "\n";

        $logDir  = __DIR__ . '/../../logs';
        $logFile = $logDir . '/contribute.jsonl';
        if (is_dir($logDir) && is_writable($logDir)) {
            file_put_contents($logFile, $entry, FILE_APPEND | LOCK_EX);
        }

        $response->getBody()->write(json_encode(['ok' => true], JSON_UNESCAPED_UNICODE));
        return $response->withStatus(200)->withHeader('Content-Type', 'application/json; charset=utf-8');
    }

    /**
     * Static helper: return the assumptions array for use in PHP templates.
     *
     * @return array<string, array{default:mixed,unit:string,explainer_he:string,post_url:string|null}>
     */
    public static function getAssumptions(): array
    {
        return self::ASSUMPTIONS;
    }
}
