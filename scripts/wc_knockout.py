#!/usr/bin/env python3
"""wc_knockout.py — knock an opaque cream/paper background out to transparent alpha.

Watercolor crop derivatives that come back on a filled cream ground (#f5f3ec-ish) show a
visible square on the card under `mix-blend-mode: multiply`. This converts the cream ground
to alpha (distance-from-corner-color ramp) so the subject floats like the original Devora
masters (radish/lettuce), preserving soft feathered edges. Idempotent: already-transparent
images are left unchanged.

Usage: python3 scripts/wc_knockout.py <file.png> [<file.png> ...]
"""
import sys
from PIL import Image
import numpy as np


def knockout(path, lo=14, hi=55):
    im = Image.open(path).convert('RGBA')
    a = np.array(im).astype(float)
    # Skip if the corner is already transparent (nothing to remove).
    if a[:6, :6, 3].mean() <= 250:
        return False
    rgb = a[..., :3]
    corners = np.concatenate([
        rgb[:6, :6].reshape(-1, 3), rgb[:6, -6:].reshape(-1, 3),
        rgb[-6:, :6].reshape(-1, 3), rgb[-6:, -6:].reshape(-1, 3),
    ])
    bg = np.median(corners, axis=0)
    # Only treat a LIGHT corner as background (avoid eating dark-on-light art).
    if bg.mean() <= 225:
        return False
    dist = np.sqrt(((rgb - bg) ** 2).sum(-1))
    alpha = np.clip((dist - lo) / (hi - lo), 0, 1) * 255
    a[..., 3] = np.minimum(a[..., 3], alpha)
    Image.fromarray(a.astype('uint8')).save(path)
    return True


if __name__ == '__main__':
    done = 0
    for p in sys.argv[1:]:
        try:
            if knockout(p):
                done += 1
        except Exception as e:  # noqa: BLE001 — best-effort; never break the build pipeline
            print(f"  wc_knockout skip {p}: {e}", file=sys.stderr)
    print(f"  wc_knockout: {done}/{len(sys.argv) - 1} backgrounds removed")
