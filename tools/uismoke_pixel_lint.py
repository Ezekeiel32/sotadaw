#!/usr/bin/env python3
"""THE PIXEL TRUTH GUARDIAN (frame-0 class, born 2026-07-13).

uismoke builds real components, pokes them, and shoots PNGs WITHOUT ever
starting a clock. Motion code keyed off wall-time alone therefore freezes at
frame 0 inside the rig: the SCALPEL VERDICT strip rendered PITCH BLACK
(beginTransparencyLayer(~0) on never-ticked badges) and the composing PHANTOM
GLASS wore pending-blue instead of violet (tint crossfade stuck at
prevMode=off). Both looked like output; both were wrong; and NO suite leg ran
uismoke, so the rig could rot in silence.

THE LAW those components now carry: NEVER TICKED => PAINT SETTLED
(ProposalDeck / GhostGlass / SurgicalBadge gate every ease on settled(), which
stays true until the first host tick()). This lint runs the rig for real and
asserts the two pixel truths that law protects:

  badges  ui_smoke/surgical_badges.png is LIT — >2%% of pixels above the
          luminance gate (the frame-0 bug measured exactly 0.0000%%; the healed
          strip measures 8.41%%)
  glass   ui_smoke/phantom_glass.png pane-1 edge is VIOLET, not blue — tinted
          edge R/B > 0.62 (accentB #a78bfa blends to ~0.671 over the lane;
          accent #7c9bff blends to ~0.565; thresholds calibrated on the actual
          bug/fixed frame pairs, 2026-07-13)

--selftest is hermetic: it synthesizes both bug signatures (a black strip, a
blue-blend edge) plus both healed signatures and asserts the detectors fire in
BOTH directions. No binary needed.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "app", "build", "uismoke_artefacts", "Release", "uismoke")

FAILS = []
CHECKS = [0]


def ok(cond, msg):
    CHECKS[0] += 1
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


# ---------------------------------------------------------------- detectors
def badge_lit_fraction(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    px = im.load()
    w, h = im.size
    lit = sum(1 for y in range(h) for x in range(w) if sum(px[x, y]) > 120)
    return lit / float(w * h), (w, h)


def glass_edge_rb(path):
    """Mean R / mean B over pane-1's tinted top-edge band (y 12..15, x 20..929).
    Geometry is uismoke scene 12's: pane 1 = {10,12,940,66}. A scene change
    shifts n way off ~1800 and fails loud -> recalibrate consciously."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    px = im.load()
    rs, bs = [], []
    for y in range(12, 16):
        for x in range(20, 930):
            r, g, b = px[x, y]
            if b > 60 and b > g:          # tinted (edge) pixels only
                rs.append(r)
                bs.append(b)
    n = len(rs)
    if n == 0:
        return 0.0, 0
    return (sum(rs) / float(n)) / max(1.0, sum(bs) / float(n)), n


def check_badges(path):
    frac, size = badge_lit_fraction(path)
    ok(size == (640, 40), f"badges strip is 640x40 (got {size[0]}x{size[1]} — rig scene changed, recalibrate)")
    ok(frac > 0.02, f"badges strip is LIT: {frac:.4%} of pixels > gate (frame-0 bug = 0.0000%)")


def check_glass(path):
    rb, n = glass_edge_rb(path)
    ok(n > 500, f"glass pane-1 edge band has tint: {n} tinted pixels (0 = no glass painted)")
    ok(rb > 0.62, f"composing glass edge is VIOLET: R/B {rb:.3f} > 0.62 (accentB ~0.671; frame-0 blue ~0.565)")


def check_hear_retarget(full_path, retarget_path):
    """THE RETARGET LAW (2026-07-17, 'the previous project's bar'): after
    HearStrip::clear(new_identity) the OLD tensor's heat must be GONE from the
    pixels (dormant well ~ near-dark) while the full tensor before it reads hot.
    Same luminance detector as the badges; thresholds calibrated on the real
    rig frames (full ~ >8%, retarget dormant ~ <1.5%)."""
    ff, fsz = badge_lit_fraction(full_path)
    rf, rsz = badge_lit_fraction(retarget_path)
    ok(fsz == (900, 46) and rsz == (900, 46),
       f"hear strip pngs are 900x46 (got {fsz} / {rsz} — rig scene changed, recalibrate)")
    ok(ff > 0.05, f"full tensor reads HOT: {ff:.4%} lit (the strip painted its subject)")
    ok(rf < 0.015, f"retargeted strip DROPPED the old tensor: {rf:.4%} lit < 1.5% (stale-bar bug reads ~full-hot)")
    ok(rf > 0.0001, f"retargeted strip still wears an identity chip: {rf:.4%} lit > 0 (not a black void)")


