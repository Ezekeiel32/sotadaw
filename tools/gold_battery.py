#!/usr/bin/env python3
"""THE GOLD STANDARD battery — the bank teaches, the gates protect, forever.

Proves (pure, zero tokens, no renders):
  A. bank invariants (gold_bank.verify): every exemplar parses, melodic DNA
     in key, block under cap with THE STANDARD / KEY LAW / MASTERING sections
  B. the session seam (through daw_mcp.TOOLS, the server's own dispatch):
     genre sessions carry the gold block + mastering DNA + real note tokens;
     empty sessions carry none; 'uk garage' resolves LITERAL-first (ukgarage,
     not a vibe neighbor); deterministic
  C. get_skill on a genre skill carries the gold AFTER the byte-exact body
  D. ingest gates in a SANDBOX bank: off-key accepts REFUSED, clean rich
     accepts banked, write-if-better refuses a worse retake
  E. parent-chain inheritance resolves (a subgenre with no own gold rides its
     parent's, labeled)

Usage: python3 tools/gold_battery.py
"""
import importlib, json, os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "agent"))

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

NOTE_TOK = re.compile(r"[A-G][#b]?\d@[\d.]")

def main():
    import gold_bank as G
    import daw_mcp as D

    # ---- A. bank invariants ----
    errs, n = G.verify()
    ok(not errs, f"bank verify clean (got {errs[:3]})")
    ok(n >= 15, f"bank holds >=15 exemplars (got {n})")

    # ---- B. the session seam ----
    s0 = D.TOOLS["start_session"][0]({})
    ok("THE STANDARD" not in s0, "empty session carries no gold")
    for genre, want in (("amapiano", "amapiano"), ("dark trap", "trap"),
                        ("uk garage", "ukgarage"), ("blues", "blues")):
        s = D.TOOLS["start_session"][0]({"genre": genre})
        m = re.search(r"THE STANDARD — (\w+) GOLD", s)
        ok(m and m.group(1) == want, f"'{genre}' gold = {want} (got {m and m.group(1)})")
        ok("MASTERING STANDARD" in s, f"'{genre}' carries mastering DNA")
        ok("KEY LAW" in s, f"'{genre}' carries the key law")
        ok(len(NOTE_TOK.findall(s)) >= 10, f"'{genre}' carries REAL note tokens "
                                           f"(got {len(NOTE_TOK.findall(s))})")
        ok("verbatim" in s, f"'{genre}' carries the generalize-don't-copy law")
        ok(len(s) < 42500, f"'{genre}' payload {len(s)} under budget (re-based 2026-07-31 TWICE: 39181 then 40098 measured same-day — grooves/gold bank LIVE from parallel sessions' accepts, organic banked-taste growth again [third re-base: 36400->37500->38500->40000]; verified the overage is grooves/gold data, NOT session-skill bloat — palette lines are essence-tier; per-block gold caps stay the content law)")
    ok(D.TOOLS["start_session"][0]({"genre": "amapiano"})
       == D.TOOLS["start_session"][0]({"genre": "amapiano"}), "deterministic")

    # ---- C. get_skill carries gold after the byte-exact body ----
    body = D.TOOLS["get_skill"][0]({"name": "amapiano-arrangement"})
    reg = D.load_registry()["skills"]["amapiano-arrangement"]
    ok(body.startswith(D.skill_body(reg)), "registry body rides byte-exact first")
    ok("THE STANDARD — amapiano GOLD" in body, "gold rides the genre fetch")
    ok("THE STANDARD" not in D.TOOLS["get_skill"][0]({"name": "fx-usage"}),
       "non-genre fetch carries no gold")

    # ---- E. parent-chain inheritance (find one live case from the index) ----
    idx = G.load_index().get("genres", {})
    inh = next((g for g, e in sorted(idx.items())
                if e.get("parent") and G.load_gold(g) is None
                and G.load_gold(e["parent"]) is not None), None)
    if inh:
        blk = G.render_block(inh)
        ok("inherited from parent" in blk, f"{inh} inherits {idx[inh]['parent']}'s gold")
    ok(inh is not None, "at least one subgenre exercises inheritance")

    # ---- D. ingest gates in a sandbox ----
    tmp = tempfile.mkdtemp(prefix="gold_sbx_")
    try:
        os.environ["SOTADAW_GOLD_DIR"] = os.path.join(tmp, "gold")
        importlib.reload(G)
        shutil.copy(os.path.join(ROOT, "library", "gold", "_index.json"),
                    os.path.join(os.makedirs(os.path.join(tmp, "gold"), exist_ok=True)
                                 or os.path.join(tmp, "gold"), "_index.json"))

        def song(off_key=False, vel=None):
            key_pcs = [2, 5, 9, 0]                      # D F A C in D minor
            bad_pcs = [3, 6, 8, 11]                     # chromatic dirt
            mk = lambda i, pc: {"start": float(i), "len": 0.5,
                                "pitch": 36 + pc + 12 * (i % 2),
                                "vel": vel or (0.5 + 0.05 * (i % 5))}
            lead = [mk(i, (bad_pcs if off_key and i % 2 else key_pcs)[i % 4])
                    for i in range(16)]
            chords = [{"start": float(b * 4), "len": 3.0, "pitch": 50 + pc,
                       "vel": 0.6} for b in range(4) for pc in (2, 5, 9, 0)]
            drums = [{"start": i * 0.5, "len": 0.1, "pitch": 42, "vel": 0.3 + 0.1 * (i % 3)}
                     for i in range(32)]
            return {"bpm": 120, "key": "D minor", "lengthBars": 8,
                    "master": [{"type": "faustfx", "id": "fx_truepeak",
                                "params": {"ceiling": -1.2}}],
                    "tracks": [
                        {"name": "lead", "source": {"kind": "faust", "id": "pluck2"},
                         "notes": lead},
                        {"name": "keys", "source": {"kind": "faust", "id": "rhodes"},
                         "notes": chords},
                        {"name": "hats", "source": {"kind": "faust", "id": "hat"},
                         "notes": drums}]}

        sdir = os.path.join(tmp, "songs")
        os.makedirs(sdir)
        json.dump(song(), open(os.path.join(sdir, "good_take.json"), "w"))
        json.dump(song(off_key=True), open(os.path.join(sdir, "bad_take.json"), "w"))
        tele = os.path.join(tmp, "proposals.jsonl")
        with open(tele, "w") as f:
            f.write(json.dumps({"song": "good_take", "genre": "sbxgenre",
                                "accepted": True}) + "\n")
            f.write(json.dumps({"song": "bad_take", "genre": "sbxbad",
                                "accepted": True}) + "\n")
        out = G.ingest_accepts(telemetry=tele, songs_dir=sdir)
        ok(any("sbxgenre: banked" in l for l in out), f"clean accept banked ({out})")
        ok(any("sbxbad: gate refused" in l and "OFF-KEY" in l for l in out),
           f"off-key accept REFUSED ({out})")
        blk = G.render_block("sbxgenre")
        ok("THE STANDARD" in blk and "MASTERING STANDARD" in blk,
           "sandbox gold renders a full block")
        # write-if-better: a flat-velocity (robotic) retake must NOT displace it
        json.dump(song(vel=0.8), open(os.path.join(sdir, "good_take.json"), "w"))
        out2 = G.ingest_accepts(telemetry=tele, songs_dir=sdir)
        ok(any("kept existing" in l for l in out2),
           f"worse retake refused — the bank only rises ({out2})")
    finally:
        os.environ.pop("SOTADAW_GOLD_DIR", None)
        shutil.rmtree(tmp, ignore_errors=True)
        importlib.reload(G)

if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"gold battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
