<?php
/**
 * OrganicMarketAgent — market report shortcode + public IconPark SVG URLs.
 *
 * Install: append to active child theme `functions.php`, or merge via
 * `scripts/wp_shortcode_install.py` (FTPS).
 *
 * Usage in pages: [sfagent_market_report]
 * Usage in theme/PHP: echo esc_url( sfagent_market_icon_url( 'tomato' ) );
 *
 * SFA_BODY_ICON_REWRITE — rewrites relative `src="icons/iconpark/..."` in the
 * published body fragment to absolute URLs under wp-content/uploads/market/.
 */

// SmallFarmsAgent market report + IconPark SVG base — SFA_BODY_ICON_REWRITE
if (!function_exists('sfagent_market_icon_url')) {
    function sfagent_market_icon_url($slug) {
        $upload = wp_upload_dir();
        if (!empty($upload['error'])) {
            return '';
        }
        $slug = preg_replace('/[^a-z0-9\-]/i', '', (string) $slug);
        return trailingslashit($upload['baseurl']) . 'market/icons/iconpark/' . $slug . '.svg';
    }
}

if (!function_exists('sfagent_market_report_shortcode')) {
    function sfagent_market_report_shortcode($atts) {
        $upload_dir = wp_upload_dir();
        if (!empty($upload_dir['error'])) {
            return '<p style="color:red;">Market report unavailable.</p>';
        }
        $file = $upload_dir['basedir'] . '/market/public_report_body.html';
        if (!file_exists($file)) {
            return '<p style="color:red;">Market report not available.</p>';
        }
        $html = file_get_contents($file);
        if ($html === false) {
            return '<p style="color:red;">Market report not available.</p>';
        }
        $prefix = trailingslashit($upload_dir['baseurl']) . 'market/';
        $html = str_replace('src="icons/iconpark/', 'src="' . esc_url($prefix) . 'icons/iconpark/', $html);
        return $html;
    }
}

if (!shortcode_exists('sfagent_market_report')) {
    add_shortcode('sfagent_market_report', 'sfagent_market_report_shortcode');
}
