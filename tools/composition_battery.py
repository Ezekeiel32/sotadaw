#!/usr/bin/env python3
"""THE COMPOSITION BATTERY — the durable guardian for waves 14-26 (the
composition turn, 2026-07-10). Every law here shipped with full controlled-
attribution receipts; this battery re-proves the fast core (pure JSON, no
renders) so a future session that breaks a flag path turns the suite red.

Laws under guard (kill env in parens):
  W14 hook engine     musicality floors on 4 genres (strong_ct/cadence/climax)
  W16 counter         (SOTADAW_COUNTER)    answers in gaps, in key, no overlap
  W17 turnaround      (SOTADAW_TURNAROUND) trap kick develops; house kick SACRED
  W18 verse recites   (SOTADAW_VERSE)      chant = chord tones; chorus sacred
  W19 808 slide       (SOTADAW_SLIDE808)   voice swap + within-bar legato
  W20 trans variety   (SOTADAW_TRANSVAR)   riser first drop; revcrash later
  W21 hat fabric      (SOTADAW_HATFAB)     verse thins; drop-1 fabric sacred
  W22 arp breathes    (SOTADAW_ARPFAB)     drop-1 restrains; later sacred
  W23 outro speaks    (SOTADAW_OUTRO)      club subtracts; song tags
  W24 pocket          (SOTADAW_POCKET)     verse lays back; chorus on top
  W25 verse band      (SOTADAW_VERSEBAND)  kick heartbeat; bass sits back
  W26 chorus lifts    (SOTADAW_CHORUSLIFT) ride+clap pure addition

Strategy: one BIRTH per (genre, seed) with flags default-on, arranged once
per flag-off + once all-on; W19 gets its own birth (a loop_gen flag).
Runtime target < 90s. Exit 0 = clean.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import loop_gen as LG
import musicality as MU

SONGS = os.path.join(ROOT, "songs")
HATS, SNARES = {42, 44, 46}, {38, 40}
fails = []


def check(tag, ok, detail=""):
    print(f"  {'ok' if ok else 'XX'} {tag} {detail}")
    if not ok:
        fails.append(tag)


def sh(cmd, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    subprocess.run(cmd, check=True, capture_output=True, cwd=ROOT, env=e, timeout=120)


def birth(genre, seed, name, env=None):
    sh([sys.executable, "tools/loop_gen.py", genre, name, "--bars", "4",
        "--seed", str(seed)], env)
    return json.load(open(os.path.join(SONGS, name + ".json")))


def arr(name, out, env=None):
    sh([sys.executable, "tools/arrange.py", os.path.join(SONGS, name + ".json"),
        "--out", out], env)
    return json.load(open(os.path.join(SONGS, out + ".json")))


def spans(song, base):
    secs = song["sections"]
    o = []
    for i, s in enumerate(secs):
        if s["name"].rstrip("0123456789") == base:
            b1 = secs[i + 1]["startBar"] if i + 1 < len(secs) else song["lengthBars"]
            o.append((s["startBar"] * 4.0, b1 * 4.0))
    return o


def lane(song, nm):
    return next((t for t in song["tracks"] if t.get("name") == nm), None)


def in_span(tr, sps, pitch_set=None):
    return [n for n in (tr["notes"] if tr else [])
            if any(a <= n["start"] < b for a, b in sps)
            and (pitch_set is None or n.get("pitch") in pitch_set)]


def cells(tr, pitch_set=None):
    from collections import defaultdict
    c = defaultdict(set)
    for n in tr["notes"]:
        if pitch_set is None or n.get("pitch") in pitch_set:
            c[int(n["start"] // 16)].add(
                (int(round((n["start"] % 16.0) * 4)), n["pitch"]))
    return len({frozenset(v) for v in c.values() if v})


def main():
    # births (flags all default ON)
    for g, s in (("house", 23), ("synthwave", 42), ("trap", 11), ("gospel", 13)):
        birth(g, s, f"_cmp_{g}")
    on = {g: arr(f"_cmp_{g}", f"_cmp_{g}_on")
          for g in ("house", "synthwave", "trap", "gospel")}

    # W14: musicality floors on the arranged takes (lead-bearing)
    for g in ("house", "synthwave", "trap", "gospel"):
        r = MU.score(json.load(open(os.path.join(SONGS, f"_cmp_{g}.json"))), g)
        ok = (r.get("lead") and (r["strong_ct"] is None or r["strong_ct"] >= 0.7)
              and r["climax_count"] <= 3
              and (r["cadence_ct"] is None or r["cadence_ct"] >= 0.5))
        check(f"W14 {g} hook floors", bool(ok),
              f"(strong {r.get('strong_ct')} cadence {r.get('cadence_ct')})")

    # W16 counter: house answers, synthwave (wall-of-8ths) correctly none
    ho = on["house"]
    ctr = lane(ho, "counter")
    root, iv = LG.key_scale(ho.get("key") or "A minor")
    pcs = {(root + v) % 12 for v in iv}
    lead_h = lane(ho, "lead")
    clash = 0
    if ctr:
        for c in ctr["notes"]:
            c0, c1 = c["start"], c["start"] + c["len"]
            for l in lead_h["notes"]:
                if c0 < l["start"] + l.get("len", 0.5) - 1e-6 and l["start"] < c1 - 1e-6:
                    clash += 1
                    break
    check("W16 house counter answers in key, no overlap",
          ctr is not None and all(n["pitch"] % 12 in pcs for n in ctr["notes"])
          and clash == 0, f"({len(ctr['notes']) if ctr else 0} notes)")
    check("W16 synthwave conditional (lead never breathes)",
          lane(on["synthwave"], "counter") is None)

    # W17: trap kick develops; house kick SACRED vs flag-off
    t_off = arr("_cmp_trap", "_cmp_trap_toff", {"SOTADAW_TURNAROUND": "0"})
    check("W17 trap kick develops",
          cells(lane(on["trap"], "kick")) > cells(lane(t_off, "kick")),
          f"({cells(lane(t_off, 'kick'))} -> {cells(lane(on['trap'], 'kick'))})")
    h_off = arr("_cmp_house", "_cmp_house_toff", {"SOTADAW_TURNAROUND": "0"})
    key_of = lambda tr: {(round(n["start"], 4), n["pitch"], n["vel"]) for n in tr["notes"]}
    check("W17 house kick SACRED",
          key_of(lane(ho, "kick")) == key_of(lane(h_off, "kick")))

    # W18: gospel verse chant = chord tones (journey-aware not needed: verse shift 0,
    # turnaround bars excluded), chorus lead sacred vs flag-off
    go = on["gospel"]
    g_off = arr("_cmp_gospel", "_cmp_gospel_voff", {"SOTADAW_VERSE": "0"})
    vsp, csp = spans(go, "verse"), spans(go, "chorus")
    dna, _ = LG.genre_dna("gospel")
    prog = ((go.get("_loop") or {}).get("chords")   # W87: the TAKE's field
            or (dna.get("grid") or {}).get("chords") or [[0, 1]])
    pspan = max(b for b, _ in prog) + 1
    groot, giv = LG.key_scale(go.get("key") or dna.get("key") or "A minor")

    def deg_at(bar):
        d = 1
        for b0, dd in sorted(prog):
            if bar % pspan >= b0:
                d = dd
        return d

    turn_bars = {int(a // 4) - 1 for a, _ in csp}
    ok_ct = True
    for n in in_span(lane(go, "lead"), vsp):
        bar = int(n["start"] // 4)
        if bar in turn_bars:
            continue
        cd = deg_at(bar)
        cpcs = {(groot + giv[(cd + o - 1) % 7]) % 12 for o in (0, 2, 4)}
        if n["pitch"] % 12 not in cpcs:
            ok_ct = False
            break
    check("W18 gospel verse chant = chord tones", ok_ct)
    sig = lambda ns: [(round(n["start"], 4), n["pitch"]) for n in ns]
    check("W18 chorus hook sacred",
          sig(in_span(lane(go, "lead"), csp)) == sig(in_span(lane(g_off, "lead"), csp)))

    # W19: trap bass = slide voice + within-bar legato; flag-off = kick_808
    tb = lane(json.load(open(os.path.join(SONGS, "_cmp_trap.json"))), "bass")
    check("W19 trap bass voice", tb["source"]["id"] == "sub_808_slide")
    birth("trap", 11, "_cmp_trap_soff", {"SOTADAW_SLIDE808": "0"})
    tb0 = lane(json.load(open(os.path.join(SONGS, "_cmp_trap_soff.json"))), "bass")
    ns = sorted(tb["notes"], key=lambda n: n["start"])
    pairs = [(a, b) for a, b in zip(ns, ns[1:])
             if int(a["start"] // 4) == int(b["start"] // 4) and b is not ns[-1]]
    check("W19 within-bar legato + legacy voice",
          tb0["source"]["id"] == "kick_808"
          and pairs and all(a["start"] + a["len"] > b["start"] + 1e-6 for a, b in pairs))

    # W20: house riser first drop only; revcrash on later drops
    dsp = [a for a, _ in spans(ho, "drop")]
    riser, rev = lane(ho, "riser"), lane(ho, "revcrash")
    check("W20 riser first / revcrash later",
          riser is not None and len(riser["notes"]) == 1
          and rev is not None and len(rev["notes"]) == len(dsp) - 1,
          f"(drops {len(dsp)})")

    # W21: gospel verse hats thin vs flag-off; house drop-1 hats sacred
    g_hoff = arr("_cmp_gospel", "_cmp_gospel_hoff", {"SOTADAW_HATFAB": "0"})
    n_on = sum(len(in_span(t, vsp, HATS)) for t in go["tracks"])
    n_off = sum(len(in_span(t, vsp, HATS)) for t in g_hoff["tracks"])
    check("W21 gospel verse hats thin", 0 < n_on < n_off, f"({n_off} -> {n_on})")
    h_hoff = arr("_cmp_house", "_cmp_house_hoff", {"SOTADAW_HATFAB": "0"})
    d1 = spans(ho, "drop")[:1]
    hsig = lambda song: sorted((round(n["start"], 4), n["pitch"], n["vel"])
                               for t in song["tracks"] for n in in_span(t, d1, HATS))
    check("W21 house drop-1 fabric sacred", hsig(ho) == hsig(h_hoff))

    # W22: synthwave arp drop-1 restrains, later drops sacred
    so = on["synthwave"]
    s_aoff = arr("_cmp_synthwave", "_cmp_synthwave_aoff", {"SOTADAW_ARPFAB": "0"})
    sd = spans(so, "drop")
    a_on = in_span(lane(so, "arp"), sd[:1])
    a_off = in_span(lane(s_aoff, "arp"), sd[:1])
    later_same = all(sig(in_span(lane(so, "arp"), [w]))
                     == sig(in_span(lane(s_aoff, "arp"), [w])) for w in sd[1:])
    check("W22 arp drop-1 restrains, later sacred",
          a_on and len(a_on) < len(a_off) and later_same,
          f"({len(a_off)} -> {len(a_on)})")

    # W23: house outro = staged exit (hats gone 2nd half); gospel tag exists
    osp = spans(ho, "outro")[0]
    half = osp[0] + (osp[1] - osp[0]) / 2
    hats2 = [n for t in ho["tracks"] for n in in_span(t, [(half, osp[1])], HATS)]
    check("W23 house outro staged exit", not hats2)
    g_osp = spans(go, "outro")[0]
    g_ooff = arr("_cmp_gospel", "_cmp_gospel_ooff", {"SOTADAW_OUTRO": "0"})
    check("W23 gospel outro tag",
          in_span(lane(go, "lead"), [g_osp])
          and not in_span(lane(g_ooff, "lead"), [g_osp]))

    # W24: gospel verse lead lays back +0.03 vs flag-off
    g_poff = arr("_cmp_gospel", "_cmp_gospel_poff", {"SOTADAW_POCKET": "0"})
    v_on = sorted(in_span(lane(go, "lead"), vsp), key=lambda n: n["start"])
    v_off = sorted(in_span(lane(g_poff, "lead"), vsp), key=lambda n: n["start"])
    check("W24 verse pocket +0.03",
          len(v_on) == len(v_off)
          and all(abs((a["start"] + 0.03) - b["start"]) < 1e-6
                  for a, b in zip(v_off, v_on)))

    # W25: gospel verse kick = heartbeat; bass sits back x0.878
    g_vboff = arr("_cmp_gospel", "_cmp_gospel_vboff", {"SOTADAW_VERSEBAND": "0"})
    k_on = in_span(lane(go, "kick"), vsp)
    k_off = in_span(lane(g_vboff, "kick"), vsp)
    hb = lambda s: (s % 4.0) < 0.08 or abs((s % 4.0) - 2.0) < 0.08 or (s % 4.0) > 3.92
    bv = lambda song: [n["vel"] for n in in_span(lane(song, "bass"), vsp)]
    von, voff = bv(go), bv(g_vboff)
    ratio = (sum(von) / len(von)) / (sum(voff) / len(voff)) if von and voff else 1.0
    check("W25 verse band skeleton + sit-back",
          k_on and len(k_on) < len(k_off) and all(hb(n["start"]) for n in k_on)
          and abs(ratio - 0.72 / 0.82) < 0.02,
          f"(kick {len(k_off)}->{len(k_on)}, bass x{ratio:.3f})")

    # W30: the club intro whispers the hook (last 4 bars, lead notes exist);
    # W31: the club break RESTS the hook (zero lead notes)
    isp = spans(ho, "intro")[0]
    tease = in_span(lane(ho, "lead"), [isp])
    check("W30 house intro tease",
          tease and all(n["start"] >= isp[1] - 16.0 for n in tease),
          f"(+{len(tease)})")
    bsp = spans(ho, "break")
    check("W31 house break rests the hook",
          bsp and not [n for t in ho["tracks"]
                       if t.get("name", "").lower().startswith("lead")
                       for n in in_span(t, bsp)])

    # W33: the delay throw exists on the house lead, targets its REAL delay,
    # rides THROUGH the boundary (settle point past a section start)
    lead_h = lane(ho, "lead")
    thr = [a for a in lead_h.get("automation", []) if a["target"].endswith(".mix")]
    ok33 = False
    if len(thr) == 1:
        di = int(thr[0]["target"].split("[")[1].split("]")[0])
        pts = thr[0]["points"]
        sec_starts = {s["startBar"] * 4.0 for s in ho["sections"]}
        ok33 = (lead_h["fx"][di].get("id") == "fx_delay"
                and all(pts[i]["beat"] < pts[i + 1]["beat"]
                        for i in range(len(pts) - 1))
                and any(p["beat"] > b for p in pts for b in sec_starts))
    check("W33 house delay throw (real target, rides through)", ok33,
          f"({len(thr[0]['points']) // 4 if thr else 0} throws)")

    # W34: the final turnaround bar's foundation is the V (bass sounds the
    # V root; kernel-owned so the ruler reads the same field)
    fin34 = None
    for i, sct in enumerate(ho["sections"]):
        if i > 0 and sct["name"].rstrip("0123456789") in ("chorus", "drop"):
            fin34 = sct["startBar"] - 1
    r34, iv34 = LG.key_scale(ho.get("key") or "A minor")
    v_pc = (r34 + iv34[4]) % 12
    bass34 = [n for n in lane(ho, "bass")["notes"]
              if fin34 * 4.0 <= n["start"] < (fin34 + 1) * 4.0]
    check("W34 house cadence bar sounds the V",
          fin34 is not None and bass34
          and any(n["pitch"] % 12 == v_pc for n in bass34),
          f"(bar {fin34})")

    # W36: gospel's intro ends on the triplet pickup (V-field, last beat)
    gisp = spans(go, "intro")[0]
    pkup = [n for n in lane(go, "lead")["notes"]
            if gisp[1] - 1.0 <= n["start"] < gisp[1]]
    check("W36 gospel pickup in the last intro beat", 2 <= len(pkup) <= 3,
          f"(+{len(pkup)})")

    # W38: the final arrival's fill starts a bar earlier (house roll tier)
    dl38 = [x["startBar"] * 4.0 for i, x in enumerate(ho["sections"])
            if i > 0 and x["name"].rstrip("0123456789") in ("drop", "chorus")]
    fd38 = dl38[-1]
    early = [n for t in ho["tracks"] if t.get("name") == "snare"
             for n in t.get("notes", [])
             if fd38 - 12.0 <= n["start"] < fd38 - 8.0 and n["vel"] <= 0.5]
    check("W38 house last fill starts earlier", len(early) >= 4, f"(+{len(early)})")

    # W26: gospel lift lanes exist, chorus-confined, pure addition
    ride, clap = lane(go, "ride"), lane(go, "clap")
    g_loff = arr("_cmp_gospel", "_cmp_gospel_loff", {"SOTADAW_CHORUSLIFT": "0"})
    pre_same = all(
        json.dumps(lane(go, t.get("name")), sort_keys=True)
        == json.dumps(t, sort_keys=True)
        for t in g_loff["tracks"])
    check("W26 chorus lift pure addition",
          ride is not None and clap is not None
          and all(any(a <= n["start"] < b for a, b in csp) for n in ride["notes"])
          and pre_same,
          f"(ride {len(ride['notes']) if ride else 0} clap {len(clap['notes']) if clap else 0})")

    # W80 THE FILL ATLAS: 30 census-mapped genres own their family's fill
    # verb (map-level law — a symbolic pin keeps the mapping from silently
    # reverting to the generic roll)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import arrange as AR
    check("W80 fill atlas mappings hold",
          AR.FILL_STYLE.get("grime") == "hat_stutter"
          and AR.FILL_STYLE.get("ukgarage") == "break_chop"
          and AR.FILL_STYLE.get("jazz") == "ghost_drag"
          and AR.FILL_STYLE.get("dancehall") == "dropout"
          and AR.FILL_STYLE.get("electro") == "hat_stutter",
          f"({len(AR.FILL_STYLE)} genres mapped)")

    # W81 THE MODULATION: the final arrival lifts +2 for song-lift genres;
    # drums + noise one-shots exempt; the stamp rides the file for the ruler
    birth("pop", 27, "_cmp_pop")
    m_on = arr("_cmp_pop", "_cmp_pop_mon")
    m_off = arr("_cmp_pop", "_cmp_pop_moff", {"SOTADAW_MODULATE": "0"})
    _mod = m_on.get("_modulation") or {}
    _mf = float(_mod.get("fromBeat", -1))
    def _lead_post(sng):
        t = next((t for t in sng["tracks"] if t.get("name") == "lead"), {})
        return sorted((round(n["start"], 3), n["pitch"]) for n in t.get("notes", [])
                      if n["start"] >= _mf - 1e-6)
    _a, _b = _lead_post(m_on), _lead_post(m_off)
    check("W81 modulation lifts the final arrival (+2, stamped)",
          bool(_mod) and _mod.get("semitones") == 2 and len(_a) == len(_b)
          and all(pa == pb + 2 and sa == sb for (sa, pa), (sb, pb) in zip(_a, _b)),
          f"(fromBeat {_mf}, {len(_a)} lead notes)")

    # W90 THE FINAL LIFT CHOIR: the last chorus doubles the hook +12 on
    # its own lane (exact copy, softer), MODULATE genres only
    _oc90 = next((t for t in m_on["tracks"] if t.get("name") == "lead_oct"), None)
    _mod90 = m_on.get("_modulation") or {}
    _lead90 = next((t for t in m_on["tracks"] if t.get("name") == "lead"), {"notes": []})
    _mf90 = _mod90.get("fromBeat", 0)
    _fin90 = sorted((round(n["start"], 4), n["pitch"]) for n in _lead90["notes"]
                    if _mf90 - 1e-6 <= n["start"] < _mf90 + 32.0)
    check("W90 the final chorus choirs (+12 exact)",
          _oc90 is not None and _fin90
          and sorted((round(n["start"], 4), n["pitch"] - 12)
                     for n in _oc90["notes"]) == _fin90,
          f"({len(_oc90['notes']) if _oc90 else 0} choir notes)")

    # W89 THE PRE-CHORUS RISE: gospel builds climb into choruses on the
    # counter (6 ascending diatonic steps at fixed offsets, vel ramp)
    # (pop pins it: gospel's dense recite never breathes -> no counter ->
    # correctly NO rise, the W16 conditional law twice over)
    _ctr89 = next((t for t in m_on["tracks"] if t.get("name") == "counter"),
                  {"notes": []})
    _ch89 = [x["startBar"] * 4.0 for x in m_on["sections"]
             if x["name"].rstrip("0123456789") in ("chorus", "drop")]
    _rise89 = 0
    for _ds in _ch89:
        _run = [n for n in _ctr89["notes"]
                if any(abs(n["start"] - (_ds + o)) < 0.01
                       for o in (-8.0, -6.0, -4.0, -3.0, -2.0, -1.5))]
        if len(_run) >= 6:
            _pp = [n["pitch"] for n in sorted(_run, key=lambda n: n["start"])[-6:]]
            if all(b > a for a, b in zip(_pp, _pp[1:])):
                _rise89 += 1
    check("W89 the pre-chorus rises (pop)", _rise89 >= 1, f"({_rise89} rises)")

    # W88 THE BREAKDOWN MOMENT: breaks gain the washed half-time hook
    # quote on a 'breath' lane; the W31 rest law untouched (lead* silent)
    _br88 = next((t for t in ho["tracks"] if t.get("name") == "breath"), None)
    _bsp88 = spans(ho, "break")
    check("W88 the break has its moment (washed, lead still rests)",
          _br88 is not None and _bsp88
          and all(any(a <= n["start"] < b for a, b in _bsp88)
                  for n in _br88["notes"])
          and all(n["vel"] <= 0.5 for n in _br88["notes"]),
          f"({len(_br88['notes']) if _br88 else 0} breath notes)")

    # W86 THE ARRIVAL STEP: every drop earns the hole (first included) and
    # the bass rests through the last 4 build bars (its return IS the drop)
    birth("house", 23, "_cmp_h86")
    h86 = arr("_cmp_h86", "_cmp_h86_on")
    h86_off = arr("_cmp_h86", "_cmp_h86_off", {"SOTADAW_BASSRESERVE": "0"})
    _drops86 = [x["startBar"] * 4.0 for x in h86["sections"]
                if x["name"].startswith("drop")]
    _bass86 = next((t for t in h86["tracks"]
                    if t.get("name") == "bass"), {"notes": []})
    _bass86off = next((t for t in h86_off["tracks"]
                       if t.get("name") == "bass"), {"notes": []})
    _resv_ok = all(sum(1 for n in _bass86["notes"]
                       if ds - 16.0 <= n["start"] < ds - 0.05) <= 1
                   for ds in _drops86 if ds >= 16.0)   # <=1: the V-cadence hit
    _off_more = all(sum(1 for n in _bass86off["notes"]
                        if ds - 16.0 <= n["start"] < ds - 0.05)
                    > sum(1 for n in _bass86["notes"]
                          if ds - 16.0 <= n["start"] < ds - 0.05)
                    for ds in _drops86 if ds >= 16.0)
    check("W86 bass reservation (rests except the cadence; off plays)",
          _resv_ok and _off_more, f"({len(_drops86)} arrivals)")

    # W84 THE RHYTHM TAKES: hooks re-speak the genre rhythm per take
    # (census had found ONE rhythm forever); seed law stays byte-exact
    def _rhy(name):
        sng = json.load(open(os.path.join(SONGS, name + ".json")))
        t = next((t for t in sng["tracks"] if t.get("name") == "lead"), {})
        ns = sorted(t.get("notes", []), key=lambda n: n["start"])[:24]
        return tuple(round((n["start"] % 16.0) * 4) / 4 for n in ns)
    birth("pop", 3, "_cmp_rt3"); birth("pop", 17, "_cmp_rt17"); birth("pop", 99, "_cmp_rt99")
    check("W84 rhythm takes vary",
          len({_rhy("_cmp_rt3"), _rhy("_cmp_rt17"), _rhy("_cmp_rt99")}) >= 2)

    # ---- THE THROUGH-COMPOSED FORM (2026-07-11) ----
    # 12 KG genres carry form_family "through_composed" and arrange.py never read
    # it — a CARNATIC RAGA arranged intro/build/DROP/break/DROP2/outro. These
    # musics unfold: no drop, no repeat, monotonic growth to one climax.
    birth("carnatic", 3, "_cmp_tc")
    tc = arr("_cmp_tc", "_cmp_tca")
    tc_secs = [s["name"] for s in tc["sections"]]
    check("through-composed: no club drop/build in a raga",
          not any(s.rstrip("0123456789") in ("drop", "build") for s in tc_secs),
          str(tc_secs))
    check("through-composed: the unfolding arc",
          tc_secs == ["opening", "statement", "development", "intensify", "climax", "resolve"],
          str(tc_secs))
    # the OPENING is texture alone — the rhythm section has not entered yet
    _tcsp = {s["name"]: (s["startBar"] * 4.0,
                         (tc["sections"][i + 1]["startBar"] if i + 1 < len(tc["sections"])
                          else tc["lengthBars"]) * 4.0)
             for i, s in enumerate(tc["sections"])}
    def _lanes(sec):
        b0, b1 = _tcsp[sec]
        return {t["name"] for t in tc["tracks"]
                if any(b0 <= n["start"] < b1 for n in t.get("notes", []))}
    _open, _clim = _lanes("opening"), _lanes("climax")
    check("through-composed: opening carries no drums (the alapana law)",
          not any(w in n for n in _open for w in ("kick", "hat", "snare", "clap")),
          str(sorted(_open)))
    check("through-composed: the ensemble ACCUMULATES (climax > opening)",
          len(_clim) > len(_open), f"open {len(_open)} -> climax {len(_clim)}")
    # and a club genre must be UNTOUCHED by all of this
    birth("techno", 3, "_cmp_tcl")
    _cl = [s["name"] for s in arr("_cmp_tcl", "_cmp_tcla")["sections"]]
    check("through-composed: club forms unchanged", "drop" in _cl and "build" in _cl, str(_cl))

    # ---- WAVE 42: the beatless family joined through_composed (2026-07-11) ----
    # ambient/drone/orchestral_cinematic fell to the generic DROP-form (probe
    # receipt: ['intro','build','drop','break','drop2','outro'] on all three) —
    # an AMBIENT piece with a drop betrays the genre. Rock-kin joined "song".
    birth("ambient", 3, "_cmp_amb")
    _amb = [s["name"] for s in arr("_cmp_amb", "_cmp_amba")["sections"]]
    check("wave42: ambient never drops",
          not any(s.rstrip("0123456789") in ("drop", "build") for s in _amb), str(_amb))
    check("wave42: ambient unfolds", _amb[:1] == ["opening"] and "climax" in _amb, str(_amb))
    birth("metal", 3, "_cmp_mtl")
    _mtl = [s["name"] for s in arr("_cmp_mtl", "_cmp_mtla")["sections"]]
    check("wave42: metal is verse/chorus, not a DJ tool",
          any(s.startswith("verse") for s in _mtl) and any(s.startswith("chorus") for s in _mtl)
          and not any(s.rstrip("0123456789") == "drop" for s in _mtl), str(_mtl))

    # ---- THE REPEAT CRIME (dr07, 2026-07-12): no section instance is a
    # byte-copy of its first occurrence — drop2 re-breathes the hats, verse2
    # sheds its bed for the first half, the final chorus lifts an octave
    # layer. SOTADAW_REPEATVAR=0 restores the clone (kill-switch law).
    _dsp = spans(ho, "drop")
    _hat = lane(ho, "hat")
    _fph = lambda tr, sp: sorted(round((n["start"] - sp[0]) % 16, 3)
                                 for n in tr["notes"] if sp[0] <= n["start"] < sp[1])
    check("dr07 drop2 breathes (hat onsets differ from drop)",
          len(_dsp) >= 2 and _fph(_hat, _dsp[0]) != _fph(_hat, _dsp[1]),
          f"({len(_fph(_hat, _dsp[0]))} vs {len(_fph(_hat, _dsp[1]))} onsets)")
    # kill-switch: flag-off restores the old behaviors on the moves this flag
    # OWNS — verse2 keeps its bed and the last chorus stays undoubled. (Hats
    # differ across drops even flag-off: W21's fabric law owns that, by design.)
    g_rv = arr("_cmp_gospel", "_cmp_gospel_rvoff", {"SOTADAW_REPEATVAR": "0"})
    _vspo, _colo = spans(g_rv, "verse"), lane(g_rv, "color")
    _fho = lambda sp: [n for n in (_colo["notes"] if _colo else [])
                       if sp[0] <= n["start"] < (sp[0] + sp[1]) / 2]
    _cspo = spans(g_rv, "chorus")
    _ldno = [n for n in lane(g_rv, "lead")["notes"]
             if _cspo[-1][0] <= n["start"] < _cspo[-1][1]]
    check("dr07 kill-switch restores the clone (bed back, no octave layer)",
          len(_fho(_vspo[1])) > 0 and not any(
              abs(a["start"] - b["start"]) < 1e-6 and a["pitch"] - b["pitch"] == 12
              for a in _ldno for b in _ldno if a is not b))
    _vsp = spans(go, "verse")
    _col = lane(go, "color")
    _fh = lambda sp: [n for n in (_col["notes"] if _col else [])
                      if sp[0] <= n["start"] < (sp[0] + sp[1]) / 2]
    check("dr07 verse2 sheds the bed for its first half",
          len(_vsp) >= 2 and _col is not None
          and len(_fh(_vsp[1])) == 0 < len(_fh(_vsp[0])),
          f"(v1 {len(_fh(_vsp[0]))} -> v2 {len(_fh(_vsp[1]))})")
    _csps = spans(go, "chorus")
    _ldn = [n for n in lane(go, "lead")["notes"]
            if _csps[-1][0] <= n["start"] < _csps[-1][1]]
    _ld1 = [n for n in lane(go, "lead")["notes"]
            if _csps[0][0] <= n["start"] < _csps[0][1]]
    _has_dbl = lambda ns: any(abs(a["start"] - b["start"]) < 1e-6
                              and a["pitch"] - b["pitch"] == 12
                              for a in ns for b in ns if a is not b)
    check("dr07 final chorus lifts an octave layer (first chorus clean)",
          len(_csps) >= 3 and _has_dbl(_ldn) and not _has_dbl(_ld1),
          f"(last {len(_ldn)} notes vs first {len(_ld1)})")

    # ---- THE WORLD KIT (dr28, 2026-07-12): the signature cells are LAW —
    # a wrong clave is not a variation, it is a wrong genre.
    birth("salsa", 3, "_cmp_sal")
    _sal = json.load(open(os.path.join(SONGS, "_cmp_sal.json")))
    _slane = {t["name"]: t for t in _sal["tracks"]}
    _clv = _slane.get("clave")
    _slots = sorted({int(round((n["start"] % 8) * 4)) % 32
                     for n in _clv["notes"]}) if _clv else []
    check("dr28 salsa clave = son 3-2", _slots == [0, 6, 12, 20, 24], str(_slots))
    _sb = _slane.get("bass")
    check("dr28 tumbao never hits the downbeat",
          _sb is not None and all((n["start"] % 4) > 0.2 for n in _sb["notes"]))
    check("dr28 salsa carries no machine snare (abanico rides a high drum)",
          all((t.get("source") or {}).get("id") != "snare"
              for t in _sal["tracks"] if t["name"] == "snare"),
          str([(t["name"], t["source"].get("id")) for t in _sal["tracks"]
               if "snare" in str(t.get("source", {}).get("id"))]))
    birth("moombahton", 3, "_cmp_moo")
    _moo = json.load(open(os.path.join(SONGS, "_cmp_moo.json")))
    _msn = next(t for t in _moo["tracks"] if t["name"] == "snare")
    _mslots = sorted({int(round((n["start"] % 4) * 4))
                      for n in _msn["notes"] if n["start"] < 4})
    check("dr28 moombahton dembow = tresillo", _mslots == [3, 6, 11, 14], str(_mslots))
    birth("amapiano", 3, "_cmp_ama")
    _ama = json.load(open(os.path.join(SONGS, "_cmp_ama.json")))
    check("dr28 amapiano shaker carpet",
          any(t["name"] == "shaker" and len(t["notes"]) >= 24 for t in _ama["tracks"]))

    # ---- SWING & EXTENSIONS (dr27/dr08, 2026-07-12) ----
    # Kernel: `open` voicing once DISCARDED the 7th/9th; ~73 curated style
    # strings were dead words falling to smooth. And the bop family was
    # missing from its own seventh-law (blues with no dominant 7 isn't blues).
    import voicing as _vo
    _op = _vo.voice_pcs([[0, 4, 7, 10]], "open", 48, 76, thirds=[4], roots=[0])
    check("dr08 open voicing keeps the seventh", 10 in {p % 12 for p in _op[0]},
          str(_op[0]))
    check("dr08 dead style strings resolve (rootless->shell, tail->smooth)",
          _vo.resolve_style("rootless_chromatic") == "shell"
          and _vo.resolve_style("chug_powerchord") == "triad"
          and _vo.resolve_style("zzz_unknown") == "smooth")
    birth("bebop", 3, "_cmp_bop")
    _bop = json.load(open(os.path.join(SONGS, "_cmp_bop.json")))
    _bcol = next((t for t in _bop["tracks"] if t["name"].startswith("color")), None)
    check("dr27 bebop color carries the 7th (>=4 pcs)",
          _bcol is not None and len({n["pitch"] % 12 for n in _bcol["notes"]
                                     if n["start"] < 4}) >= 4)
    # dr27's "bop renders dead straight" REFUTED by measurement: the ride's
    # odd-8ths ride +0.119 beats off grid (the jazz_swing groove bakes the
    # feel at birth). Keep the receipt as a law: bebop must stay SWUNG.
    _ride = next((t for t in _bop["tracks"] if t["name"] == "ride"), None) or \
            next((t for t in _bop["tracks"] if t["name"] == "hat"), None)
    _offs = [n["start"] - round(n["start"] * 2) / 2 for n in (_ride or {}).get("notes", [])
             if abs(round(n["start"] * 2) % 2) == 1]
    check("dr27 bebop stays swung (odd-8ths ride late)",
          bool(_offs) and sum(_offs) / len(_offs) > 0.06,
          f"mean {sum(_offs)/len(_offs):+.3f}" if _offs else "no offbeats")

    # ---- THE DRUM TAKE (dr01-d, 2026-07-12): syncopated kicks differ by
    # seed (bounded, downbeat-anchored); four-on-floor identities are SACRED.
    def _kick_of(name):
        _d = json.load(open(os.path.join(SONGS, name + ".json")))
        _k = next(t for t in _d["tracks"] if t["name"] == "kick")
        return tuple(sorted(round(n["start"] * 4) for n in _k["notes"] if n["start"] < 4))
    birth("trap", 42, "_cmp_dt42"); birth("trap", 99, "_cmp_dt99")
    _tsets = {_kick_of("_cmp_trap"), _kick_of("_cmp_dt42"), _kick_of("_cmp_dt99")}
    check("dr01d trap kick takes vary by seed", len(_tsets) >= 2, str(_tsets))
    check("dr01d every take anchors the downbeat", all(0 in s for s in _tsets))
    birth("house", 42, "_cmp_dh42")
    check("dr01d four-on-floor kick SACRED across seeds",
          _kick_of("_cmp_house") == _kick_of("_cmp_dh42"))

    # ---- THE WOBBLE (dr29, 2026-07-12): dubstep bass rides the LFO voice,
    # tempo-synced (rate = bpm/60 * cycles-per-beat; measured 4.61 Hz vs
    # 4.63 commanded on the solo render). A static reese on dubstep was the
    # 'defining sound is a drone' crit.
    birth("dubstep", 3, "_cmp_wob")
    _wd = json.load(open(os.path.join(SONGS, "_cmp_wob.json")))
    _wb = next(t for t in _wd["tracks"] if t["name"] == "bass")
    _wrate = (_wb["source"].get("params") or {}).get("rate")
    check("dr29 dubstep bass = wobble, tempo-synced 1/8",
          _wb["source"]["id"] == "wobble"
          and _wrate == round(_wd["bpm"] / 60.0 * 2.0, 2),
          f"(rate {_wrate} @ {_wd['bpm']} bpm)")

    # ---- WORLD KIT 2 (wave 49, dr28): the cells are law.
    def _slots(tracks, lane, span=4.0, mod=16):
        tr = next((t for t in tracks if t["name"] == lane), None)
        return sorted({int(round(n["start"] * 4)) % mod
                       for n in (tr["notes"] if tr else []) if n["start"] < span})
    birth("cumbia", 3, "_cmp_cum")
    _cum = json.load(open(os.path.join(SONGS, "_cmp_cum.json")))["tracks"]
    check("wk2 cumbia llamador on the offbeats", _slots(_cum, "conga") == [2, 6, 10, 14],
          str(_slots(_cum, "conga")))
    check("wk2 cumbia carries no machine snare",
          all((t.get("source") or {}).get("id") != "snare"
              for t in _cum if t["name"] == "snare"))
    birth("samba", 3, "_cmp_sam")
    _sam = json.load(open(os.path.join(SONGS, "_cmp_sam.json")))["tracks"]
    _surdo = next((t for t in _sam if t["name"] == "conga"), None)
    check("wk2 samba surdo answers LOW on 2 and 4",
          _surdo is not None and _slots(_sam, "conga") == [4, 12]
          and all(n["pitch"] == 48 for n in _surdo["notes"]))
    birth("bossanova", 3, "_cmp_bsa")
    _bsa = json.load(open(os.path.join(SONGS, "_cmp_bsa.json")))["tracks"]
    check("wk2 bossa rim = the Jobim cell (steady, never breathes)",
          _slots(_bsa, "rim", span=7.9, mod=32) == [0, 6, 12, 22, 26],
          str(_slots(_bsa, "rim", span=7.9, mod=32)))
    birth("gqom", 3, "_cmp_gq")
    _gq = json.load(open(os.path.join(SONGS, "_cmp_gq.json")))["tracks"]
    _gh = next((t for t in _gq if t["name"] == "hat"), None)
    _pulls = [round((n["start"] * 4) % 1, 2) for n in (_gh["notes"] if _gh else [])]
    check("wk2 gqom hats ride the triplet pull (off the 16th grid)",
          bool(_pulls) and all(0.30 <= p <= 0.72 for p in _pulls),
          str(_pulls[:5]))

    # ---- THE CHOP TAKE (dr23, 2026-07-12): breaks-family snares re-chop per
    # bar; the 2&4 backbeat anchors stay sacred in EVERY bar.
    # ---- THE BREATH LAW (dr03 + the adlib court, 2026-07-12): a chattering
    # cell's phrase tail thins to anchor + one pickup (pure hook_notes case;
    # curated cells that already rest, like pop's, no-op by construction).
    import random as _rd
    _chatter = [[st, 1 + (st % 5), 1] for st in range(16)]      # wall-to-wall
    _bn = LG.hook_notes(_chatter, 1, [0, 2, 4, 5, 7, 9, 11], 0, 60,
                        lambda b: 1, 4, _rd.Random(7))
    _tail0 = [n for n in _bn if 3.0 <= n["start"] < 4.0]
    # the cell puts 4 events in the last beat; anchors (strong beat + the
    # cadence) are sacred, so the lawful floor is anchors + one pickup = 3
    check("dr03 breath law: a chattering cell's tail thins (< the cell's 4)",
          len(_tail0) < 4, f"({len(_tail0)} tail notes)")

    # ---- THE PRE-CHORUS (dr25, 2026-07-12): SONG_FORM's missing organ —
    # tension between verse and chorus, words repeated like a hook.
    _pcs = [s["name"] for s in go["sections"]]
    check("dr25 song form carries the pre-chorus (x2, third chorus straight off the bridge)",
          _pcs.count("prechorus") + _pcs.count("prechorus2") == 2
          and "prechorus3" not in _pcs, str(_pcs))
    def _mv(sp):
        vs = [n["vel"] for t in go["tracks"] for n in t.get("notes", [])
              if sp[0] <= n["start"] < sp[1]]
        return sum(vs) / len(vs) if vs else 0
    _vsp0, _pcsp = spans(go, "verse")[0], spans(go, "prechorus")[0]
    _chsp = spans(go, "chorus")[0]
    check("dr25 the tension tier: verse < prechorus < chorus",
          _mv(_vsp0) < _mv(_pcsp) < _mv(_chsp),
          f"({_mv(_vsp0):.2f} < {_mv(_pcsp):.2f} < {_mv(_chsp):.2f})")

    sh(["python3", "tools/loop_gen.py", "jungle", "_cmp_chop", "--bars", "8",
        "--seed", "3"])
    _ch = json.load(open(os.path.join(SONGS, "_cmp_chop.json")))
    _csn = next(t for t in _ch["tracks"] if t["name"] == "snare")
    _cfp = [tuple(sorted(round((n["start"] - b * 4) * 4) for n in _csn["notes"]
                         if b * 4 <= n["start"] < b * 4 + 4)) for b in range(6)]
    check("dr23 jungle snare re-chops (>=3 distinct bars of 6)",
          len(set(_cfp)) >= 3, str([list(p) for p in _cfp]))
    check("dr23 the 2&4 anchors are sacred in every bar",
          all(4 in p and 12 in p for p in _cfp if p))

    # ---- WAVE 43: THE RAP FORM + the fail-closed router (2026-07-12, dr24) ----
    # Rap arranged EDM club drops with risers; lofi got crash impacts; a torn
    # dna_cache silently handed EVERY genre the drop form. Laws: rap = verse/
    # hook over the FULL beat with zero EDM gestures; lofi = steady themes;
    # gestures gate on FAMILY not section name; cache failure fails CLOSED;
    # pop forms vary with the take seed.
    birth("trap", 3, "_cmp_rap")
    _rap = arr("_cmp_rap", "_cmp_rapa")
    _rl = [s["name"] for s in _rap["sections"]]
    _rt = [t.get("name") for t in _rap["tracks"]]
    check("wave43: rap is verse/hook, never a drop",
          any(s.startswith("verse") for s in _rl) and any(s.startswith("chorus") for s in _rl)
          and not any(s.rstrip("0123456789") in ("drop", "build") for s in _rl), str(_rl))
    check("wave43: rap ships ZERO EDM gestures",
          not any(n in _rt for n in ("riser", "revcrash", "crash")),
          str([n for n in _rt if n in ("riser", "revcrash", "crash")]))
    _secs43 = {s["name"]: s["startBar"] for s in _rap["sections"]}
    _kick43 = next((t for t in _rap["tracks"] if "kick" in t.get("name", "").lower()), None)
    if _kick43 and "verse" in _secs43 and "chorus" in _secs43:
        _vs, _cs = _secs43["verse"] * 4.0, _secs43["chorus"] * 4.0
        _vn = sum(1 for n in _kick43["notes"] if _vs <= n["start"] < _vs + 64.0) / 16.0
        _cn = sum(1 for n in _kick43["notes"] if _cs <= n["start"] < _cs + 32.0) / 8.0
        check("wave43: rap verse keeps the FULL beat", _vn >= 0.75 * _cn,
              f"kick/bar verse {_vn:.2f} vs chorus {_cn:.2f}")
    birth("lofi", 3, "_cmp_lof")
    _lof = arr("_cmp_lof", "_cmp_lofa")
    _ll = [s["name"] for s in _lof["sections"]]
    check("wave43: lofi is a steady loop (themes, no drop/chorus)",
          any(s.startswith("theme") for s in _ll)
          and not any(s.rstrip("0123456789") in ("drop", "build", "chorus") for s in _ll),
          str(_ll))
    check("wave43: lofi adds no crash/riser",
          not any(t.get("name") in ("riser", "revcrash", "crash") for t in _lof["tracks"]), "")
    birth("flamenco", 3, "_cmp_flm")
    sh([sys.executable, "tools/arrange.py", os.path.join(SONGS, "_cmp_flm.json"),
        "--out", "_cmp_flma", "--form", "intro:8,build:8,drop:16,outro:8",
        "--genre", "flamenco"])
    _flm = json.load(open(os.path.join(SONGS, "_cmp_flma.json")))
    check("wave43: gesture guard rides FAMILY, not the section name",
          not any(t.get("name") in ("riser", "revcrash", "crash") for t in _flm["tracks"]),
          str([t.get("name") for t in _flm["tracks"]][-3:]))
    import arrange as AR
    _bad = os.path.join(SONGS, "_cmp_badcache.json")
    open(_bad, "w").write('{"genres": {"trap": {"form_fam')     # torn mid-write
    _keep_dc = AR.DNA_CACHE
    AR.DNA_CACHE = _bad
    try:
        check("wave43: torn cache fails CLOSED", AR.form_family_for("trap") is None, "")
        AR.arrange(os.path.join(SONGS, "_cmp_rap.json"), "_cmp_fcl", genre="trap")
        _fcl = [s["name"] for s in
                json.load(open(os.path.join(SONGS, "_cmp_fcl.json")))["sections"]]
        check("wave43: torn-cache arrangement lands on the SONG form (no drop)",
              not any(s.rstrip("0123456789") == "drop" for s in _fcl), str(_fcl))
    finally:
        AR.DNA_CACHE = _keep_dc
    birth("pop", 3, "_cmp_pop")
    AR.arrange(os.path.join(SONGS, "_cmp_pop.json"), "_cmp_popa", genre="pop", seed=1)
    AR.arrange(os.path.join(SONGS, "_cmp_pop.json"), "_cmp_popb", genre="pop", seed=2)
    _pa = [s["name"] for s in json.load(open(os.path.join(SONGS, "_cmp_popa.json")))["sections"]]
    _pb = [s["name"] for s in json.load(open(os.path.join(SONGS, "_cmp_popb.json")))["sections"]]
    check("wave43: pop form varies with the take seed", _pa != _pb,
          f"{_pa[:6]} vs {_pb[:6]}")
    _sb = [s["startBar"] for s in
           json.load(open(os.path.join(SONGS, "_cmp_popa.json")))["sections"]]
    _dl = [b - a for a, b in zip(_sb, _sb[1:])]
    check("wave43: pop bars follow the grammar durations (not flat 8s)",
          len(set(_dl)) > 1, str(_dl))

    import glob
    for p in glob.glob(os.path.join(SONGS, "_cmp_*")):
        os.remove(p)
    print(f"composition battery: {'clean' if not fails else 'RED ' + str(fails[:4])}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
