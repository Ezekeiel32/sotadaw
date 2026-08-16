#!/usr/bin/env python3
"""The ENGINE's automation-curve math, ported 1:1 so Python tools can sample
the exact shape the audio thread plays.

Source of truth (vendored engine):
  app/tracktion_engine/modules/tracktion_core/utilities/tracktion_Bezier.h
  app/tracktion_engine/modules/tracktion_engine/model/automation/
      tracktion_AutomationCurve.cpp  (getValueAt: segment p1->p2 takes p1's
      curve; c==0 linear; |c|<=0.5 one-control quadratic bezier; |c|>0.5
      flat LEDGES at the ends + bezier between the moved ends)

song.json point curve -1..1 rides through SongLoader straight into
AutomationCurve::addPoint, so THESE formulas are what a curve value means.
c=+1.0 degenerates to hold-then-step (value1 all the way to x2);
c=-1.0 to step-then-hold (value2 from x1 on).
"""
import math


def get_bezier_point(x1, y1, x2, y2, c):
    """Control point of the one-control quadratic (tracktion_Bezier.h)."""
    if y2 > y1:
        run, rise = x2 - x1, y2 - y1
        xc, yc = x1 + run / 2, y1 + rise / 2
        return xc - run / 2 * -c, yc + rise / 2 * -c
    run, rise = x2 - x1, y1 - y2
    xc, yc = x1 + run / 2, y2 + rise / 2
    return xc - run / 2 * -c, yc - rise / 2 * -c


def get_bezier_ends(x1, y1, x2, y2, c):
    """|c|>0.5: the flat-ledge endpoints (tracktion_Bezier.h getBezierEnds)."""
    minic = (abs(c) - 0.5) * 2.0
    run = minic * (x2 - x1)
    rise = minic * ((y2 - y1) if y2 > y1 else (y1 - y2))
    if c > 0:
        return x1 + run, y1, x2, (y2 - rise) if y1 < y2 else (y2 + rise)
    return x1, (y1 + rise) if y1 < y2 else (y1 - rise), x2 - run, y2


def get_bezier_y_from_x(x, x1, y1, xb, yb, x2, y2):
    if x1 == x2 or y1 == y2:
        return y1
    if x <= x1:
        return y1
    if x >= x2:
        return y2
    a = x1 - 2 * xb + x2
    b = -2 * x1 + 2 * xb
    cc = x1 - x
    if a == 0:
        t = -cc / b
    else:
        disc = math.sqrt(max(0.0, b * b - 4 * a * cc))
        t = (-b + disc) / (2 * a)
        if t < 0.0 or t > 1.0:
            t = (-b - disc) / (2 * a)
    return ((1 - t) ** 2) * y1 + 2 * t * (1 - t) * yb + (t ** 2) * y2


def curve_value(x, x1, y1, x2, y2, c):
    """Value at x on the segment (x1,y1)->(x2,y2) shaped by the STARTING
    point's curve c — the exact AutomationCurve::getValueAt composition."""
    if x <= x1:
        return y1
    if x >= x2:
        return y2
    if c == 0.0:
        return y1 + (x - x1) / (x2 - x1) * (y2 - y1)
    if -0.5 <= c <= 0.5:
        xb, yb = get_bezier_point(x1, y1, x2, y2, c)
        return get_bezier_y_from_x(x, x1, y1, xb, yb, x2, y2)
    ex1, ey1, ex2, ey2 = get_bezier_ends(x1, y1, x2, y2, c)
    if x1 <= x <= ex1:
        return y1
    if ex2 <= x <= x2:
        return y2
    xb, yb = get_bezier_point(x1, y1, x2, y2, c)
    return get_bezier_y_from_x(x, ex1, ey1, xb, yb, ex2, ey2)


def sample_lane(points, xs):
    """Sample a whole automation lane ({beat,v,curve} dicts, sorted) at xs."""
    pts = sorted(({"beat": float(p["beat"]), "v": float(p["v"]),
                   "curve": float(p.get("curve", 0.0))} for p in points),
                 key=lambda p: p["beat"])
    out = []
    for x in xs:
        if not pts:
            out.append(0.0)
            continue
        if x <= pts[0]["beat"]:
            out.append(pts[0]["v"])
            continue
        if x >= pts[-1]["beat"]:
            out.append(pts[-1]["v"])
            continue
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            if a["beat"] <= x <= b["beat"]:
                out.append(curve_value(x, a["beat"], a["v"],
                                       b["beat"], b["v"], a["curve"]))
                break
    return out


if __name__ == "__main__":
    # tiny shape probe: late-bloom c=0.8 hugs the floor then blooms
    ys = sample_lane([{"beat": 0, "v": 0, "curve": 0.8}, {"beat": 8, "v": 1}],
                     [0, 2, 4, 6, 7, 8])
    print("late-bloom c=0.8:", [round(y, 3) for y in ys])
    ys = sample_lane([{"beat": 0, "v": 0, "curve": 1.0}, {"beat": 8, "v": 1}],
                     [0, 4, 7.9, 8])
    print("hold c=1.0     :", [round(y, 3) for y in ys])
