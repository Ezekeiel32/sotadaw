#!/usr/bin/env python3
"""THE GROOVE ENGINE (ROADMAP_0.020 W1.3): timing+velocity DNA as a transferable object.

A groove = per-16th-slot (16 slots/bar): timing offset (beats) + velocity factor.
Curated profiles ship in GROOVES; extract() learns one from any song track.

  groove.py list
  groove.py apply <song> <track> <groove> [amount 0..1]
  groove.py extract <song> <track> <new_name>
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
STORE = os.path.join(ROOT, "library", "grooves.json")

# curated profiles (offsets in beats at 4/4; slots = 16ths 0..15; vel = multiplier)
GROOVES = {
    "dilla": {
        "prov": "curated:claude/2026-07-03 (drunk swing: dragged evens, late backbeat)",
        "off": [0, .012, -.008, .022, .015, .010, -.006, .024, 0, .014, -.008, .020, .012, .011, -.004, .026],
        "vel": [1, .82, .90, .78, .95, .80, .88, .74, .98, .81, .89, .77, .94, .83, .87, .72]},
    "ukg_shuffle": {
        "prov": "curated:claude/2026-07-03 (2-step: hard 16th swing, ghosted e/a)",
        "off": [0, .030, 0, .034, 0, .028, 0, .036, 0, .030, 0, .034, 0, .028, 0, .038],
        "vel": [1, .62, .92, .70, 1, .60, .90, .72, 1, .64, .92, .68, 1, .60, .90, .74]},
    "psy_straight": {
        "prov": "curated:claude/2026-07-03 (machine grid, accented offbeat 8ths)",
        "off": [0]*16,
        "vel": [1, .78, .95, .78, 1, .78, .95, .78, 1, .78, .95, .78, 1, .78, .95, .78]},
    # R-21 GROOVE PACK (backlog wave 14): the classic MACHINE swings as slot
    # tables. TR-909 shuffle delays the off-16ths (2nd/4th of each beat) by
    # its per-amount step table; MPC swing % = off-16th delay of (pct-50)% of
    # an 8th (Roger Linn's own definition). Offsets in beats @4/4.
    "tr909_shuffle_58": {
        "prov": "curated:claude/2026-07-14 wave-14 (TR-909 shuffle ~58%: off-16ths late by 0.08 beats, ghosted)",
        "off": [0, .08, 0, .08, 0, .08, 0, .08, 0, .08, 0, .08, 0, .08, 0, .08],
        "vel": [1, .72, .90, .78, 1, .72, .90, .78, 1, .72, .90, .78, 1, .72, .90, .78]},
    "mpc_54": {
        "prov": "curated:claude/2026-07-14 wave-14 (MPC 54%: off-16th +0.04 beats — the subtle house pocket)",
        "off": [0, .04, 0, .04, 0, .04, 0, .04, 0, .04, 0, .04, 0, .04, 0, .04],
        "vel": [1, .80, .92, .80, 1, .80, .92, .80, 1, .80, .92, .80, 1, .80, .92, .80]},
    "mpc_58": {
        "prov": "curated:claude/2026-07-14 wave-14 (MPC 58%: +0.08 beats — the hip-hop default)",
        "off": [0, .08, 0, .08, 0, .08, 0, .08, 0, .08, 0, .08, 0, .08, 0, .08],
        "vel": [1, .76, .90, .74, 1, .76, .90, .74, 1, .76, .90, .74, 1, .76, .90, .74]},
    "mpc_62": {
        "prov": "curated:claude/2026-07-14 wave-14 (MPC 62%: +0.12 beats — deep swing, UKG/neo-soul edge)",
        "off": [0, .12, 0, .12, 0, .12, 0, .12, 0, .12, 0, .12, 0, .12, 0, .12],
        "vel": [1, .70, .90, .72, 1, .70, .90, .72, 1, .70, .90, .72, 1, .70, .90, .72]},
    "mpc_66": {
        "prov": "curated:claude/2026-07-14 wave-14 (MPC 66%: +0.16 beats = triplet feel)",
        "off": [0, .16, 0, .16, 0, .16, 0, .16, 0, .16, 0, .16, 0, .16, 0, .16],
        "vel": [1, .68, .88, .70, 1, .68, .88, .70, 1, .68, .88, .70, 1, .68, .88, .70]},
    "dembow_lilt": {
        "prov": "curated:claude/2026-07-03 (3-3-2 lean: pushed 'a' of 2 and 4)",
        "off": [0, .008, .004, -.014, .006, .010, -.012, .016, 0, .008, .004, -.014, .006, .010, -.012, .018],
        "vel": [1, .80, .88, .95, .92, .78, .96, .82, 1, .80, .88, .95, .92, .78, .96, .84]},
    "boombap_56": {
        "prov": "curated:claude/2026-07-03 (56% swing + heavy backbeat)",
        "off": [0, .024, 0, .026, 0, .022, 0, .028, 0, .024, 0, .026, 0, .022, 0, .028],
        "vel": [1, .74, .90, .70, 1.02, .72, .88, .68, .98, .74, .90, .70, 1.04, .72, .88, .66]},
    "jazz_swing": {
        "prov": "curated:claude/2026-07-06 (medium swing ride ~64%: delayed off-8ths, 2&4 backbeat)",
        "off": [0, .02, .14, .10, 0, .02, .14, .10, 0, .02, .14, .10, 0, .02, .14, .10],
        "vel": [1, .68, .80, .72, .98, .68, .82, .72, .95, .68, .80, .72, .98, .68, .82, .74]},
    # ---- THE GROOVE ATLAS (2026-07-09): the identity organ, genre-family wide ----
    "house_shuffle": {
        "prov": "curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents)",
        "off": [0, .022, .006, .026, 0, .020, .004, .028, 0, .022, .006, .026, 0, .020, .004, .030],
        "vel": [1, .66, .90, .70, .96, .64, .92, .68, 1, .66, .90, .70, .96, .64, .92, .72]},
    "trap_grid": {
        "prov": "curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a)",
        "off": [0]*16,
        "vel": [1, .58, .78, .60, .95, .56, .80, .62, 1, .58, .76, .58, .97, .62, .82, .66]},
    "drill_slip": {
        "prov": "curated:claude/2026-07-09 (drill's slippery lean: 3rd 16th of each beat pushed hard, light drag elsewhere)",
        "off": [0, .010, .030, .012, 0, .008, .028, .014, 0, .012, .032, .010, 0, .010, .030, .016],
        "vel": [1, .60, .82, .64, .94, .58, .84, .62, .98, .60, .82, .64, .95, .62, .86, .68]},
    "funk_pocket": {
        "prov": "curated:claude/2026-07-09 (16th funk: leans forward on the a's, audible ghosts, heavy backbeat)",
        "off": [0, .006, -.004, -.008, 0, .004, -.004, -.010, 0, .006, -.004, -.008, 0, .004, -.002, -.010],
        "vel": [1, .55, .75, .50, .98, .52, .78, .55, .95, .50, .72, .50, 1, .55, .80, .60]},
    "reggae_lean": {
        "prov": "curated:claude/2026-07-09 (behind-the-beat lag ~8-12ms, offbeat-8th bubble accents; one-drop space)",
        "off": [0, .014, .018, .014, .008, .016, .020, .014, .006, .014, .018, .016, .008, .014, .020, .018],
        "vel": [.92, .66, .95, .68, .88, .64, .96, .66, .90, .66, .94, .68, .88, .64, .96, .70]},
    "afro_lilt": {
        "prov": "curated:claude/2026-07-09 (afrobeats/afro-house anticipation: pushed a-of-beat, 3-2 bell lean)",
        "off": [0, .010, -.006, .022, 0, .012, -.004, .024, 0, .008, -.006, .020, 0, .012, -.004, .026],
        "vel": [1, .62, .88, .74, .92, .60, .90, .76, .98, .62, .86, .72, .94, .64, .92, .78]},
    # ---- RESEARCH-MEASURED profiles (R-3 fold 2026-07-14; sources in
    # docs/research_producer_mind/r-3.json — corpus studies, not hand-feel) ----
    "funk_ontop": {
        "prov": "research:R-3/2026-07-14 (expert-funk medians @100bpm: kick -12.5ms ON TOP, "
                "overall -4ms tight SD 5.3ms; JB backbeat ~1.0 ratio; mild 16th swing; "
                "ghost grammar 20-45 MIDI)",
        "off": [-.007, .011, -.005, .012, -.002, .010, -.006, .012,
                -.007, .011, -.005, .012, -.002, .010, -.006, .014],
        "vel": [1, .28, .74, .32, 1.0, .26, .78, .34, .98, .28, .72, .30, 1.02, .30, .80, .36]},
    "samba_16th": {
        "prov": "research:R-3/2026-07-14 (16th duration pattern 23/23.6/22.8/30.7% — 3rd+4th "
                "16ths AHEAD of grid, the long-fourth lilt; scales with tempo)",
        "off": [0, -.020, -.034, -.056, 0, -.020, -.034, -.056,
                0, -.020, -.034, -.056, 0, -.020, -.034, -.056],
        "vel": [1, .72, .78, .92, .96, .70, .76, .94, 1, .72, .78, .92, .96, .70, .76, .96]},
    "neosoul_drag": {
        "prov": "research:R-3/2026-07-14 (D'Angelo/Dilla class: hats STRAIGHT, snare drag "
                "+45-65ms, layered lateness, bass anticipates ~32nd; repeat identically per bar)",
        "off": [.006, .012, .008, .014, .072, .012, .008, .016,
                .006, .012, .008, .014, .078, .014, .010, .016],
        "vel": [1, .70, .84, .68, .98, .68, .84, .70, .98, .70, .82, .68, 1.0, .70, .86, .72]},
    "latin_drive": {
        "prov": "curated:claude/2026-07-09 (salsa/samba/cumbia forward energy: hairs ahead, syncopation accents)",
        "off": [0, -.006, .004, -.010, 0, -.004, .004, -.008, 0, -.006, .006, -.010, 0, -.004, .004, -.008],
        "vel": [1, .72, .85, .78, .92, .70, .88, .74, .96, .72, .86, .76, .94, .74, .90, .80]},
    "dnb_roll": {
        "prov": "curated:claude/2026-07-09 (rolling break at 170+: tight grid, ghost 16ths a hair early, 2&4 spine full)",
        "off": [0, -.004, .006, -.006, 0, -.004, .004, -.006, 0, -.004, .006, -.006, 0, -.004, .004, -.008],
        "vel": [1, .56, .80, .60, .98, .54, .78, .58, .96, .56, .82, .60, 1, .58, .84, .64]},
    "techno_drive": {
        "prov": "curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse)",
        "off": [0]*16,
        "vel": [1, .70, .94, .70, 1, .70, .94, .70, 1, .70, .94, .70, 1, .70, .94, .70]},
    "halftime_drag": {
        "prov": "curated:claude/2026-07-09 (phonk/memphis/doom drag: uniform lag, backbeat extra late)",
        "off": [0, .012, .015, .012, .010, .014, .016, .012, .025, .014, .016, .014, .010, .012, .018, .016],
        "vel": [1, .60, .78, .58, .90, .58, .80, .60, 1, .60, .76, .58, .92, .62, .82, .64]},
    "rock_drive": {
        "prov": "curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine)",
        "off": [0, -.004, -.006, -.004, 0, -.004, -.006, -.004, 0, -.004, -.006, -.004, 0, -.004, -.006, -.004],
        "vel": [1, .60, .85, .55, .98, .60, .82, .55, 1, .62, .85, .58, .97, .60, .88, .62]},
    "bounce_swing": {
        "prov": "curated:claude/2026-07-09 (jersey/NOLA/new-jack hard 16th swing ~60%, triplet lean)",
        "off": [0, .030, .006, .034, 0, .028, .004, .036, 0, .030, .006, .034, 0, .028, .004, .038],
        "vel": [1, .64, .88, .70, .95, .62, .90, .72, 1, .64, .86, .68, .96, .66, .92, .74]},
    "disco_roll": {
        "prov": "curated:claude/2026-07-09 (subtle ~53% swing, offbeat-8th hat barks, strong quarter pulse)",
        "off": [0, .012, 0, .014, 0, .010, 0, .014, 0, .012, 0, .014, 0, .010, 0, .016],
        "vel": [1, .70, .88, .68, .95, .72, .90, .70, .98, .70, .88, .68, .96, .72, .92, .74]},
    "shuffle_blues": {
        "prov": "curated:claude/2026-07-09 (66% shuffle — deeper than jazz_swing's 64%, heavy backbeat)",
        "off": [0, .03, .16, .12, 0, .03, .16, .12, 0, .03, .16, .12, 0, .03, .16, .12],
        "vel": [1, .62, .82, .68, 1, .62, .80, .66, .96, .62, .82, .68, 1, .64, .84, .70]},
}

def store():
    if os.path.exists(STORE):
        d = json.load(open(STORE))
    else:
        d = {}
    changed = False
    for k, v in GROOVES.items():
        if k not in d:
            d[k] = v; changed = True
    if changed:
        os.makedirs(os.path.dirname(STORE), exist_ok=True)
        json.dump(d, open(STORE, "w"), indent=1)
    return d

def slot_of(start):
    frac = start % 4.0
    return int(round(frac / 0.25)) % 16

def to_groovae(name_or_profile):
    """Slot profile -> GrooVAE/GMD-interoperable rows (backlog wave 14,
    R-3): per-16th-slot {"offset": fraction of a 16th in [-0.5, 0.5],
    "velocity": 0-127 where our 1.0 multiplier = 100}. Magenta's GMD/E-GMD
    convention so external groove templates and future models interop."""
    g = GROOVES.get(name_or_profile) if isinstance(name_or_profile, str) \
        else name_or_profile
    if not g:
        return None
    rows = []
    for off, vel in zip(g["off"], g["vel"]):
        rows.append({"offset": max(-0.5, min(0.5, off / 0.25)),
                     "velocity": int(max(0, min(127, round(vel * 100))))})
    return rows


def from_groovae(rows, prov="import:groovae"):
    """GrooVAE/GMD rows -> our slot profile (inverse of to_groovae)."""
    off = [max(-0.125, min(0.125, float(r.get("offset", 0)) * 0.25))
           for r in rows[:16]]
    vel = [max(0.05, min(1.27, float(r.get("velocity", 100)) / 100.0))
           for r in rows[:16]]
    while len(off) < 16:
        off.append(0.0)
        vel.append(1.0)
    return {"prov": prov, "off": off, "vel": vel}


def apply_groove(song_path, track_name, name, amount=1.0):
    g = store().get(name)
    if g is None:
        return f"unknown groove '{name}'. available: {sorted(store())}"
    song = json.load(open(song_path))
    tr = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if tr is None:
        return f"no track '{track_name}'"
    moved = 0
    for n in tr.get("notes", []):
        grid = round(n["start"] / 0.25) * 0.25
        if abs(n["start"] - grid) > 0.03:      # already humanized/off-grid: leave the feel alone
            continue
        s = slot_of(grid)
        n["start"] = round(max(0.0, grid + g["off"][s] * amount), 4)
        n["vel"] = round(min(1.0, max(0.05, n["vel"] * (1.0 + (g["vel"][s] - 1.0) * amount))), 3)
        moved += 1
    tr["groove"] = {"name": name, "amount": amount}
    json.dump(song, open(song_path, "w"), indent=1)
    return f"OK: groove '{name}' x{amount} applied to '{track_name}' ({moved} on-grid notes moved; off-grid feel preserved)"

def extract(song_path, track_name, new_name):
    song = json.load(open(song_path))
    tr = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if tr is None or not tr.get("notes"):
        return f"no notes on '{track_name}'"
    offs = [[] for _ in range(16)]
    vels = [[] for _ in range(16)]
    for n in tr["notes"]:
        grid = round(n["start"] / 0.25) * 0.25
        d = n["start"] - grid
        if abs(d) > 0.12:
            continue
        s = slot_of(grid)
        offs[s].append(d)
        vels[s].append(n["vel"])
    base_vel = max(1e-6, max((sum(v) / len(v) for v in vels if v), default=1.0))
    prof = {"prov": f"extracted:{os.path.basename(song_path)}/{track_name}",
            "off": [round(sum(o) / len(o), 4) if o else 0.0 for o in offs],
            "vel": [round((sum(v) / len(v)) / base_vel, 3) if v else 1.0 for v in vels]}
    d = store()
    d[new_name] = prof
    json.dump(d, open(STORE, "w"), indent=1)
    return f"OK: groove '{new_name}' extracted ({sum(len(o) for o in offs)} hits analyzed) -> library/grooves.json"

def extract_audio(wav_path, bpm, new_name, max_bars=32):
    """Learn a groove from AUDIO (an imported drums stem): onset-detect, find the
    grid PHASE that explains the onsets best (imports rarely start on beat 1),
    then per-16th-slot timing offsets + velocity factors — the timing DNA of
    someone else's record, transferable to any of our tracks. Feeds the KG
    (Groove node w/ provenance) so the factory can link it to genres later."""
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from chop import detect_onsets
    import wave as wavmod
    w = wavmod.open(wav_path, "rb")
    sr, sw, nch = w.getframerate(), w.getsampwidth(), w.getnchannels()
    raw = w.readframes(w.getnframes()); w.close()
    if sw == 3:                                     # m1 renders 24-bit
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        x = (x - (x >> 23 << 24)).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768.0
    if nch > 1:
        x = x.reshape(-1, nch).mean(axis=1)
    spb = 60.0 / bpm
    x = x[: int(max_bars * 4 * spb * sr)]
    # onset times need ~3ms precision (a 56% swing is only ~17ms at 104bpm):
    # fine-hop energy rise, peak-picked at the point of steepest attack — NOT
    # chop's valley-backtracked slicer (11.6ms grain + variable backtrack).
    hop = 128
    n = (len(x) // hop) * hop
    xe = x[:n] - 0.97 * np.concatenate(([0.0], x[:n - 1]))   # pre-emphasis: time every
    env = np.sqrt((xe.reshape(-1, hop) ** 2).mean(axis=1))   # hit by its CLICK, not its
    # body — kick fundamentals rise ~20ms slower than hat transients and would
    # otherwise read as fake lateness on kick/snare slots.
    strength = np.maximum(0, np.diff(env, prepend=env[0]))
    if strength.max() <= 0:
        return f"no onsets in {os.path.basename(wav_path)}"
    min_gap = max(1, int(0.06 * sr / hop))
    order = np.argsort(strength)[::-1]
    picked = []
    for i in order:
        if strength[i] < 0.05 * strength.max() or len(picked) >= max_bars * 24:
            break
        if all(abs(i - j) >= min_gap for j in picked):
            picked.append(int(i))
    ts = sorted(i * hop / sr for i in picked)
    if len(ts) < 8:
        return f"only {len(ts)} onsets in {os.path.basename(wav_path)} — not enough to learn a groove"
    tb = np.array(ts) / spb                         # onset positions in beats
    # grid phase by DENSITY MODE, not least squares: lock to where MOST hits sit
    # (the straight majority) so swung hits appear as +offsets instead of pulling
    # the whole grid toward themselves.
    cand = np.linspace(0, 0.25, 65)[:-1]
    dev_at = lambda ph: (tb - ph) - np.round((tb - ph) / 0.25) * 0.25
    density = [np.exp(-(dev_at(p) / 0.02) ** 2).sum() for p in cand]
    phase = float(cand[int(np.argmax(density))])
    dev = dev_at(phase)
    keep = np.abs(dev) <= 0.12                      # beyond an eighth of a beat = not this grid
    amps = []
    for t in ts:
        seg = x[int(t * sr): int(t * sr) + int(0.03 * sr)]
        amps.append(float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0)
    offs = [[] for _ in range(16)]
    vels = [[] for _ in range(16)]
    for i in range(len(ts)):
        if not keep[i]:
            continue
        s = int(np.round((tb[i] - phase) / 0.25)) % 16
        offs[s].append(float(dev[i]))
        vels[s].append(amps[i])
    med = lambda a: float(np.median(a))             # robust to flams/ghost outliers
    base = max(1e-9, max((med(v) for v in vels if v), default=1.0))
    prof = {"prov": f"extracted-audio:{os.path.basename(wav_path)} @{bpm}bpm (phase {phase:.3f}b)",
            "off": [round(med(o), 4) if o else 0.0 for o in offs],
            "vel": [round(med(v) / base, 3) if v else 1.0 for v in vels]}
    # SANDBOX/TEST LAW: rig extractions must NOT persist to grooves.json or the KG
    # (un-guarded, they leaked import__*_e2e Groove nodes into the brain). Skip when
    # SOTADAW_SANDBOX=1 or the name is test-shaped (import__* / *_e2e); the groove is
    # still RETURNED so the extraction path is fully exercised.
    _skip = (os.environ.get("SOTADAW_SANDBOX") == "1"
             or new_name.endswith("_e2e") or "__" in new_name)
    if not _skip:
        d = store()
        d[new_name] = prof
        json.dump(d, open(STORE, "w"), indent=1)
    msg = (f"OK: groove '{new_name}' learned from audio ({int(keep.sum())}/{len(ts)} onsets on grid, "
           f"phase {phase:.3f} beats)"
           + (" (sandbox/test — NOT persisted)" if _skip else " -> library/grooves.json"))
    if not _skip:
        try:                                        # best-effort: the graph learns it exists
            from kg import KG
            kg = KG()
            kg.upsert("Groove", new_name, prof["prov"], bpm=float(bpm))
            msg += " + KG Groove node"
        except Exception:
            pass
    return msg

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        print(json.dumps({k: v["prov"] for k, v in store().items()}, indent=1))
    elif cmd == "apply":
        print(apply_groove(os.path.join(SONGS, sys.argv[2] + ".json"), sys.argv[3], sys.argv[4],
                           float(sys.argv[5]) if len(sys.argv) > 5 else 1.0))
    elif cmd == "extract-audio":
        print(extract_audio(sys.argv[2], float(sys.argv[3]), sys.argv[4]))
    elif cmd == "extract":
        print(extract(os.path.join(SONGS, sys.argv[2] + ".json"), sys.argv[3], sys.argv[4]))


def seed_kg():
    """Curated grooves -> KG Groove nodes + HAS_GROOVE genre edges (git truth for
    the docker-volume graph; idempotent). Extracted-audio grooves self-register
    at extraction time; this covers the shipped curated profiles."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from kg import KG
    kg = KG()
    d = store()
    LINKS = {"dilla": ["boombap", "triphop", "lofi"],
             "ukg_shuffle": ["ukgarage", "speed_garage", "future_garage"],
             "psy_straight": ["psytrance", "goa"],
             "dembow_lilt": ["dembow", "reggaeton", "dancehall"],
             "boombap_56": ["boombap", "hiphop"]}
    for name, genres in LINKS.items():
        if name not in d:
            continue
        kg.upsert("Groove", name, d[name]["prov"])
        for g in genres:
            kg.link("Genre", g, "HAS_GROOVE", "Groove", name)
    print("KG grooves:", kg.q("MATCH (n:Groove) RETURN count(n)")[0][0],
          "| HAS_GROOVE:", kg.q("MATCH ()-[r:HAS_GROOVE]->() RETURN count(r)")[0][0])

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "seed-kg":
    seed_kg()
