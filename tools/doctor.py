#!/usr/bin/env python3
"""DOCTOR — symbolic critique: what's wrong with this track + the fix tool.

  doctor.py <song>

Reads a song and reports fixable issues WITHOUT rendering (fast, glass-box),
composing the campaign's analysis: chordvote (harmony), automix roles (mix),
expressive/NOMML (feel), section + range analysis (arrangement). Every finding
names the exact tool that fixes it — the 'make it better' loop's first half.

Checks (each -> a named fix):
  H1 no harmony       -> nothing to build changes on
  A1 no sections      -> arrange / finish
  A2 doesn't breathe  -> harmonize sectioned
  M1 off-center sub   -> automix (mono_below_120)
  M2 mud collision    -> automix (symbolic unmask)
  M3 focal off-center -> automix
  F1 dead-mechanical  -> humanize
  X1 no master limiter-> finish (master safety) / add fx_brickwall
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map, is_drum_track
import automix as M
from expressive import nomml_level
import songname

# Zone truth per faust fx — ONE table, shared with the write seams
# (tools/fx_zones.py, 2026-07-24 THE PARAM COURT). setZone() is EXACT-name;
# a param not in the set is a silent no-op. New fx: add zones THERE.
from fx_zones import FX_ZONES


def diagnose(song, genre=""):
    issues = []
    tracks = song.get("tracks", [])
    melodic = [t for t in tracks if not is_drum_track(t) and t.get("notes")]

    # H1 harmony
    chords = song.get("chords") or chord_map(song)
    if not chords:
        issues.append(("H1", "no voteable harmony — add a chordal/melodic part",
                       "write chords or a melody, then chord_map"))

    # A1/A2 arrangement
    secs = song.get("sections", [])
    if len(secs) < 2:
        issues.append(("A1", "no arrangement — it's a loop, not a song",
                       "arrange_song / finish"))
    else:
        # A2 does it breathe? compare busiest vs sparsest section density on melodic parts
        lab_bar = sorted([(float(s["startBar"]), str(s.get("name", "")).lower()) for s in secs])
        def dens(track, lo, hi):
            n = sum(1 for x in track["notes"] if lo <= x["start"] // 4 < hi)
            return n / max(hi - lo, 1)
        spans = [(lab_bar[i][0], lab_bar[i + 1][0] if i + 1 < len(lab_bar) else float(song.get("lengthBars", 1)), lab_bar[i][1])
                 for i in range(len(lab_bar))]
        flat = True
        for t in melodic:
            ds = [dens(t, int(lo), int(hi)) for lo, hi, _ in spans]
            if any(d == 0 for d in ds) and any(d > 0 for d in ds):
                flat = False               # a part RESTING in sections IS breathing
                break
            ds = [d for d in ds if d > 0]
            if ds and max(ds) > min(ds) * 1.5:
                flat = False
                break
        if flat and melodic:
            issues.append(("A2", "the arrangement doesn't breathe — every section is the same density",
                           "harmonize sectioned"))

    # X4 (w58, r-23): THE GRIND SCOOP — genre-conditional; only judged
    # when the caller KNOWS the genre (the daw_mcp verdict seam has no
    # genre; run_courts + the Doctor CLI do)
    if genre:
        try:
            import metal_heal as _mh
            for a in _mh.court_metal_mix(song, genre).get("advisories", []):
                if a["kind"] == "grind_scoop_trap":
                    issues.append(("X4", a["why"], "metal_heal (clamp -3)"))
        except Exception:
            pass

    # X5 (w63, r-32): parallel-perfects / leaping comp / entropy —
    # genre-aware extremes only
    if genre:
        try:
            import symbolic_invariants as _si
            for a in _si.invariants(song, genre).get("advisories", []):
                issues.append(("X5", a["why"][:160], "see the WHY"))
        except Exception:
            pass

    # M1 off-center subs
    for t in tracks:
        if M.role(t) in ("kick", "bass") and abs(float(t.get("pan", 0))) > 1e-6:
            issues.append(("M1", f"'{t.get('name')}' (sub/kick) is panned {t.get('pan')} — cancels in mono",
                           "automix (mono_below_120)"))
        if M.role(t) in ("kick", "bass") and any(f.get("id") == "fx_widen" for f in t.get("fx", [])):
            issues.append(("M1", f"'{t.get('name')}' (sub) is WIDENED — mono cancellation",
                           "automix (strip the widener)"))

    # stereo-double pairs (X + XR, the birth doubling law) are ONE wide voice —
    # identical content on purpose; exempt from collision/focus complaints.
    _names = {t.get("name", "") for t in tracks}
    def _doubled(nm):
        nm = str(nm or "")
        return (nm + "R") in _names or (nm.endswith("R") and nm[:-1] in _names)

    # M2 mud collisions (two melodic ranges overlap in the low-mid)
    profs = []
    for t in melodic:
        ns = [n["pitch"] for n in t["notes"]]
        profs.append((t.get("name"), min(ns), max(ns)))
    for i in range(len(profs)):
        for j in range(i + 1, len(profs)):
            (na, a0, a1), (nb, b0, b1) = profs[i], profs[j]
            if str(nb) == str(na) + "R" or str(na) == str(nb) + "R":
                continue                   # the two halves of one double
            lo, hi = max(a0, b0), min(a1, b1)
            if hi - lo >= 3:
                import math
                center = (lo + hi) / 2.0
                freq = round(440.0 * 2 ** ((center - 69) / 12.0))
                if 120 <= freq <= 2000 and not any(f.get("type") == "eq" for t in melodic for f in t.get("fx", [])):
                    issues.append(("M2", f"'{na}' and '{nb}' collide around {freq}Hz (mud)",
                                   "automix (complementary EQ)"))
                    break
        else:
            continue
        break

    # M3 focal off-center (double pairs exempt: symmetric pan IS their width)
    for t in tracks:
        if M.role(t) == "focal" and abs(float(t.get("pan", 0))) > 0.2 \
           and not _doubled(t.get("name")):
            issues.append(("M3", f"'{t.get('name')}' (lead/focal) is panned {t.get('pan')} — focus wanders",
                           "automix (center the focal)"))

    # F1 dead-mechanical parts
    for t in melodic:
        if len(t["notes"]) >= 8:
            lvl, cls = nomml_level(t["notes"])
            vels = {round(n.get("vel", 0.8), 2) for n in t["notes"]}
            if cls == "mechanical" and len(vels) <= 1:
                issues.append(("F1", f"'{t.get('name')}' is dead-mechanical (on-grid, uniform velocity)",
                               "humanize"))

    # X1 no master limiter (fx_truepeak = the release wall; brickwall = legacy ok)
    if not any(f.get("id") in ("fx_truepeak", "fx_brickwall") for f in song.get("master", [])):
        issues.append(("X1", "no master limiter — the mix can clip on export",
                       "finish (master safety) or add fx_truepeak ceiling -1.2"))

    # X3 parked dark filter on the MASTER: the whole mix through mud, forever
    # (the 'barely audible' class; SWEEPS are exempt — an automated cutoff/knob
    # is motion, not a parking violation)
    autos = {str(a.get("target", "")) for a in song.get("automation", [])}
    for i, f in enumerate(song.get("master", [])):
        p = f.get("params") or {}
        if any(t.startswith(f"master[{i}].") for t in autos):
            continue
        if f.get("id") == "fx_filter":
            cut = p.get("cutoff", 20000)
            if isinstance(cut, (int, float)) and cut < 800:
                issues.append(("X3", f"master fx_filter parked dark (cutoff {int(cut)}Hz, no automation) — the whole mix is muffled",
                               "open/remove it, or automate the sweep"))
        if f.get("id") == "fx_djfilter":
            knob = p.get("knob", 0)
            if isinstance(knob, (int, float)) and knob < -0.35:
                issues.append(("X3", f"master fx_djfilter parked dark (knob {knob:+.2f}, no automation) — the whole mix is muffled",
                               "return the knob toward 0, or automate the sweep"))

    # X4 positive master volume after the wall: masterGainDb applies AFTER the
    # whole master chain — a positive value re-opens the headroom the limiter
    # just closed (the export clips 'through' the wall). Same truth the floor
    # heals (worldclass post_wall_gain) — the Doctor chip must see it too.
    try:
        mg = float(song.get("masterGainDb", 0) or 0)
    except (TypeError, ValueError):
        mg = 0.0
    if mg > 0.0 and any(f.get("id") in ("fx_truepeak", "fx_brickwall")
                        for f in song.get("master", [])):
        issues.append(("X4", f"masterGainDb {mg:+.1f} runs AFTER the wall — re-opens the clipping the limiter just closed",
                       "set masterGainDb 0; stage level with fx_trim inside the chain"))

    # X2 zone traps the schema can't see: params that silently do NOTHING
    # (upstreamed from the write-path verdict so the Doctor chip sees them too).
    # Sweeps EVERY chain that hosts fx — tracks, master, AND buses (I5, THE TEN:
    # a 'gain' trim on the verb bus no-opped just as silently). X3 deliberately
    # stays master-only: a dark filter on a reverb bus is a classic technique,
    # not a trap.
    chains = (tracks + [{"fx": song.get("master", []), "name": "master"}]
              + [{"fx": b.get("fx", []), "name": f"bus:{b.get('id', '?')}"}
                 for b in song.get("buses", []) or []])
    for t in chains:
        for f in t.get("fx", []) or []:
            if f.get("id") == "fx_trim" and "gain" in (f.get("params") or {}):
                issues.append(("X2", f"fx_trim on '{t.get('name')}' has param 'gain' — the zone is 'level'; this trim does NOTHING",
                               "rename the param to level"))
            # X2 generalized: setZone() matches zone NAMES exactly — any
            # unknown param is silently ignored and the fx runs at defaults.
            # Table = the zone declarations in instruments/fx_*.dsp; unknown
            # fx ids skip (fail-open for future fx); vst3 params are a
            # different space (natural units on display names) — exempt.
            zones = FX_ZONES.get(f.get("id"))
            if zones is not None:
                bad = [k for k in (f.get("params") or {})
                       if k not in zones
                       and not k.startswith("_")   # first-party markers (params._am)
                       and not (f.get("id") == "fx_trim" and k == "gain")]
                if bad:
                    issues.append(("X2", f"{f.get('id')} on '{t.get('name')}' has unknown param(s) {bad} — real zones: {sorted(zones)}; these do NOTHING",
                                   "rename to a real zone or remove the param"))
            if f.get("type") == "limiter":
                issues.append(("X2", f"deprecated type:'limiter' on '{t.get('name')}' — its ceiling is non-functional",
                               "use fx_truepeak (ceiling = output dBTP)"))
            # fx_widen width < 1.0 NARROWS (default 1.4 = neutral-wide; the side
            # level SCALES with width). 'Modest' values ship a MORE-mono mix —
            # this trap shipped born-mono takes for a week before it was caught.
            if f.get("id") == "fx_widen":
                w = (f.get("params") or {}).get("width")
                if w is not None and float(w) < 1.0:
                    issues.append(("X2", f"fx_widen on '{t.get('name')}' has width {w} — values <1.0 NARROW the image (1.4 = neutral)",
                                   "raise width above 1.0 (1.15-1.7) or remove the widener"))

    # M4 sub-CONTENT off-center: a lane whose NOTES live in the sub range but
    # whose NAME doesn't say bass/kick (an 808 named 'melody') — role checks
    # miss it, mono playback cancels it. Median pitch <= E2 (82Hz) = sub truth.
    for t in tracks:
        ns = [n.get("pitch", 60) for n in t.get("notes", [])]
        if len(ns) < 4 or is_drum_track(t) or M.role(t) in ("kick", "bass"):
            continue                       # drum-map numbers are NOT pitches
        med = sorted(ns)[len(ns) // 2]
        if med <= 40:
            if abs(float(t.get("pan", 0))) > 0.1:
                issues.append(("M4", f"'{t.get('name')}' plays sub-range content (median pitch {med}) panned {t.get('pan')} — cancels in mono",
                               "center it (pan 0)"))
            if any(f.get("id") == "fx_widen" for f in t.get("fx", []) or []):
                issues.append(("M4", f"'{t.get('name')}' plays sub-range content (median pitch {med}) through fx_widen — mono cancellation",
                               "strip the widener from sub content"))

    # ---- COMPOSITION completeness (DEFINITE checks only — no taste judgments) ----
    # C1 static harmony: <=1 unique chord across the whole song
    if chords:
        uniq = {c["chord"] for c in chords}
        if len(uniq) <= 1 and len(chords) >= 4:
            issues.append(("C1", f"static harmony — the whole song is one chord ({next(iter(uniq))})",
                           "reharmonize / add chord movement (write chords, reharm)"))
    # C2 register cramp: ALL melodic notes inside < 12 semitones (one octave)
    all_mel_pitches = [n["pitch"] for t in melodic for n in t["notes"]]
    if len(all_mel_pitches) >= 8 and (max(all_mel_pitches) - min(all_mel_pitches)) < 12:
        issues.append(("C2", f"cramped register — all melodic content in {max(all_mel_pitches)-min(all_mel_pitches)} semitones",
                       "spread the arrangement across octaves (move a part up/down)"))
    # C3 no low-end foundation: no bass/sub role anywhere
    if melodic and not any(M.role(t) in ("bass", "kick") for t in tracks):
        issues.append(("C3", "no low-end foundation — nothing in the bass/sub range",
                       "harmonize a bass (finish / harmonize bass)"))
    # C4 thin arrangement: a multi-section song carried by a single melodic voice
    if len(secs) >= 2 and len(melodic) <= 1:
        issues.append(("C4", "thin arrangement — one melodic voice carries the whole song",
                       "add a counter-melody or pad (harmonize pad)"))
    # C5 harmony clash: sustained STRONG-BEAT notes a semitone against the bar's
    # chord (the b9 class — definite wrongness, not taste). Conservative by law:
    # confident bars only (conf >= 0.5), notes >= 0.5 beats long ON beats 1/3,
    # and a track nags only when clashing is a PATTERN (>=3 and >=20% of its
    # strong notes) — one blue note never flags.
    if chords:
        from reharm import parse_chord, tones as _ctones
        cmap = {}
        for c in chords:
            if float(c.get("conf", 1.0)) >= 0.5:
                try:
                    r, q, d7 = parse_chord(c["chord"])
                    cmap[int(c["bar"])] = (c["chord"], set(_ctones(r, q, d7).values()))
                except SystemExit:
                    pass
        for t in melodic:
            strong = clash = 0
            ex = None
            for n in t["notes"]:
                s, ln = float(n["start"]), float(n.get("len", 0.25))
                bar = int(s // 4) + 1
                beat_in = s - (bar - 1) * 4
                if bar not in cmap or ln < 0.5 or min(beat_in % 2, 2 - beat_in % 2) > 0.1:
                    continue
                strong += 1
                label, ct = cmap[bar]
                pc = int(n["pitch"]) % 12
                if pc not in ct and any((pc - x) % 12 in (1, 11) for x in ct):
                    clash += 1
                    ex = ex or f"bar {bar}: pitch {int(n['pitch'])} against {label}"
            if strong >= 4 and clash >= 3 and clash / strong >= 0.2:
                issues.append(("C5", f"'{t.get('name')}' fights the harmony — {clash}/{strong} strong-beat notes a semitone against the chord lane ({ex})",
                               "suggest_chords (ranked alternatives) / surgical_edit to retune the clashing notes"))

    return issues


# ---- EARS-GRADE BAND TRUTH (W7) -------------------------------------------
# The symbolic checks above never hear the render; this one judges analyze2's
# measured band shares against the genre's MixTarget order + the real-record
# calibration (records ~10% lowmid, ~7-12% above 500Hz; the demo-mud class
# ships 28%+ with presence under 3% — docs/GENERATION_UPLIFT waves 5-6).
# Thresholds are EXTREMES-ONLY so a legitimately dark genre never gets nagged.
_BAND_KEYS = (("low", "low_20_120"), ("lowmid", "lowmid_120_500"),
              ("mid", "mid_500_2k"), ("himid", "himid_2k_6k"),
              ("high", "high_6k_up"))


def band_verdict(analysis, dna=None):
    """analyze2 dict (band_energy_pct) + genre dna (band_order) -> verdict
    strings, [] when clean. Pure + stdlib (the sidecar imports this live)."""
    bands = (analysis or {}).get("band_energy_pct") or {}
    if not isinstance(bands, dict) or not bands:
        return []
    shares = {short: float(bands.get(key) or 0.0) for short, key in _BAND_KEYS}
    out = []
    lm = shares["lowmid"]
    pres = shares["mid"] + shares["himid"] + shares["high"]
    # W45 CALIBRATION: the ~10% record figure was measured on ONE electronic
    # record — genres whose band_order LEADS with lowmid (jazz/bossa/gospel
    # families) live at 25-40% by identity. Their MUD bar sits at 45%
    # (pathology only); everyone else keeps the 28% mainstream bar.
    _lm_led = str((dna or {}).get("band_order") or "").startswith("lowmid")
    _mud_bar = 45.0 if _lm_led else 28.0
    if lm >= _mud_bar:
        out.append(f"MUD: lowmid {lm:.1f}% of energy "
                   f"({'even for a lowmid-led genre' if _lm_led else 'records ~10%'})"
                   " — box-cut the top 120-500Hz owner (render_cache.py "
                   "--prove-stems names it per track)")
    if pres < 3.0 and shares["low"] + lm > 80.0:
        out.append(f"PRESENCE STARVED: {pres:.1f}% above 500Hz (records "
                   "~7-12%) — brighten the lead (hi-shelf), open a filter, "
                   "or lift hats")
    want = [w for w in str((dna or {}).get("band_order") or "").split(">") if w]
    if want:
        got = sorted(shares, key=lambda k: -shares[k])
        if got and want[0] != got[0]:
            out.append(f"BAND ORDER: {got[0]} leads the mix ("
                       f"{'>'.join(got[:3])}) but this genre wants "
                       f"{'>'.join(want[:3])}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--genre", default="",
                    help="unlocks genre-conditional checks (X4 grind scoop)")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
    issues = diagnose(song, a.genre)
    if not issues:
        print(f"[doctor] {name}: CLEAN — no fixable issues found")
    else:
        print(f"[doctor] {name}: {len(issues)} issue(s):")
        for code, what, fix in issues:
            print(f"  [{code}] {what}\n        -> fix: {fix}")
    print("DOCTOR_JSON " + json.dumps([{"code": c, "issue": w, "fix": f} for c, w, f in issues]))


if __name__ == "__main__":
    main()
