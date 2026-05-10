<?php
/*
 * Plugin Name: SmallFarmsAgents File Upload
 * Description: REST endpoint for uploading SFA artifacts to the canonical
 *              static path (smallfarmsagents/) outside the media library.
 *              POST /wp-json/sfagent/v1/upload  — auth: Application Password
 */

add_action('rest_api_init', function () {
    register_rest_route('sfagent/v1', '/upload', [
        'methods'             => 'POST',
        'callback'            => 'sfagent_handle_upload',
        'permission_callback' => function () {
            return current_user_can('upload_files');
        },
    ]);
});

function sfagent_handle_upload(WP_REST_Request $request) {
    $filename = sanitize_file_name($request->get_param('filename'));
    $subdir   = $request->get_param('subdir');
    $b64      = $request->get_param('content');

    if (!$filename || !$subdir || $b64 === null) {
        return new WP_Error('bad_request', 'Missing filename, subdir, or content', ['status' => 400]);
    }

    // Whitelist allowed subdirs — extend when crop-book pipeline is ready
    $allowed_subdirs = ['market', 'crop-book'];
    if (!in_array($subdir, $allowed_subdirs, true)) {
        return new WP_Error('bad_subdir', 'subdir must be one of: ' . implode(', ', $allowed_subdirs), ['status' => 400]);
    }

    // Decode and validate
    $content = base64_decode($b64, true);
    if ($content === false) {
        return new WP_Error('bad_content', 'content is not valid base64', ['status' => 400]);
    }

    $dir = ABSPATH . 'smallfarmsagents/' . $subdir . '/';

    if (!wp_mkdir_p($dir)) {
        return new WP_Error('mkdir_failed', 'Could not create directory: ' . $dir, ['status' => 500]);
    }

    $dest  = $dir . $filename;
    $bytes = file_put_contents($dest, $content);

    if ($bytes === false) {
        return new WP_Error('write_failed', 'Failed to write ' . $filename, ['status' => 500]);
    }

    // site_url() = WordPress Address URL (includes /Agents if WP is in a subdir)
    $url = site_url('smallfarmsagents/' . $subdir . '/' . $filename);

    return new WP_REST_Response([
        'ok'       => true,
        'filename' => $filename,
        'subdir'   => $subdir,
        'bytes'    => $bytes,
        'url'      => $url,
    ], 201);
}
