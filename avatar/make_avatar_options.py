#!/usr/bin/env python3
"""
make_avatar_options.py — candidate avatars for the everycarnegie bot.

Eight approaches, not eight versions of one. `A` is the avatar currently on the
account, redrawn here so it can be compared on the same sheet rather than
remembered.

The three constraints from make_avatar.py apply to every one of them, and are
what most of the candidates are really being tested against:

  Bluesky crops to a circle, so nothing may rely on the corners.
  It has to read at 40 px, which is all most people will ever see. That is the
  test that kills lettering, and it is why every candidate is rendered at 40 px
  on the comparison sheet as well as at full size.
  PIL does not anti-alias polygons, so everything is drawn at 4x and
  downsampled with LANCZOS.

Usage:
    python3 make_avatar_options.py            # writes options/*.png and options.html
    python3 make_avatar_options.py --only C
"""

import argparse
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "options")
SS = 4

INK = (26, 38, 43)                  # cold near-black, the house ground
STONE = (232, 221, 200)             # limestone
STONE_DARK = (198, 184, 160)        # risers and shadowed faces
LAMP = (242, 181, 68)               # the enlightenment lamp, the one warm note
PAPER = (233, 227, 213)             # daylight ground: warm limestone
INK_SOFT = (44, 60, 66)

COPPERPLATE = "/System/Library/Fonts/Supplemental/Copperplate.ttc"
GILL = "/System/Library/Fonts/Supplemental/GillSans.ttc"


# ---------------------------------------------------------------- scaffolding

def canvas(size, bg):
    S = size * SS
    img = Image.new("RGB", (S, S), bg)
    return img, ImageDraw.Draw(img), S, S / 1024.0


def fit_circle(img, bg, safe=0.455):
    """Re-center on the drawn content and scale it inside the crop disc.

    What matters is not the bounding box but the distance from the center to
    the furthest drawn pixel, because Bluesky crops to a disc. Eyeballing this
    left the first version's steps grazing the crop while the top third sat
    empty.
    """
    S = img.size[0]
    flat = Image.new("RGB", img.size, bg)
    bbox = ImageChops.difference(img, flat).convert("L").getbbox()
    if not bbox:
        return img
    content = img.crop(bbox)
    cw, ch = content.size
    half_diag = ((cw / 2) ** 2 + (ch / 2) ** 2) ** 0.5
    scale = min(1.0, S * safe / half_diag) if half_diag else 1.0
    if scale < 1.0:
        content = content.resize((max(1, int(cw * scale)), max(1, int(ch * scale))),
                                 Image.LANCZOS)
        cw, ch = content.size
    out = Image.new("RGB", img.size, bg)
    out.paste(content, ((S - cw) // 2, (S - ch) // 2))
    return out


def add_glow(img, u, cx, cy, radius, strength=(120, 84, 26), blur=44):
    """Screen-style addition, never alpha composite.

    Laying translucent orange over a near-black ground gives a grey-brown
    smudge, which is what the first attempt at this produced. Adding a blurred
    disc is what actually reads as light.
    """
    S = img.size[0]
    glow = Image.new("RGB", (S, S), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [(cx - radius) * u, (cy - radius) * u, (cx + radius) * u, (cy + radius) * u],
        fill=strength)
    return ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(radius=blur * u)))


def font(path, size, index=0):
    return ImageFont.truetype(path, int(size), index=index)


# ------------------------------------------------------------- shared drawing

