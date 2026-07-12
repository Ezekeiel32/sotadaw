#!/usr/bin/env python3
"""THE EVAL ROTATION (ledger dr30, 2026-07-12): 85% of the taxonomy had zero
scored eval — world-class was empirically unverified for most of the catalog.

  eval_rotation.py [N]        birth+arrange+render+check the N least-recently
                              evaled grid genres (default 4), append rows
                              tagged {"rotation": true} to eval/history.jsonl

Zero tokens (deterministic births), a few renders — run through tools/
gated.sh when the box may be busy. Each pass moves the never-evaled frontier;
~35 nights at N=6 covers the whole 204.

KNOWN BIAS (first rotation, 2026-07-12): rows measure RAW births — the
universal loudness pass lives on proposal lanes, so lufs_in_range fails
systematically here (all 4 first-rotation genres). The bias is constant, so
trends WITHIN rotation rows compare cleanly; never mix rotation scores with
brief scores. Rows carry {"rotation": true} for exactly this reason. Also:
genre_sim_ok inherits CLAP's text-label sensitivity — obscure genre names
('3step') may score low on label unfamiliarity, not musical mismatch.
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")
HIST = os.path.join(ROOT, "eval", "history.jsonl")
PY = os.path.join(ROOT, ".venv", "bin", "python")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")


def last_eval_times():
    seen = {}
    if os.path.exists(HIST):
        for ln in open(HIST):
            try:
                d = json.loads(ln)
            except json.JSONDecodeError:
                continue
            g = d.get("genre")
            if g:
                seen[g] = max(seen.get(g, 0), float(d.get("t", 0)))
    return seen


def main(n):
    genres = sorted(json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"])
    seen = last_eval_times()
    order = sorted(genres, key=lambda g: seen.get(g, 0))
    picks = order[:n]
    never = sum(1 for g in genres if g not in seen)
    print(f"rotation: {never}/{len(genres)} never evaled; picking {picks}")
    os.environ["SOTADAW_EVAL_RAW"] = "1"   # raw births: disaster floor 0.10
    from eval_daw import check_song
    out = []
    for g in picks:
        name = f"_rot_{g}"
        try:
            subprocess.run([PY, os.path.join(ROOT, "tools", "loop_gen.py"), g, f"{name}_l",
                            "--bars", "4", "--seed", "3"], capture_output=True, timeout=180)
            subprocess.run([PY, os.path.join(ROOT, "tools", "arrange.py"),
                            os.path.join(SONGS, f"{name}_l.json"), "--out", name,
                            "--genre", g], capture_output=True, timeout=180)
            r = check_song(name, g)          # renders via m1 inside
            r["rotation"] = True
            r["t"] = time.time()
            out.append(r)
            fails = [k for k, v in (r.get("checks") or {}).items() if not v]
            print(f"  {g:20} score {r.get('score')}  "
                  + ("ALL GREEN" if not fails else "fails: " + ",".join(fails)))
        except Exception as e:
            print(f"  {g:20} ERROR {e}")
        finally:
            for suf in ("_l.json", ".json", ".wav"):
                p = os.path.join(SONGS, name + suf)
                if os.path.exists(p):
                    os.remove(p)
    if out:
        os.makedirs(os.path.dirname(HIST), exist_ok=True)
        with open(HIST, "a") as f:
            for r in out:
                f.write(json.dumps(r) + "\n")
        print(f"{len(out)} rotation rows -> eval/history.jsonl")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
