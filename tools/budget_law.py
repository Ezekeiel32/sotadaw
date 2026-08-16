#!/usr/bin/env python3
"""THE BRAIN BR-D — THE BUDGET LAW (docs/SPEC_THE_BRAIN.md PART III.3).

The hour dies by construction: every take carries HARD caps — renders,
wall seconds, orders — enforced at the seam, telemetered per stage. A breach
stops the stage HONESTLY (a gap report, AMAZING's worst case), never a
silent grind. Baseline indictment: 53-58 turns / 545-1041 s per brief.

Kernel is PURE (injectable clock); the sidecar keeps one Budget per run id
and asks allow("render") before paying for another one. Telemetry rows land
in telemetry/budget.jsonl at close() — the ledger the escalation ladder
learns from.
"""
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)

DEFAULT_CAPS = {
    "renders": int(os.environ.get("SOTADAW_RENDER_CAP", "24")),
    "seconds": float(os.environ.get("SOTADAW_WALL_CAP", "1800")),
    "orders": int(os.environ.get("SOTADAW_ORDER_CAP", "400")),
}


class Budget:
    """One take's ledger. spend() counts; allow() gates; report() narrates."""

    def __init__(self, run_id, caps=None, clock=None, label=""):
        self.run_id = str(run_id)
        self.label = str(label or "")
        self.caps = dict(DEFAULT_CAPS)
        if caps:
            for k, v in caps.items():
                if v is not None:
                    self.caps[k] = v
        self._clock = clock or time.time
        self.t0 = self._clock()
        self.spent = {"renders": 0, "orders": 0}
        self.breaches = []

    def seconds(self):
        return self._clock() - self.t0

    def spend(self, kind, n=1):
        if kind in self.spent:
            self.spent[kind] += n
        return self.remaining(kind)

    def remaining(self, kind):
        if kind == "seconds":
            return max(0.0, self.caps["seconds"] - self.seconds())
        return max(0, self.caps.get(kind, 0) - self.spent.get(kind, 0))

    def allow(self, kind, n=1):
        """True if spending n of kind stays inside the cap; a refusal is
        recorded ONCE per kind (the breach ledger, not a storm)."""
        if self.seconds() > self.caps["seconds"]:
            self._breach("seconds")
            return False
        if kind == "seconds":
            return True
        ok = self.spent.get(kind, 0) + n <= self.caps.get(kind, n)
        if not ok:
            self._breach(kind)
        return ok

    def _breach(self, kind):
        if kind not in self.breaches:
            self.breaches.append(kind)

    def report(self):
        return {"run_id": self.run_id, "label": self.label,
                "seconds": round(self.seconds(), 1),
                "renders": self.spent["renders"], "orders": self.spent["orders"],
                "caps": dict(self.caps), "breaches": list(self.breaches)}

    def gap_line(self):
        """The honest stop line for a breached take."""
        if not self.breaches:
            return ""
        parts = []
        for k in self.breaches:
            if k == "seconds":
                parts.append(f"wall {self.seconds():.0f}s > cap {self.caps['seconds']:.0f}s")
            else:
                parts.append(f"{k} {self.spent.get(k, 0)} at cap {self.caps.get(k)}")
        return ("[budget] THE BUDGET LAW stopped this stage: " + ", ".join(parts)
                + " — shipping the best take so far with this gap report "
                  "(never a silent grind)")


_LIVE = {}


def for_run(run_id, caps=None, label=""):
    """The sidecar seam: one Budget per run id, created on first ask."""
    b = _LIVE.get(run_id)
    if b is None:
        b = Budget(run_id, caps=caps, label=label)
        _LIVE[run_id] = b
        if len(_LIVE) > 64:                       # bounded — runs are serial
            for k in list(_LIVE)[:-32]:
                _LIVE.pop(k, None)
    return b


def close(run_id, root=None):
    """Retire the run's budget -> one telemetry/budget.jsonl row. Fail-open."""
    b = _LIVE.pop(run_id, None)
    if b is None:
        return None
    try:
        row = {"t": round(time.time(), 1), **b.report()}
        tdir = os.path.join(root or DEF_ROOT, "telemetry")
        os.makedirs(tdir, exist_ok=True)
        with open(os.path.join(tdir, "budget.jsonl"), "a") as f:
            f.write(json.dumps(row) + "\n")
        return row
    except Exception:
        return None