def facade(d, u, body, shade, door_fill, base=762, lamp_post=True, lamp_lit=True):
    """The library front: pediment, colonnade, entry staircase, lamp post.

    The last two are canonical, not decorative. Wikipedia on Carnegie
    libraries: the entry staircase 'symbolized a person's elevation by
    learning', and most had 'a lamp post or lantern installed near the
    entrance, meant as a symbol of enlightenment'.

    Returns the lamp's lantern center so the caller can put a glow there.
    """
    CX = 512

    def box(x0, y0, x1, y1, fill):
        d.rectangle([x0 * u, y0 * u, x1 * u, y1 * u], fill=fill)

    for i, (w, y0, y1) in enumerate([(214, 654, 690), (250, 690, 726), (288, 726, base)]):
        box(CX - w, y0, CX + w, y1, body if i % 2 == 0 else shade)
        box(CX - w, y1 - 6, CX + w, y1, shade)

    box(CX - 200, 626, CX + 200, 654, body)                  # stylobate
    box(CX - 168, 396, CX + 168, 626, shade)                 # wall behind the columns

    # Doorway, dark against the shadowed wall rather than against the sky.
    # Against the sky is what made it vanish in the first version.
    box(CX - 52, 470, CX + 52, 626, door_fill)
    d.ellipse([(CX - 52) * u, 418 * u, (CX + 52) * u, 522 * u], fill=door_fill)

    for cx in (CX - 152, CX - 51, CX + 51, CX + 152):
        box(cx - 23, 400, cx + 23, 626, body)
        box(cx - 30, 392, cx + 30, 408, body)                # capital
        box(cx - 29, 616, cx + 29, 630, body)                # base

    box(CX - 232, 344, CX + 232, 396, body)                  # entablature
    d.polygon([(CX - 248) * u, 344 * u, CX * u, 208 * u, (CX + 248) * u, 344 * u], fill=body)
    d.polygon([(CX - 162) * u, 344 * u, CX * u, 296 * u, (CX + 162) * u, 344 * u], fill=shade)

    if not lamp_post:
        return None

    lx = CX - 336
    box(lx - 9, 556, lx + 9, base - 8, body)
    box(lx - 32, base - 14, lx + 32, base, body)             # foot
    box(lx - 32, 550, lx + 32, 562, body)                    # bracket
    head = LAMP if lamp_lit else body
    d.polygon([(lx - 28) * u, 550 * u, (lx + 28) * u, 550 * u,
               (lx + 17) * u, 498 * u, (lx - 17) * u, 498 * u], fill=head)
    d.ellipse([(lx - 8) * u, 476 * u, (lx + 8) * u, 498 * u], fill=body)
    return (lx, 524)


def arc_text(layer, text, cx, cy, radius, fnt, mid_deg, flip=False, tracking=1.0):
    """Text around a circle, one rotated glyph at a time: PIL has no text-on-path.

    Lifted from everylibrary's make_avatar.py, including its trap. Screen angles
    run 0=right, 90=bottom, 270=top; along the top, reading order means
    increasing angle, along the bottom it means decreasing. Negating the walk
    direction is enough. Reversing the string as well double-negates and prints
    the words backwards.
    """
    widths = [(fnt.getbbox(ch)[2] - fnt.getbbox(ch)[0]) + fnt.size * 0.13 for ch in text]
    total = math.degrees(sum(widths) * tracking / radius)
    direction = -1 if flip else 1
    cursor = mid_deg - direction * total / 2
    for ch, w in zip(text, widths):
        step = math.degrees(w * tracking / radius)
        ang = cursor + direction * step / 2
        cursor += direction * step
        if ch == " ":
            continue
        pad = int(fnt.size * 0.95)
        glyph = Image.new("L", (pad * 2, pad * 2), 0)
        ImageDraw.Draw(glyph).text((pad, pad), ch, font=fnt, fill=255, anchor="mm")
        glyph = glyph.rotate(-ang + (90 if flip else -90), resample=Image.BICUBIC)
        rad = math.radians(ang)
        layer.paste(255, (int(cx + radius * math.cos(rad)) - pad,
                          int(cy + radius * math.sin(rad)) - pad), glyph)


# ------------------------------------------------------------------ the eight

