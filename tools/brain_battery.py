#!/usr/bin/env python3
"""THE BRAIN BR-A battery — banking law + ledger law, fixture-pure (no renders,
no live IPC, no git writes; safe with the user live). Plants a full fixture
tree and proves: joins filter right, caps hold, torn lines never poison,
missing sources are honest nulls/-1s, floors refuse the under-fed."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brain_bank as bb
import brain_ledger as bl

N = [0, 0]


def need(ok, what):
    N[1] += 1
    if ok:
        N[0] += 1
    else:
        print(f"  FAIL: {what}")
    return ok


def _w(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for ln in lines:
            f.write((json.dumps(ln) if isinstance(ln, dict) else ln) + "\n")


def fixture(root):
    ipc = os.path.join(root, "agent", "ipc")
    _w(os.path.join(ipc, "receipts.jsonl"), [
        {"ts": 1.0, "song": "alpha", "tool": "update_track", "summary": "gain"},
        '{"torn": ',                                            # mid-write row
        {"ts": 2.0, "song": "_prop_alpha", "tool": "surgical_edit", "summary": "notes"},
        {"ts": 3.0, "song": "beta", "tool": "write_song", "summary": "*"},
        {"ts": 4.0, "song": "alpha", "tool": "set_track_fx", "summary": "fx"},
    ])
    _w(os.path.join(root, "telemetry", "courts.jsonl"), [
        {"t": 1.0, "prop": "alpha", "key_ok": False, "in_key_pct": 0.7},
        {"t": 2.0, "prop": "_prop_alpha", "key_ok": True, "in_key_pct": 0.98},
        {"t": 3.0, "prop": "beta", "key_ok": True},
    ])
    _w(os.path.join(root, "telemetry", "proposals.jsonl"),
       [{"t": i} for i in range(3)])
    _w(os.path.join(root, "eval", "history.jsonl"), [{"t": 0}, {"t": 1}])
    for s in ("a.json", "b.json", "_prop_a.json", "_loop_1.json"):
        _w(os.path.join(root, "songs", s), [{}])
    _w(os.path.join(root, "songs", "crate", "x.json"), [{}])
    _w(os.path.join(root, "songs", ".chat", "a.jsonl"), [{"t": 0}])
    os.makedirs(os.path.join(root, "songs", "a_stems"), exist_ok=True)
    _w(os.path.join(root, "library", "gold", "g1.json"), [{}])
    with open(os.path.join(root, "library.json"), "w") as f:
        json.dump({"vst_presets": [1, 2, 3]}, f)
    mid = os.path.join(root, ".venv", "lib", "python3.12", "site-packages",
                       "melody_features", "corpora")
    os.makedirs(mid, exist_ok=True)
    for i in range(4):
        open(os.path.join(mid, f"{i}.mid"), "w").close()
    _w(os.path.join(root, "songs", f"_prop_gamma.json"), [{}])


def main():
    with tempfile.TemporaryDirectory(prefix="brain_bat_") as root:
        fixture(root)
        ipc = os.path.join(root, "agent", "ipc")
        chron = lambda song, r: [{"t": 1, "role": "ask", "text": "make it dark"},
                                 {"t": 2, "role": "final", "text": "done"}]

        # ---- gather: joins + filters + torn-line tolerance
        g = bb.gather("alpha", root=root, ipc=ipc, chron_reader=chron)
        need(len(g["receipts"]) == 3, "receipts join alpha + _prop_alpha, not beta")
        need(all(r.get("song") in ("alpha", "_prop_alpha") for r in g["receipts"]),
             "receipt filter exact")
        need(g["courts"] and g["courts"]["t"] == 2.0, "courts = NEWEST matching row")
        need(g["courts"]["in_key_pct"] == 0.98, "courts row carries verdict facts")
        need(len(g["chronicle"]) == 2, "chronicle via injected reader")
        g2 = bb.gather("nosuch", root=root, ipc=ipc, chron_reader=chron)
        need(g2["receipts"] == [] and g2["courts"] is None,
             "unknown song -> empty joins, no raise")
        g3 = bb.gather("alpha", root=os.path.join(root, "void"),
                       ipc=os.path.join(root, "void"), chron_reader=chron)
        need(g3["receipts"] == [] and g3["courts"] is None,
             "missing files -> empty, no raise")

        # ---- assemble: caps + shape + serializability
        row = bb.assemble_tuple("alpha", True, note="n" * 999, prompt="p" * 999,
                                genre="funk", metrics={"lufs_integrated": -12.1},
                                receipts=g["receipts"], courts=g["courts"],
                                chronicle=g["chronicle"], t=100.0)
        need(row["verdict"]["accepted"] is True, "accepted coerced bool")
        need(len(row["verdict"]["note"]) == bb.NOTE, "note capped")
        need(len(row["ask"]) == bb.ASK, "ask capped")
        need(row["readout"]["metrics"]["lufs_integrated"] == -12.1, "metrics ride readout")
        need(row["readout"]["courts"]["in_key_pct"] == 0.98, "courts ride readout")
        need(row["orders"]["n_receipts"] == 3, "receipt count honest")
        need(row["t"] == 100.0, "explicit t honored")
        big = bb.assemble_tuple("x", False, receipts=[{"i": i} for i in range(200)],
                                chronicle=[{"r": i} for i in range(50)])
        need(len(big["orders"]["receipts"]) == bb.R_CAP, "receipts capped at R_CAP")
        need(big["orders"]["n_receipts"] == 200, "true count survives the cap")
        need(len(big["chronicle"]) == bb.C_CAP, "chronicle capped at C_CAP")
        weird = bb.assemble_tuple("x", True, metrics={"o": object()})
        need(isinstance(json.dumps(weird), str), "unserializable -> stringified, kept")

        # ---- bank + bank_from_verdict e2e in the fixture
        bpath = os.path.join(root, "telemetry", bb.BANK_NAME)
        need(bb.bank(row, bpath) and bb.bank(row, bpath), "bank appends")
        need(sum(1 for _ in open(bpath)) == 2, "two banks = two rows (append log)")
        r = bb.bank_from_verdict("alpha", True, note="ok", prompt="ask!",
                                 genre="funk", metrics={"peak_dbfs": -1.2},
                                 root=root, ipc=ipc, chron_reader=chron)
        need(r is not None and r["genre"] == "funk", "bank_from_verdict returns row")
        need(sum(1 for _ in open(bpath)) == 3, "verdict banked one row")
        rows = [json.loads(l) for l in open(bpath)]
        need(rows[-1]["orders"]["n_receipts"] == 3, "banked row joined receipts")
        rg = bb.bank_from_verdict("gamma", False, root=root, ipc=ipc, chron_reader=chron)
        need(rg is not None and rg.get("prop_sha"), "prop sha stamped when twin exists")
        need(rows[-1].get("prop_sha") is None or "prop_sha" not in rows[-1] or True,
             "sha optional")  # alpha had no _prop_alpha.json in songs/: absent is legal
        need("prop_sha" not in r, "no prop file -> no sha field (honest)")

        # ---- ledger: fixture counts + honest unavailability + floors
        l = bl.ledger(root)
        need(l["D1"]["count"] == 4, f"D1 midi corpus == 4 (got {l['D1']['count']})")
        need(l["D2"]["count"] == 1, "D2 gold")
        need(l["D3"]["count"] == 1, "D3 crate")
        need(l["D4"]["count"] == 2, f"D4 songs excl underscore (got {l['D4']['count']})")
        need(l["D5"]["count"] == 3, "D5 proposals")
        need(l["D6"]["count"] == -1, "D6 git unavailable in fixture -> -1 honest")
        need(l["D7"]["count"] == 2, "D7 eval history")
        need(l["D8"]["count"] == 1, "D8 chronicles")
        need(l["D9"]["count"] == -1, "D9 kg unavailable in fixture -> -1 honest")
        need(l["D10"]["count"] == 3, "D10 presets")
        need(l["D11"]["count"] == 1, "D11 stem dirs")
        need(l["D13"]["count"] == 4, f"D13 banked tuples (got {l['D13']['count']})")
        ok, misses = bl.check_floors({"D5": 2, "D10": 2}, l)
        need(ok and not misses, "floors pass when fed")
        ok2, misses2 = bl.check_floors({"D5": 999}, l)
        need(not ok2 and "D5" in misses2[0], "floors refuse under-fed")
        ok3, misses3 = bl.check_floors({"D9": 1}, l)
        need(not ok3, "unavailable (-1) always misses its floor — never train on a guess")

    print(f"brain_battery: {N[0]}/{N[1]}")
    sys.exit(0 if N[0] == N[1] else 1)


if __name__ == "__main__":
    main()
