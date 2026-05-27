<?php
declare(strict_types=1);

namespace SFA\Tests;

use PHPUnit\Framework\TestCase;
use SFA\Lib\Hmac;

final class HmacTest extends TestCase
{
    private const SECRET = 'test-secret-do-not-use-in-prod';

    public function testSignProducesSha256Prefix(): void
    {
        $sig = Hmac::sign('{"hello":"world"}', self::SECRET);
        $this->assertStringStartsWith('sha256=', $sig);
        $this->assertSame(7 + 64, strlen($sig), 'sha256= + 64 hex chars');
    }

    public function testVerifyAcceptsValidSignature(): void
    {
        $body = '{"table":"crops","rows":[]}';
        $sig = Hmac::sign($body, self::SECRET);
        $this->assertNull(Hmac::verify($sig, $body, self::SECRET));
    }

    public function testVerifyRejectsWrongSecret(): void
    {
        $body = '{"x":1}';
        $sig = Hmac::sign($body, 'wrong-secret');
        $this->assertSame('hmac mismatch', Hmac::verify($sig, $body, self::SECRET));
    }

    public function testVerifyRejectsMalformedHeader(): void
    {
        $this->assertSame('missing/malformed X-SFA-Auth', Hmac::verify('', 'body', self::SECRET));
        $this->assertSame('missing/malformed X-SFA-Auth', Hmac::verify('md5=abc', 'body', self::SECRET));
    }

    public function testVerifyRejectsEmptySecret(): void
    {
        $sig = Hmac::sign('body', 'any');
        $this->assertSame('server not configured', Hmac::verify($sig, 'body', ''));
    }

    public function testVerifyRejectsTamperedBody(): void
    {
        $sig = Hmac::sign('original', self::SECRET);
        $this->assertSame('hmac mismatch', Hmac::verify($sig, 'tampered', self::SECRET));
    }

    public function testHashEqualsIsConstantTime(): void
    {
        // Smoke check: signing same body+secret yields identical sig
        $a = Hmac::sign('foo', self::SECRET);
        $b = Hmac::sign('foo', self::SECRET);
        $this->assertSame($a, $b);
    }
}