def opt_a(size):
    """A — night facade with the lit lamp. What is on the account now."""
    img, d, S, u = canvas(size, INK)
    lamp = facade(d, u, STONE, STONE_DARK, INK)
    img = add_glow(img, u, *lamp, radius=52)
    return fit_circle(img, INK).resize((size, size), Image.LANCZOS)


def opt_b(size):
    """B — the lamp alone, the enlightenment symbol, nothing else."""
    img, d, S, u = canvas(size, INK)
    lx, base = 512, 830

    def box(x0, y0, x1, y1, fill=STONE):
        d.rectangle([x0 * u, y0 * u, x1 * u, y1 * u], fill=fill)

    box(lx - 74, base - 34, lx + 74, base)                   # plinth
    box(lx - 52, base - 62, lx + 52, base - 30)
    box(lx - 21, 386, lx + 21, base - 56)                    # post
    box(lx - 78, 372, lx + 78, 400)                          # bracket
    d.polygon([(lx - 70) * u, 374 * u, (lx + 70) * u, 374 * u,
               (lx + 40) * u, 208 * u, (lx - 40) * u, 208 * u], fill=LAMP)
    d.polygon([(lx - 44) * u, 212 * u, (lx + 44) * u, 212 * u,
               (lx + 22) * u, 168 * u, (lx - 22) * u, 168 * u], fill=STONE)
    d.ellipse([(lx - 15) * u, 138 * u, (lx + 15) * u, 172 * u], fill=STONE)
    # Glazing bars, so the head reads as a lantern rather than a wedge of color.
    for gx in (lx - 14, lx + 14):
        d.line([gx * u, 372 * u, (lx + (gx - lx) * 0.55) * u, 210 * u],
               fill=STONE_DARK, width=int(7 * u))
    img = add_glow(img, u, lx, 292, radius=118, strength=(112, 78, 24), blur=64)
    return fit_circle(img, INK, safe=0.44).resize((size, size), Image.LANCZOS)


def opt_c(size):
    """C — the same building by day: ink on limestone, no glow.

    A colorway, not a new drawing, but inverting the ground is the single
    biggest change available at 40 px, so it earns a place on the sheet.
    """
    img, d, S, u = canvas(size, PAPER)
    facade(d, u, INK, INK_SOFT, PAPER, lamp_lit=False)
    return fit_circle(img, PAPER).resize((size, size), Image.LANCZOS)


def opt_d(size):
    """D — the carved lintel: what is actually cut in stone over the door."""
    img, d, S, u = canvas(size, STONE)
    f = font(COPPERPLATE, 176 * u, index=2)
    for i, line in enumerate(("CARNEGIE", "LIBRARY")):
        y = (446 + i * 190) * u
        # Incised, not printed: a pale ghost above the dark cut face.
        d.text((512 * u, y - 9 * u), line, font=f, fill=(246, 239, 224), anchor="mm")
        d.text((512 * u, y), line, font=f, fill=(96, 84, 62), anchor="mm")
    d.rectangle([214 * u, 316 * u, 810 * u, 330 * u], fill=(176, 162, 138))
    d.rectangle([214 * u, 742 * u, 810 * u, 756 * u], fill=(176, 162, 138))
    return fit_circle(img, STONE, safe=0.47).resize((size, size), Image.LANCZOS)


