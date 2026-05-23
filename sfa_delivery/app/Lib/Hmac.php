<?php
declare(strict_types=1);

namespace SFA\Lib;

/**
 * HMAC-SHA256 sign/verify helpers.
 * Used by HmacAuthMiddleware to authenticate /api/v1/ingest pushes
 * from waldhomeserver publisher.
 */
final class Hmac
{
    /**
     * Compute the header value: "sha256=<hex>" for the given body.
     */
    public static function sign(string $body, string $secret): string
    {
        return 'sha256=' . hash_hmac('sha256', $body, $secret);
    }

    /**
     * Verify the X-SFA-Auth header against the body using constant-time compare.
     * Returns null on success; a short reason string on failure.
     */
    public static function verify(string $headerValue, string $body, string $secret): ?string
    {
        if ($secret === '') {
            return 'server not configured';
        }
        if (!str_starts_with($headerValue, 'sha256=')) {
            return 'missing/malformed X-SFA-Auth';
        }
        $given = substr($headerValue, 7);
        $expected = hash_hmac('sha256', $body, $secret);
        if (!hash_equals($expected, $given)) {
            return 'hmac mismatch';
        }
        return null;
    }
}
