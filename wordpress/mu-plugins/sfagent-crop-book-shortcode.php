<?php
/**
 * SFA Crop Book Shortcode — [sfagent_crop_book]
 *
 * Renders the ספר גידולים SPA inside a WordPress page.
 * Fetches the body fragment from the WP media library via the
 * manifest-of-URLs pointer stored in WP option
 * `sfagent_crop_book_manifest_of_urls_url`.
 *
 * Deploy: upload this file to wp-content/mu-plugins/ via uPress File Manager.
 * See runbook: UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md § Crop Book publish (S003 / WP004)
 *
 * PHP 7.4 minimum (matches uPress baseline).
 *
 * F-190-WP004-03: uses 4-arg str_replace with $count check to detect sentinel drift.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// Guard: safe to re-upload (idempotency)
if ( ! function_exists( 'sfagent_crop_book_shortcode' ) ) {

    // -------------------------------------------------------------------------
    // 1. Register WP option (show_in_rest: CLI can set via /wp/v2/settings)
    // -------------------------------------------------------------------------
    add_action( 'init', function () {
        register_setting(
            'options',
            'sfagent_crop_book_manifest_of_urls_url',
            array(
                'show_in_rest'      => true,
                'type'              => 'string',
                'sanitize_callback' => 'esc_url_raw',
                'default'           => '',
            )
        );
    } );

    // -------------------------------------------------------------------------
    // 2. Register shortcode
    // -------------------------------------------------------------------------
    add_shortcode( 'sfagent_crop_book', 'sfagent_crop_book_shortcode' );

    // -------------------------------------------------------------------------
    // 3. Enqueue styles hook (no-op for v1 — CSS is inlined in body fragment)
    //    Registered so adding deployed CSS later is a one-line change.
    // -------------------------------------------------------------------------
    add_action( 'wp_enqueue_scripts', 'sfagent_crop_book_enqueue_styles' );

    function sfagent_crop_book_enqueue_styles() {
        // v1: all styles inline in body fragment — no external stylesheet.
    }

    // -------------------------------------------------------------------------
    // Shortcode function
    // -------------------------------------------------------------------------
    function sfagent_crop_book_shortcode( $atts ) {
        $placeholder = '<div class="sfa-crop-book-pending">ספר גידולים — בטעינה</div>';

        // Step 1: read MoU URL from WP option
        $mou_url = get_option( 'sfagent_crop_book_manifest_of_urls_url', '' );
        if ( empty( $mou_url ) ) {
            error_log( '[sfagent_crop_book] manifest_of_urls_url option is empty — has first publish run?' );
            return $placeholder;
        }

        // Step 2: check transient cache (5-minute TTL)
        $cache_key = 'sfagent_cb_' . md5( $mou_url );
        $cached    = get_transient( $cache_key );
        if ( $cached !== false ) {
            return $cached;
        }

        // Step 3: fetch manifest-of-URLs
        $mou_resp = wp_remote_get( $mou_url, array( 'timeout' => 10 ) );
        if ( is_wp_error( $mou_resp ) ) {
            error_log( '[sfagent_crop_book] wp_remote_get MoU failed: ' . $mou_resp->get_error_message() . ' url=' . $mou_url );
            return $placeholder;
        }
        $mou_status = wp_remote_retrieve_response_code( $mou_resp );
        if ( $mou_status !== 200 ) {
            error_log( '[sfagent_crop_book] MoU URL returned HTTP ' . $mou_status . ' — url=' . $mou_url );
            return $placeholder;
        }

        // Step 4: decode MoU JSON
        $mou = json_decode( wp_remote_retrieve_body( $mou_resp ) );
        if ( null === $mou || empty( $mou->artifacts->body ) || empty( $mou->artifacts->data ) ) {
            error_log( '[sfagent_crop_book] MoU JSON invalid or missing artifacts.body / artifacts.data' );
            return $placeholder;
        }

        $body_url = $mou->artifacts->body;
        $data_url = $mou->artifacts->data;

        // Step 5: fetch body fragment
        $body_resp = wp_remote_get( $body_url, array( 'timeout' => 15 ) );
        if ( is_wp_error( $body_resp ) ) {
            error_log( '[sfagent_crop_book] wp_remote_get body failed: ' . $body_resp->get_error_message() . ' url=' . $body_url );
            return $placeholder;
        }
        $body_status = wp_remote_retrieve_response_code( $body_resp );
        if ( $body_status !== 200 ) {
            error_log( '[sfagent_crop_book] body URL returned HTTP ' . $body_status . ' — url=' . $body_url );
            return $placeholder;
        }

        $body_html = wp_remote_retrieve_body( $body_resp );

        // Step 6: rewrite data URL sentinel (F-190-WP004-03 — 4-arg str_replace with $count)
        $sentinel    = 'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"';
        $replacement = 'window.CROP_BOOK_DATA_URL = "' . esc_url_raw( $data_url ) . '"';

        $count     = 0;
        $body_html = str_replace( $sentinel, $replacement, $body_html, $count );

        if ( $count === 0 ) {
            error_log(
                '[sfagent_crop_book] sentinel substitution miss — body fragment may have drifted; '
                . 'expected: ' . $sentinel . ' — falling back to placeholder'
            );
            return $placeholder;
        }

        // Cache for 5 minutes
        set_transient( $cache_key, $body_html, 5 * MINUTE_IN_SECONDS );

        return $body_html;
    }

} // end if ! function_exists