def opt_e(size):
    """E — a date stamp, built the way everylibrary's is, so the two read as a set."""
    img, d, S, u = canvas(size, PAPER)
    cx = cy = S // 2
    r_out, r_in = int(S * 0.455), int(S * 0.375)
    d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], outline=INK, width=int(15 * u))
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], outline=INK, width=int(7 * u))

    text = Image.new("L", img.size, 0)
    arc_text(text, "EVERY CARNEGIE LIBRARY", cx, cy, int(S * 0.415),
             font(GILL, 82 * u, index=1), 270, tracking=1.02)
    arc_text(text, "1883 – 1929", cx, cy, int(S * 0.415),
             font(GILL, 82 * u, index=1), 90, flip=True, tracking=1.02)
    img.paste(INK, (0, 0), text)
    for a in (0, 180):
        px = cx + int(S * 0.415 * math.cos(math.radians(a)))
        py = cy + int(S * 0.415 * math.sin(math.radians(a)))
        d.ellipse([px - 13 * u, py - 13 * u, px + 13 * u, py + 13 * u], fill=INK)

    # A small facade in the middle, drawn plainly: at this size the colonnade
    # of the full drawing turns to porridge.
    def box(x0, y0, x1, y1):
        d.rectangle([x0 * u, y0 * u, x1 * u, y1 * u], fill=INK)
    d.polygon([368 * u, 470 * u, 512 * u, 372 * u, 656 * u, 470 * u], fill=INK)
    for bx in (404, 466, 528, 590):
        box(bx, 486, bx + 38, 596)
    box(360, 596, 664, 630)
    return img.resize((size, size), Image.LANCZOS)


def opt_f(size):
    """F — the doorway lit from inside, lamp removed. The library is open."""
    img, d, S, u = canvas(size, INK)
    facade(d, u, STONE, STONE_DARK, LAMP, lamp_post=False)
    # Light falling down the steps, before the glow so the glow sits over it.
    for i, (w, y0, y1) in enumerate([(214, 654, 690), (250, 690, 726), (288, 726, 762)]):
        spread = 66 + i * 26
        d.rectangle([(512 - spread) * u, y0 * u, (512 + spread) * u, y1 * u],
                    fill=(238, 206, 142) if i % 2 == 0 else (208, 176, 116))
    img = add_glow(img, u, 512, 540, radius=96, strength=(96, 66, 20), blur=58)
    return fit_circle(img, INK).resize((size, size), Image.LANCZOS)


def opt_g(size):
    """G — the entry staircase alone, the 'elevation by learning' figure."""
    img, d, S, u = canvas(size, INK)
    for i in range(7):
        w = 148 + i * 62
        y0, y1 = 736 - i * 82, 818 - i * 82
        d.rectangle([(512 - w) * u, y0 * u, (512 + w) * u, y1 * u],
                    fill=STONE if i % 2 == 0 else STONE_DARK)
        d.rectangle([(512 - w) * u, (y1 - 12) * u, (512 + w) * u, y1 * u], fill=INK)
    d.polygon([362 * u, 268 * u, 512 * u, 176 * u, 662 * u, 268 * u], fill=STONE)
    img = add_glow(img, u, 512, 230, radius=64, strength=(88, 62, 20), blur=52)
    return fit_circle(img, INK, safe=0.45).resize((size, size), Image.LANCZOS)


def opt_h(size):
    """H — the arched doorway and its fanlight, lit. A circle inside the circle."""
    img, d, S, u = canvas(size, INK)
    cx = 512

    d.rectangle([(cx - 268) * u, 300 * u, (cx + 268) * u, 862 * u], fill=STONE_DARK)
    d.pieslice([(cx - 268) * u, 32 * u, (cx + 268) * u, 568 * u], 180, 360, fill=STONE_DARK)
    d.rectangle([(cx - 216) * u, 300 * u, (cx + 216) * u, 862 * u], fill=STONE)
    d.pieslice([(cx - 216) * u, 84 * u, (cx + 216) * u, 516 * u], 180, 360, fill=STONE)

    # The opening: fanlight above, doors below.
    d.pieslice([(cx - 158) * u, 142 * u, (cx + 158) * u, 458 * u], 180, 360, fill=LAMP)
    d.rectangle([(cx - 158) * u, 300 * u, (cx + 158) * u, 862 * u], fill=LAMP)
    for a in range(0, 5):
        ang = math.radians(180 + a * 45)
        d.line([cx * u, 300 * u,
                (cx + 170 * math.cos(ang)) * u, (300 + 170 * math.sin(ang)) * u],
               fill=STONE, width=int(16 * u))
    d.rectangle([(cx - 158) * u, 292 * u, (cx + 158) * u, 320 * u], fill=STONE)
    d.rectangle([(cx - 12) * u, 320 * u, (cx + 12) * u, 862 * u], fill=STONE)   # meeting stile
    img = add_glow(img, u, cx, 420, radius=150, strength=(78, 52, 14), blur=70)
    return fit_circle(img, INK, safe=0.47).resize((size, size), Image.LANCZOS)


