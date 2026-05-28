#!/usr/bin/env python3
"""compose_brand_assets.py — deterministic nimrod.bio/SFA visual series.

Composes the full asset series from the authentic Devora watercolor masters on
cream paper. No AI generation → perfect series consistency. Outputs WebP (deploy
spec) + JPG previews + a hero contact-sheet into candidates/.

Run: python3 compose_brand_assets.py
"""
import os
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, "..", "..",
        "SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF",
        "03_NIMROD_BIO_STYLE_ANCHORS", "source_masters"))
WC = os.path.join(PKG, "watercolor_illustrations")
LG = os.path.join(PKG, "logos_png")
OUT = os.path.abspath(os.path.join(HERE, "..", "UPLOAD_ASSETS", "candidates"))
os.makedirs(os.path.join(OUT, "heroes"), exist_ok=True)

CREAM = (246, 241, 227, 255)            # #f5f3ec

def load(path, flip=False):
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()                  # trim transparent margins
    if bbox: im = im.crop(bbox)
    if flip: im = ImageOps.mirror(im)
    return im

def canvas(w, h): return Image.new("RGBA", (w, h), CREAM)

def place(c, asset, h_frac, cx, cy, flip=False):
    a = load(asset, flip)
    W, H = c.size; th = int(H * h_frac); sc = th / a.height
    a = a.resize((max(1, int(a.width * sc)), th), Image.LANCZOS)
    c.alpha_composite(a, (int(W * cx - a.width / 2), int(H * cy - a.height / 2)))

def save(c, name, webp_q=80):
    rgb = c.convert("RGB")
    rgb.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=webp_q, method=6)
    rgb.save(os.path.join(OUT, name + ".preview.jpg"), quality=86)

m = lambda f: os.path.join(WC, f)
basket = os.path.join(LG, "logo_with_basket.png")   # basket + wordmark (OG only)
basket_mark = os.path.join(LG, "basket.png")          # basket alone, NO text (heroes/favicon)

# ---- 8 SFA module heroes (800x800) : each = list of layers (master, h_frac, cx, cy, flip) ----
# Maximize distinctiveness: all 7 distinct masters + 2 combos. radishes = red pop.
HEROES = {
    "crop-book":   [(m("bunch.png"),     0.80, 0.44, 0.58, False)],                 # leafy clump
    "market":      [(m("radishes.png"),  0.74, 0.42, 0.60, False)],                 # red pop
    "clients":     [(m("lettuce.png"),   0.74, 0.44, 0.57, False)],                 # lush head
    "inventory":   [(basket_mark,        0.70, 0.50, 0.54, False)],                 # woven basket (object, no text)
    "calc":        [(m("parsley_1.png"), 0.50, 0.50, 0.50, False)],                 # single flat sprig, airy
    "planner":     [(m("dill.png"),      0.62, 0.50, 0.52, True)],                  # feathery, wide
    "tend-bridge": [(m("parsley_2.png"), 0.46, 0.30, 0.46, False),                  # combo = "bridge"
                    (m("radishes.png"),  0.38, 0.70, 0.62, True)],
    "field-log":   [(m("bunch.png"),     0.55, 0.34, 0.56, True),                   # combo = mixed log
                    (m("radishes.png"),  0.34, 0.68, 0.66, False)],
}
for slug, layers in HEROES.items():
    c = canvas(800, 800)
    for asset, hf, cx, cy, fl in layers:
        place(c, asset, hf, cx, cy, fl)
    save(c, os.path.join("heroes", slug))

# ---- og-default 1200x630 : radishes lower-left, logo fully inside upper-right ----
c = canvas(1200, 630)
place(c, m("radishes.png"), 0.78, 0.20, 0.60)
lg = load(basket); th = int(630 * 0.34); lg = lg.resize((int(lg.width*th/lg.height), th), Image.LANCZOS)
c.alpha_composite(lg, (1200 - lg.width - 60, int(630*0.5 - lg.height/2)))
save(c, "og-default", 80)

# ---- hub-hero 1600x900 : basket centre-left + dill, quiet right (no text) ----
c = canvas(1600, 900)
place(c, basket_mark, 0.66, 0.28, 0.54)
place(c, m("dill.png"), 0.50, 0.60, 0.40, True)
save(c, "hub-hero", 80)

# ---- contact 1600x900 : lettuce + radishes cluster left, quiet right ----
c = canvas(1600, 900)
place(c, m("lettuce.png"), 0.66, 0.26, 0.55)
place(c, m("radishes.png"), 0.50, 0.46, 0.66)
save(c, "contact", 80)

# ---- favicon set from basket mark ----
fav = canvas(512, 512); place(fav, basket_mark, 0.80, 0.5, 0.5)
fav.convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"))
for sz in (180, 32):
    fav.resize((sz, sz), Image.LANCZOS).convert("RGB").save(os.path.join(OUT, f"favicon-{sz}.png"))

# ---- hero contact sheet (one-glance review) ----
sheet = Image.new("RGB", (4*410+10, 2*410+10), (255,255,255))
for i,slug in enumerate(HEROES):
    th = Image.open(os.path.join(OUT,"heroes",slug+".preview.jpg")).resize((400,400))
    sheet.paste(th, (10 + (i%4)*410, 10 + (i//4)*410))
sheet.save(os.path.join(OUT, "_HERO_CONTACT_SHEET.jpg"), quality=88)
print("done →", OUT)
