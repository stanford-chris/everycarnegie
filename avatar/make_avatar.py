#!/usr/bin/env python3
"""
make_avatar.py — the everycarnegie Bluesky avatar.

Draws a Carnegie library front: pediment, columns, the entry staircase and a
lamp post. Both of the last two are canonical rather than decorative. Wikipedia
on Carnegie libraries: "The entry staircase symbolized a person's elevation by
learning", and "Most libraries had a lamp post or lantern installed near the
entrance, meant as a symbol of enlightenment."

Three constraints drive the drawing:

  Bluesky crops avatars to a circle, so everything sits inside a disc of 90% of
  the width. The corners are dead space and nothing may rely on them.
  It has to read at 40 px in a feed, which is what most people will ever see.
  That rules out windows, mouldings, lettering and any detail finer than a
  column: at thumbnail size the whole thing has to work as one silhouette.
  PIL does not anti-alias its polygons, so everything is drawn at 4x and
  downsampled with LANCZOS, which is what actually produces clean diagonals on
  the pediment and the lamp bracket.

Usage:
    python3 make_avatar.py                 # writes avatar.png at 1024px
    python3 make_avatar.py --size 512
    python3 make_avatar.py --preview       # also writes a 40px feed-size proof
"""

import argparse
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 4                                   # supersampling factor

INK = (26, 38, 43)                       # background, a cold near-black
STONE = (232, 221, 200)                  # limestone
STONE_DARK = (198, 184, 160)             # step risers and shadowed faces
DOOR = (26, 38, 43)
LAMP = (242, 181, 68)                    # the enlightenment lamp, the one warm note


def draw(size):
    S = size * SS
    u = S / 1024.0                        # design units: laid out on a 1024 grid

    img = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(img)

    def box(x0, y0, x1, y1, fill):
        d.rectangle([x0 * u, y0 * u, x1 * u, y1 * u], fill=fill)

    CX, BASE = 512, 762                   # center line and the ground line

    # ---- steps
    for i, (w, y0, y1) in enumerate([(214, 654, 690), (250, 690, 726), (288, 726, BASE)]):
        box(CX - w, y0, CX + w, y1, STONE if i % 2 == 0 else STONE_DARK)
        box(CX - w, y1 - 6, CX + w, y1, STONE_DARK)

    box(CX - 200, 626, CX + 200, 654, STONE)          # stylobate

    # ---- the wall behind the colonnade, so the doorway has something to sit in
    box(CX - 168, 396, CX + 168, 626, STONE_DARK)

    # ---- doorway. Dark against the shadowed wall rather than against the sky,
    # which is what made it vanish in the first version.
    box(CX - 52, 470, CX + 52, 626, DOOR)
    d.ellipse([(CX - 52) * u, 418 * u, (CX + 52) * u, 522 * u], fill=DOOR)

    # ---- columns
    for cx in (CX - 152, CX - 51, CX + 51, CX + 152):
        box(cx - 23, 400, cx + 23, 626, STONE)
        box(cx - 30, 392, cx + 30, 408, STONE)        # capital
        box(cx - 29, 616, cx + 29, 630, STONE)        # base

    box(CX - 232, 344, CX + 232, 396, STONE)          # entablature

    # ---- pediment
    d.polygon([(CX - 248) * u, 344 * u, CX * u, 208 * u, (CX + 248) * u, 344 * u], fill=STONE)
    d.polygon([(CX - 162) * u, 344 * u, CX * u, 296 * u, (CX + 162) * u, 344 * u], fill=STONE_DARK)

    # ---- lamp post
    lx = CX - 336
    box(lx - 9, 556, lx + 9, BASE - 8, STONE)
    box(lx - 32, BASE - 14, lx + 32, BASE, STONE)     # foot
    box(lx - 32, 550, lx + 32, 562, STONE)            # bracket
    d.polygon([(lx - 28) * u, 550 * u, (lx + 28) * u, 550 * u,
               (lx + 17) * u, 498 * u, (lx - 17) * u, 498 * u], fill=LAMP)
    d.ellipse([(lx - 8) * u, 476 * u, (lx + 8) * u, 498 * u], fill=STONE)

    # ---- glow. Added, not alpha-composited: laying translucent orange over a
    # near-black background gives a grey-brown smudge, which is exactly what the
    # first version produced. Screen-style addition of a blurred disc is what
    # actually reads as light.
    glow = Image.new("RGB", (S, S), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([(lx - 52) * u, (524 - 52) * u, (lx + 52) * u, (524 + 52) * u],
               fill=(120, 84, 26))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=44 * u))
    img = ImageChops.add(img, glow)

    # ---- fit to the circle, measured rather than eyeballed.
    # Bluesky crops to a disc, so what matters is not the bounding box but the
    # distance from the center to the furthest drawn pixel. The composition is
    # wide and low, so hand-placing it left the steps grazing the crop while the
    # top third sat empty. Re-center on the actual content, then scale so the
    # furthest corner lands inside a safe radius.
    bg = Image.new("RGB", img.size, INK)
    bbox = ImageChops.difference(img, bg).convert("L").getbbox()
    if bbox:
        content = img.crop(bbox)
        cw, ch = content.size
        safe = S * 0.455
        half_diag = ((cw / 2) ** 2 + (ch / 2) ** 2) ** 0.5
        scale = min(1.0, safe / half_diag) if half_diag else 1.0
        if scale < 1.0:
            content = content.resize((max(1, int(cw * scale)), max(1, int(ch * scale))),
                                     Image.LANCZOS)
            cw, ch = content.size
        out = Image.new("RGB", img.size, INK)
        out.paste(content, ((S - cw) // 2, (S - ch) // 2))
        img = out

    return img.resize((size, size), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=1024)
    ap.add_argument("--preview", action="store_true", help="also write a 40px feed-size proof")
    args = ap.parse_args()

    img = draw(args.size)
    out = os.path.join(HERE, "avatar.png")
    img.save(out, optimize=True)
    print(f"wrote {out}  {img.size[0]}x{img.size[1]}  {os.path.getsize(out)/1024:.0f} KB")

    if args.preview:
        # What it actually looks like in a feed, blown back up so it is visible.
        small = draw(40)
        small.save(os.path.join(HERE, "avatar_40px.png"))
        small.resize((320, 320), Image.NEAREST).save(os.path.join(HERE, "avatar_40px_zoom.png"))
        print("wrote avatar_40px.png and avatar_40px_zoom.png")


if __name__ == "__main__":
    main()