# (key, title, blurb, provenance, drawn-from-life?, fn)
#
# ⚠️ The provenance column is the point of this table. Three of the motifs are
# documented features of these buildings; the rest are things that merely look
# like them, and the difference is not visible in the picture. Wikipedia's
# Carnegie library article, checked 19 August 2026, is the source for all three
# quotations, and for the fact that sinks D: "No architectural style was
# recommended for the exterior, nor was it necessary to put Andrew Carnegie's
# name on the building."
OPTIONS = [
    ("A", "Facade and lamp, night",
     "Live now. The whole building, the entry steps and the lit lamp post.",
     "Two documented features, one invented frame. The staircase 'symbolized a person's "
     "elevation by learning'; most had 'a lamp post or lantern installed near the entrance, "
     "meant as a symbol of enlightenment'. The temple front is not required by anything: "
     "no style was recommended and each town chose its own, from Beaux-Arts to Scottish "
     "Baronial. The colonnade is what we picture, not what he specified.", True, opt_a),

    ("B", "The lamp alone",
     "The enlightenment lantern on its own, no building.",
     "The one motif that is documented and nothing else. A lamp post near the entrance, "
     "meant as a symbol of enlightenment: the only piece of these buildings Carnegie's "
     "office attached a meaning to that was not about the reader climbing.", True, opt_b),

    ("C", "Facade by day",
     "The same drawing inverted: ink building on limestone, no glow.",
     "Same provenance as A, minus the lamp's meaning: unlit, it is just a post. "
     "The change is the ground, which is the largest change available at 40 px.", True, opt_c),

    ("D", "The carved lintel",
     "The words cut in stone over the door, incised rather than printed.",
     "⚠️ Invented, and wrongly. Plenty of these buildings do carry the words, but the "
     "article is explicit that it 'was not necessary to put Andrew Carnegie's name on the "
     "building'. An avatar asserting it as the defining feature states something the bot's "
     "own source contradicts.", False, opt_d),

    ("E", "Date stamp",
     "Built like everylibrary's mark, so the two accounts read as a pair.",
     "The backstory is the sibling bot's, not this one's: the rubber-stamped impression on "
     "the return slip inside the front cover of a British library book. It suits an avatar "
     "because the artifact is already a circle. It has nothing to do with Carnegie, and "
     "the borrowed date stamp is British where this corpus is 88% American.", False, opt_e),

    ("F", "The lit doorway",
     "The building dark, the door warm, light falling down the steps.",
     "Documented, and the only candidate that says something the others do not. The article "
     "describes 'a prominent doorway, nearly always accessed via a staircase from the "
     "ground level'. That staircase is also the standing criticism of these buildings: "
     "the symbol of elevation is a barrier at the door.", True, opt_f),

    ("G", "The steps",
     "The entry staircase alone, with a pediment above it.",
     "The purest version of the documented symbol, and the emptiest picture. Elevation by "
     "learning with the learning removed.", True, opt_g),

    ("H", "The fanlight",
     "The arched door and its glazed fan, filling the circular crop.",
     "⚠️ Invented. Fanlights are not mentioned in the article at all. It fills the circular "
     "crop better than anything else here, which is a design argument and not a reason to "
     "claim it is a Carnegie feature.", False, opt_h),
]


# ------------------------------------------------------------------ rendering