# ---------------------------------------------------------------- selftest
def selftest():
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        # badge signatures
        black = os.path.join(td, "black.png")
        Image.new("RGB", (640, 40), (5, 6, 12)).save(black)
        lit = os.path.join(td, "lit.png")
        im = Image.new("RGB", (640, 40), (5, 6, 12))
        for y in range(12, 28):
            for x in range(20, 200):
                im.putpixel((x, y), (60, 220, 140))
        im.save(lit)
        fb, _ = badge_lit_fraction(black)
        fl, _ = badge_lit_fraction(lit)
        ok(fb < 0.001, f"selftest: black strip reads dark ({fb:.4%})")
        ok(fl > 0.02, f"selftest: lit strip reads lit ({fl:.4%})")

        # glass signatures — measured blends from the real bug/fixed frames
        def edge(colour, name):
            g = Image.new("RGB", (960, 238), (10, 11, 18))
            for y in range(12, 16):
                for x in range(20, 930):
                    g.putpixel((x, y), colour)
            p = os.path.join(td, name)
            g.save(p)
            return p

        blue = edge((50, 60, 88), "blue.png")       # accent blend  ~0.568
        violet = edge((83, 80, 123), "violet.png")  # accentB blend ~0.675
        rbb, nb = glass_edge_rb(blue)
        rbv, nv = glass_edge_rb(violet)
        ok(nb > 500 and rbb < 0.62, f"selftest: blue edge caught (R/B {rbb:.3f}, n={nb})")
        ok(nv > 500 and rbv > 0.62, f"selftest: violet edge passes (R/B {rbv:.3f}, n={nv})")

        # hear-retarget signatures: a STALE bar (old tensor still hot) vs a
        # dormant well wearing only the identity chip
        stale = Image.new("RGB", (900, 46), (8, 9, 16))
        for y in range(14, 40):
            for x in range(10, 890):
                if (x // 6) % 2 == 0:
                    stale.putpixel((x, y), (138, 77, 255))
        sp = os.path.join(td, "stale.png")
        stale.save(sp)
        dorm = Image.new("RGB", (900, 46), (8, 9, 16))
        for y in range(8, 11):                        # the dim chip: real rig frame
            for x in range(8, 64):                    # measures 0.454% lit (2026-07-17)
                dorm.putpixel((x, y), (52, 46, 84))
        dp = os.path.join(td, "dorm.png")
        dorm.save(dp)
        fs, _ = badge_lit_fraction(sp)
        fd, _ = badge_lit_fraction(dp)
        ok(fs > 0.015, f"selftest: stale bar signature reads HOT ({fs:.4%} — the detector would catch it)")
        ok(0.0001 < fd < 0.015, f"selftest: dormant+chip signature reads quiet-but-present ({fd:.4%})")


# ---------------------------------------------------------------- main
def main():
    if "--selftest" in sys.argv:
        selftest()
    else:
        ok(os.path.exists(BIN), f"uismoke binary exists ({os.path.relpath(BIN, ROOT)})")
        if not FAILS:
            with tempfile.TemporaryDirectory() as td:
                r = subprocess.run([BIN], cwd=td, capture_output=True, text=True, timeout=180)
                ok(r.returncode == 0, f"uismoke rig ran (rc={r.returncode})")
                out = os.path.join(td, "ui_smoke")
                if not FAILS:
                    check_badges(os.path.join(out, "surgical_badges.png"))
                    check_glass(os.path.join(out, "phantom_glass.png"))
                    check_hear_retarget(os.path.join(out, "hear_full.png"),
                                        os.path.join(out, "hear_retarget.png"))
    n = len(FAILS)
    print(f"pixel lint: {'GREEN' if n == 0 else 'RED'} ({CHECKS[0] - n}/{CHECKS[0]} checks)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
