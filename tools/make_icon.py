#!/usr/bin/env python3
"""THE ICON IS THE FIRST PIXEL (relight v8) — generate app/icon.png.

The dock/launcher face every public install shows (make_deb.sh hicolor 256,
make_appimage.sh). Mirrors the app's brand exactly: the four-point spark
(UiTheme.h theme::spark — quad beziers, k = 0.32R) in the agent violet, on a
deep-space glass tile under the nebula's blue/violet blooms with the signature
crown hairline. Deterministic: same inputs -> same bytes (no time, no random).

    .venv/bin/python tools/make_icon.py          # writes app/icon.png (256)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# UiTheme.h truth
BG = (7, 8, 13)         # theme::bg
BG_HI = (12, 14, 21)    # theme::bgHi
ACCENT = (124, 155, 255)   # theme::accent 0xff7c9bff
ACCENT_B = (167, 139, 250)  # theme::accentB 0xffa78bfa
AGENT = (199, 146, 234)     # theme::agent 0xffc792ea
GOOD = (61, 220, 151)       # theme::good


def quad(p0, p1, p2, n=48):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
            for t in (i / n for i in range(n + 1))]


def spark_points(cx, cy, R):
    k = R * 0.32
    pts = []
    pts += quad((cx, cy - R), (cx + k * 0.4, cy - k * 0.4), (cx + R, cy))
    pts += quad((cx + R, cy), (cx + k * 0.4, cy + k * 0.4), (cx, cy + R))
    pts += quad((cx, cy + R), (cx - k * 0.4, cy + k * 0.4), (cx - R, cy))
    pts += quad((cx - R, cy), (cx - k * 0.4, cy - k * 0.4), (cx, cy - R))
    return pts


def bloom(size, centre, radius, colour, alpha):
    """A soft radial light: white disc -> blur -> tint."""
    g = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(g)
    d.ellipse([centre[0] - radius, centre[1] - radius,
               centre[0] + radius, centre[1] + radius], fill=alpha)
    g = g.filter(ImageFilter.GaussianBlur(radius * 0.75))
    layer = Image.new("RGBA", (size, size), colour + (0,))
    layer.putalpha(g)
    return layer


def main():
    S = 1024
    R_CORNER = 232

    # the glass tile: vertical bgHi -> bg gradient inside a rounded rect
    col = Image.new("RGB", (1, S))
    for y in range(S):
        t = y / (S - 1)
        col.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(BG_HI, BG)))
    grad = col.resize((S, S))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([10, 10, S - 10, S - 10],
                                           radius=R_CORNER, fill=255)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    img.paste(grad, (0, 0), mask)

    # the nebula: blue lower-left, violet upper-right, teal whisper lower-right
    stage = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    stage.alpha_composite(bloom(S, (250, 850), 430, ACCENT, 66))
    stage.alpha_composite(bloom(S, (800, 190), 400, ACCENT_B, 74))
    stage.alpha_composite(bloom(S, (860, 900), 300, GOOD, 26))
    stage.putalpha(Image.composite(stage.split()[3], Image.new("L", (S, S), 0), mask))
    img.alpha_composite(stage)

    # the crown hairline (the signature): a lit top edge inside the tile
    crown = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dc = ImageDraw.Draw(crown)
    dc.line([(R_CORNER * 0.75, 26), (S - R_CORNER * 0.75, 26)],
            fill=ACCENT_B + (110,), width=6)
    crown = crown.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(crown)

    # the spark: outer glow -> body -> hot core (optically centred, a hair high)
    cx, cy, R = S / 2, S / 2 - 14, 315
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon(spark_points(cx, cy, R * 1.06), fill=AGENT + (150,))
    glow = glow.filter(ImageFilter.GaussianBlur(56))
    img.alpha_composite(glow)

    body_col = tuple(int(a + (255 - a) * 0.42) for a in AGENT)     # lit violet
    body = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(body).polygon(spark_points(cx, cy, R), fill=body_col + (255,))
    body = body.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(body)

    core = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(core).polygon(spark_points(cx, cy, R * 0.55), fill=(246, 240, 255, 255))
    core = core.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(core)

    out = img.resize((256, 256), Image.LANCZOS)
    dst = os.path.join(ROOT, "app", "icon.png")
    out.save(dst, optimize=True)
    print(f"icon -> {dst} ({os.path.getsize(dst)} bytes)")


if __name__ == "__main__":
    sys.exit(main())