def circle_crop(img):
    """What Bluesky actually shows. Composited onto the sheet's own ground."""
    S = img.size[0]
    mask = Image.new("L", (S * 4, S * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S * 4 - 1, S * 4 - 1], fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask.resize((S, S), Image.LANCZOS))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="render one option by letter")
    args = ap.parse_args()

    os.makedirs(OUTDIR, exist_ok=True)
    rows = []
    for key, title, blurb, prov, real, fn in OPTIONS:
        if args.only and args.only.upper() != key:
            continue
        big = circle_crop(fn(512))
        big.save(os.path.join(OUTDIR, f"{key}.png"))
        small = circle_crop(fn(40))
        small.save(os.path.join(OUTDIR, f"{key}_40.png"))
        small.resize((160, 160), Image.NEAREST).save(os.path.join(OUTDIR, f"{key}_40x4.png"))
        rows.append((key, title, blurb, prov, real))
        print(f"{key}  {title}")

    if args.only:
        return

    css = """
:root{color-scheme:light dark;--bg:#faf9f7;--card:#fff;--ink:#1a262b;--muted:#5d6b70;--line:#e3e0da}
@media (prefers-color-scheme:dark){:root{--bg:#14191c;--card:#1c2429;--ink:#e8ddc8;--muted:#9aa8ad;--line:#2b353a}}
*{box-sizing:border-box}
body{margin:0;padding:38px 24px 90px;background:var(--bg);color:var(--ink);
     font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:24px;margin:0 0 6px}
.sub{color:var(--muted);font-size:14px;margin:0 0 30px;max-width:620px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px}
.big{width:100%;max-width:240px;display:block;margin:0 auto 14px}
.key{font-weight:700}
.blurb{font-size:14px;margin:6px 0 10px}
.prov{color:var(--muted);font-size:13px;line-height:1.5;margin:0 0 14px;
      padding-left:11px;border-left:2px solid var(--line)}
.tag{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;
     padding:2px 7px;border-radius:99px;margin-left:7px;vertical-align:2px}
.drawn{background:#2c6e49;color:#fff}
.made{background:#a33;color:#fff}
.feed{display:flex;align-items:center;gap:14px;border-top:1px solid var(--line);padding-top:13px}
.feed img{image-rendering:pixelated}
.feed .real{image-rendering:auto}
.feed span{color:var(--muted);font-size:12.5px}
"""
    html = [f'<meta charset="utf-8">'
            f"<title>Carnegie avatar options</title><style>{css}</style>",
            "<div class=wrap><h1>Every Carnegie Library — avatar options</h1>",
            "<p class=sub>Eight approaches. The strip at the foot of each card is the "
            "avatar at its real feed size of 40 px, then the same 40 px file magnified "
            "4x so it can be judged. That strip is the test that matters.<br><br>"
            "<b>Documented</b> means the motif is a described feature of these buildings in "
            "Wikipedia\u2019s Carnegie library article, checked 19 August 2026. "
            "<b>Invented</b> means it is not, however much it looks the part.</p>",
            "<div class=grid>"]
    for key, title, blurb, prov, real in rows:
        tag = ("<span class='tag drawn'>documented</span>" if real
               else "<span class='tag made'>invented</span>")
        html.append(
            f"<div class=card><img class=big src='options/{key}.png' alt=''>"
            f"<div class=key>{key} — {title}{tag}</div><div class=blurb>{blurb}</div>"
            f"<div class=prov>{prov}</div>"
            f"<div class=feed><img class=real src='options/{key}_40.png' width=40 alt=''>"
            f"<img src='options/{key}_40x4.png' width=160 alt=''>"
            f"<span>40&nbsp;px,<br>then 4x</span></div></div>")
    html.append("</div></div>")
    with open(os.path.join(HERE, "options.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(html))
    print(f"\nwrote {os.path.join(HERE, 'options.html')}")


if __name__ == "__main__":
    main()
