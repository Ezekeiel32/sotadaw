#!/usr/bin/env python3
"""THE BRAIN BR-A — THE BANKING LAW (docs/SPEC_THE_BRAIN.md PART V).

Every gated take banks ONE tuple — (ask -> readout -> orders -> verdict) — to
telemetry/brain_tuples.jsonl: the training rows for the organs (taste head,
conductor cadet). Mounted at the ONE verdict seam (sidecar log_telemetry,
after its SANDBOX early-return, so rigs never bank junk).

LAWS:
- FAIL-OPEN EVERYWHERE: banking must never break a verdict; a missing source
  is an honest null, never a raise.
- The kernel (assemble_tuple) is PURE — every piece arrives as an argument.
  gather() does the IO joins: receipts by song incl. the _prop_ twin
  (ipc receipts.jsonl, rows keyed "song"), the last courts verdict
  (telemetry/courts.jsonl, rows keyed "prop"), the chronicle tail
  (injectable reader for rigs; real chronicle.read otherwise).
- CAPS keep tuples small and the bank readable by small models:
  receipts<=60, chronicle<=12, ask<=600, note<=400, texts<=200.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)

R_CAP, C_CAP = 60, 12          # receipts / chronicle rows per tuple
TXT, ASK, NOTE = 200, 600, 400  # text truncation caps
BANK_NAME = "brain_tuples.jsonl"


def _tail_jsonl(path, max_bytes=262144):
    """Last rows of a jsonl file, torn-line tolerant. [] on any trouble."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - max_bytes))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return []
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue                      # torn first line / mid-write row
    return out


def _default_chron_reader(song, root):
    """Real chronicle tail. Import is lazy + fail-open (rigs, moved trees)."""
    try:
        ag = os.path.join(root, "agent")
        if ag not in sys.path:
            sys.path.insert(0, ag)
        import chronicle
        rows = chronicle.read(song, limit=C_CAP) or []
        return [{"t": r.get("t"), "role": r.get("role"),
                 "text": str(r.get("text", ""))[:TXT]} for r in rows]
    except Exception:
        return []


def gather(song, root=None, ipc=None, chron_reader=None):
    """IO joins for one song's tuple. Every source degrades to empty/None."""
    root = root or DEF_ROOT
    ipc = ipc or os.path.join(root, "agent", "ipc")
    names = {song, f"_prop_{song}"}

    receipts = [r for r in _tail_jsonl(os.path.join(ipc, "receipts.jsonl"))
                if r.get("song") in names][-R_CAP:]

    courts = None
    for row in reversed(_tail_jsonl(os.path.join(root, "telemetry", "courts.jsonl"))):
        if row.get("prop") in names:
            courts = row
            break

    reader = chron_reader or _default_chron_reader
    try:
        chron = (reader(song, root) or [])[-C_CAP:]
    except Exception:
        chron = []
    return {"receipts": receipts, "courts": courts, "chronicle": chron}


def assemble_tuple(song, accepted, note="", prompt="", genre="", surgical=None,
                   metrics=None, receipts=None, courts=None, chronicle=None,
                   t=None, prop_sha=None):
    """PURE kernel: one banked row. Never raises; unserializable extras are
    stringified rather than lost."""
    row = {
        "t": round(float(time.time() if t is None else t), 1),
        "song": str(song),
        "ask": str(prompt or "")[:ASK],
        "genre": str(genre or ""),
        "verdict": {"accepted": bool(accepted), "note": str(note or "")[:NOTE]},
        "readout": {"metrics": metrics if isinstance(metrics, dict) else None,
                    "courts": courts if isinstance(courts, dict) else None,
                    "surgical": surgical if isinstance(surgical, dict) else None},
        "orders": {"receipts": (receipts or [])[-R_CAP:],
                   "n_receipts": len(receipts or [])},
        "chronicle": (chronicle or [])[-C_CAP:],
    }
    if prop_sha:
        row["prop_sha"] = str(prop_sha)[:16]
    try:
        json.dumps(row)
    except (TypeError, ValueError):
        row = json.loads(json.dumps(row, default=str))
    return row


def bank(row, path):
    """Append one tuple row. True on success."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(row) + "\n")
        return True
    except Exception:
        return False


def bank_from_verdict(song, accepted, note="", prompt="", genre="",
                      surgical=None, metrics=None, root=None, ipc=None,
                      chron_reader=None):
    """The sidecar hook: gather + assemble + append. Returns the row or None.
    NEVER raises — a verdict outranks its own bookkeeping."""
    try:
        root = root or DEF_ROOT
        prop_sha = None
        try:
            pj = os.path.join(root, "songs", f"_prop_{song}.json")
            if os.path.exists(pj):
                prop_sha = hashlib.sha256(open(pj, "rb").read()).hexdigest()
        except Exception:
            pass
        g = gather(song, root=root, ipc=ipc, chron_reader=chron_reader)
        row = assemble_tuple(song, accepted, note=note, prompt=prompt,
                             genre=genre, surgical=surgical, metrics=metrics,
                             receipts=g["receipts"], courts=g["courts"],
                             chronicle=g["chronicle"], prop_sha=prop_sha)
        ok = bank(row, os.path.join(root, "telemetry", BANK_NAME))
        return row if ok else None
    except Exception:
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: brain_bank.py <song>   (dry gather+assemble, prints the tuple)")
        sys.exit(2)
    s = sys.argv[1]
    g = gather(s)
    print(json.dumps(assemble_tuple(s, accepted=True, receipts=g["receipts"],
                                    courts=g["courts"], chronicle=g["chronicle"]),
                     indent=1))
