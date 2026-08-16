#!/usr/bin/env python3
"""UI CAMERA A/B DIFFER — the campaign's regression eye.

Compares two --snapshot output dirs (same views, two binaries/states) and
reports per-view pixel deltas. The top-left logo sparkle animates per-boot
(x 0-60, y 0-80) and is EXCLUDED by default — every honest diff of identical
UI states differs there and nowhere else (measured 2026-07-31: 1392px,
max-delta 12, always inside that box).

Usage:
  tools/ui_pixel_diff.py A_dir B_dir                 # report all common views
  tools/ui_pixel_diff.py A_dir B_dir --view main     # one view
  tools/ui_pixel_diff.py A_dir B_dir --expect-same   # exit 1 on ANY real delta
  tools/ui_pixel_diff.py A_dir B_dir --expect-diff main --expect-same-rest
      # main MUST change (a wave landed), everything else MUST NOT (no fallout)
  --save-heat DIR   # write per-view heatmaps of differing pixels

Exit: 0 = expectations met (or report-only), 1 = an expectation failed.
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageChops
    import numpy as np
except ImportError:                                    # bare python3: honest skip
    print("ui_pixel_diff: SKIP (PIL/numpy not available — use .venv/bin/python)")
    sys.exit(0)

SPARKLE = (0, 0, 60, 80)          # x0, y0, x1, y1 — the animated logo zone
THRESH = 8                        # per-pixel channel-sum delta that counts


def view_delta(a_path, b_path):
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        return {"size_mismatch": f"{a.size} vs {b.size}", "count": -1}
    d = np.array(ImageChops.difference(a, b)).sum(axis=2)
    d[SPARKLE[1]:SPARKLE[3], SPARKLE[0]:SPARKLE[2]] = 0
    mask = d > THRESH
    count = int(mask.sum())
    out = {"count": count, "max": int(d.max())}
    if count:
        ys, xs = np.nonzero(mask)
        out["bbox"] = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    return out, mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--view", action="append", default=None,
                    help="limit to these view names (no .png)")
    ap.add_argument("--expect-same", action="store_true",
                    help="fail if any compared view differs")
    ap.add_argument("--expect-diff", action="append", default=[],
                    help="these views MUST differ (a landed wave shows itself)")
    ap.add_argument("--expect-same-rest", action="store_true",
                    help="with --expect-diff: every other view must NOT differ")
    ap.add_argument("--save-heat", default=None, help="write diff heatmaps here")
    args = ap.parse_args()

    a_views = {f[:-4] for f in os.listdir(args.a) if f.endswith(".png")}
    b_views = {f[:-4] for f in os.listdir(args.b) if f.endswith(".png")}
    common = sorted(a_views & b_views)
    if args.view:
        common = [v for v in common if v in set(args.view)]
    if not common:
        print("ui_pixel_diff: RED — no common views to compare")
        return 1
    only = (a_views ^ b_views)
    if only and not args.view:
        print(f"  (views present on one side only, skipped: {sorted(only)})")

    failed = []
    for v in common:
        res = view_delta(os.path.join(args.a, v + ".png"),
                         os.path.join(args.b, v + ".png"))
        if isinstance(res, dict):                      # size mismatch
            print(f"  {v}: SIZE MISMATCH {res['size_mismatch']}")
            failed.append(v)
            continue
        r, mask = res
        differs = r["count"] > 0
        tag = f"{r['count']}px (max {r['max']}, bbox {r.get('bbox')})" if differs else "identical"
        print(f"  {v}: {tag}")
        if args.save_heat and differs:
            os.makedirs(args.save_heat, exist_ok=True)
            hm = (mask * 255).astype("uint8")
            Image.fromarray(hm).save(os.path.join(args.save_heat, v + "_heat.png"))
        if args.expect_same and differs:
            failed.append(v)
        if v in args.expect_diff and not differs:
            print(f"    RED: {v} was expected to change and did not")
            failed.append(v)
        if args.expect_same_rest and v not in args.expect_diff and differs:
            failed.append(v)
    if failed:
        print(f"ui_pixel_diff: RED — expectation failed on: {sorted(set(failed))}")
        return 1
    print("ui_pixel_diff: GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
