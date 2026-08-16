#!/usr/bin/env python3
"""PARSE BATTERY — proof for agent/parse_lane.py (ZPE_TRANSFER_ROADMAP T1-R2).

Bars (§4.4 R2): **100%% precision** (a compiled plan that edits wrongly or leaks
scope = hard FAIL), honest coverage reporting (a miss on a target sentence is
reported, never hidden), compile median < 50ms.

Ground truth is borrowed, not re-invented: the 22 scalpel_suite.CASES verifiers
grade the parse lane's proposals exactly as they grade the real agent's — same
fixture song, same musical assertions — plus paraphrases mapped onto those same
verifiers, plus an adversarial set that MUST miss (the QTAG polarity: zero false
positives). Every executed plan must also come out scope-CLEAN under
surgical.scope_report from the receipts the plan itself filed.

Verb-compiling asks (color/intensify) run through the SAME subprocess rail the
sidecar verb bus uses (agent/verbs.py REGISTRY cli + receipt), against scratch
song `_parseb` under an isolated SOTADAW_IPC. Everything is scrubbed after.

Zero tokens, zero GPU, no sidecar. Exit 0 = all green.
"""
import copy, json, os, shutil, statistics, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPC = tempfile.mkdtemp(prefix="parse_ipc_")
os.environ["SOTADAW_IPC"] = IPC                      # receipts stay out of the live app
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import parse_lane, surgical, verbs                    # noqa: E402
from scalpel_suite import CASES, base_song, T, OTHERS, unchanged, in_win  # noqa: E402

SONGS = os.path.join(ROOT, "songs")
SCRATCH = "_parseb"
PY = os.path.join(ROOT, ".venv", "bin", "python")
if not os.path.exists(PY):
    PY = sys.executable

# The suite is a MOVING list (22 -> 50 on 2026-07-06, and growing): reference its
# verifiers BY SENTENCE, never by index, and claim coverage only over the set the
# v1 grammar ships. Every OTHER suite sentence still runs through compile() — a
# wrong compile anywhere is a precision failure; a miss outside the claim is the
# honest cloud-class, reported not failed.
SUITE = {ask: verify for ask, verify in CASES}

def suite_v(ask):
    if ask not in SUITE:
        raise SystemExit(f"suite no longer carries {ask!r} — update CLAIMED/paraphrases")
    return SUITE[ask]

CLAIMED = [
    "mute the hats", "make the kick 3 dB louder", "pan the pad a little to the left",
    "delete the snare in the intro", "transpose the lead up an octave in the drop only",
    "make the hats quieter in the verse only", "quantize the lead tight to the grid",
    "humanize the snare a bit", "shorten the bass notes, make them staccato",
    "the 3rd kick is late, fix it", "remove the pad from the outro",
    "add some reverb to the pad", "double the lead an octave up, quieter",
    "velocity ramp the hats rising through the verse into the drop",
    "delete every other hat in the drop", "pitch the last lead note up a third",
    "mute the bass and the pad", "make the pad warmer",
    "nudge the whole lead slightly later, about a 32nd",
    "strip the intro down to just kick and hats", "make the drop hit harder",
    "swing the hats a little",
    # -------- wave 2 (2026-07-07): grown from the CC4 suite's own evidence,
    # each verifier-pinned before implementation --------
    "delete the snare in the intro and the outro", "make the hats about half as loud",
    "make the lead twice as loud in the drop only",
    "mute the hats and pan the lead hard left",
    "make everything except the bass quieter by 3 db",
    "transpose everything down two semitones",
    "flatten the kick velocities, make it robotic",
    "widen the pad but keep the bass mono", "drop the bass an octave in the intro only",
    "accent every fourth hat", "delete everything after bar 12",
    "bump the tempo to 130", "add some swing to the groove",
    "delete the pad track entirely", "reverse the last four lead notes",
    # -------- wave 3 (routing + automation authoring + zone fill) --------
    "fade the pad in over the intro",
    "make the hats travel left to right across each bar",
    "give the lead some space with a send to a reverb bus",
    "double-time the hats in the bar before the drop",
    # -------- wave 4 (2026-07-07, THE TEN I1): source swap from the live
    # inventory — the suite's last standing grammar gap (case 'swap the lead
    # sound for an epiano' burned 124s on the cloud rail) --------
    "swap the lead sound for an epiano",
]


def run_verb(action, base):
    """Execute a verb action exactly like sidecar.handle_verb: registry cli
    subprocess against the scratch song + registry receipt -> coarse_receipt."""
    spec = verbs.REGISTRY[action["verb"]]
    path = os.path.join(SONGS, f"{SCRATCH}.json")
    json.dump(base, open(path, "w"), indent=1)
    surgical.clear_receipts()
    argv = [PY, os.path.join(ROOT, "tools", spec["tool"])] + \
        spec["cli"](SCRATCH, action["args"])
    cp = subprocess.run(argv, capture_output=True, text=True,
                        timeout=spec["timeout"])
    if cp.returncode != 0:
        raise RuntimeError(f"{action['verb']} rc={cp.returncode}: "
                           f"{(cp.stdout + cp.stderr)[-300:]}")
    tnames = [t.get("name") for t in base.get("tracks", [])]
    rcpt = spec["receipt"](action["args"], tnames, cp.stdout)
    surgical.coarse_receipt(SCRATCH, action["verb"], fields=rcpt.get("fields"),
                            track_wild=rcpt.get("track_wild"),
                            summary=f"verb bus: {action['verb']}")
    return json.load(open(path))


def execute(plan, base):
    """Plan -> (proposal_song, scope_report). Mirrors the R3 wiring."""
    if plan["verb"]:
        act = next(a for a in plan["actions"] if a["kind"] == "verb")
        prop = run_verb(act, copy.deepcopy(base))
    else:
        prop = copy.deepcopy(base)
        surgical.clear_receipts()
        parse_lane.apply_plan(prop, plan, song_name=SCRATCH)
    rep = surgical.scope_report(base, prop, surgical.read_receipts(SCRATCH))
    return prop, rep


# ---------------------------------------------------------------- fixtures
def keyless():
    s = base_song()
    s.pop("key", None)
    return s

def muted_hats():
    s = base_song()
    T(s, "hats")["muted"] = True
    return s


# ---------------------------------------------------------------- paraphrases
# (text, verify(base,prop), fixture_fn, facts) — verify reuses suite lambdas
# wherever the semantics are identical; customs mirror the suite's style.
PARAPHRASES = [
    ("MUTE THE HATS!!", suite_v("mute the hats"), None, None),
    ("mute the hats please", suite_v("mute the hats"), None, None),
    ("silence the pad",
     lambda b, p: T(p, "pad").get("muted") is True and unchanged(b, p, OTHERS("pad")),
     None, None),
    ("unmute the hats",
     lambda b, p: not T(p, "hats").get("muted") and unchanged(b, p, OTHERS("hats")),
     muted_hats, None),
    ("make the kick louder",
     lambda b, p: abs(T(p, "kick")["gainDb"] - (T(b, "kick")["gainDb"] + 3)) <= 0.75
     and unchanged(b, p, OTHERS("kick")), None, None),
    ("turn the bass down 2db",
     lambda b, p: abs(T(p, "bass")["gainDb"] - (T(b, "bass")["gainDb"] - 2)) <= 0.5
     and unchanged(b, p, OTHERS("bass")), None, None),
    ("raise the kick 3db", suite_v("make the kick 3 dB louder"), None, None),
    ("lower the hats 2db",
     lambda b, p: abs(T(p, "hats")["gainDb"] - (T(b, "hats")["gainDb"] - 2)) <= 0.5
     and unchanged(b, p, OTHERS("hats")), None, None),
    ("make the hats quieter in the verse", suite_v("make the hats quieter in the verse only"), None, None),
    ("make the hats 3db quieter in the verse only", suite_v("make the hats quieter in the verse only"), None, None),
    ("remove the snare during the intro", suite_v("delete the snare in the intro"), None, None),
    ("kill the pad in the outro", suite_v("remove the pad from the outro"), None, None),
    ("delete the snare in the drop",
     lambda b, p: not [n for n in T(p, "snare")["notes"] if in_win(n, 32, 48)]
     and len([n for n in T(p, "snare")["notes"] if not in_win(n, 32, 48)])
     == len([n for n in T(b, "snare")["notes"] if not in_win(n, 32, 48)])
     and unchanged(b, p, OTHERS("snare")), None, None),
    ("transpose the lead up an octave in the drop", suite_v("transpose the lead up an octave in the drop only"), None, None),
    ("transpose the lead down an octave",
     lambda b, p: len(T(p, "lead")["notes"]) == len(T(b, "lead")["notes"])
     and all(any(abs(m["start"] - n["start"]) < 0.02 and m["pitch"] == n["pitch"] - 12
                 for m in T(p, "lead")["notes"]) for n in T(b, "lead")["notes"])
     and unchanged(b, p, OTHERS("lead")), None, None),
    ("shift the lead up 2 semitones in the verse only",
     lambda b, p: all(any(abs(m["start"] - n["start"]) < 0.02
                          and m["pitch"] == n["pitch"] + (2 if in_win(n, 16, 32) else 0)
                          for m in T(p, "lead")["notes"]) for n in T(b, "lead")["notes"])
     and unchanged(b, p, OTHERS("lead")), None, None),
    ("quantize the lead", suite_v("quantize the lead tight to the grid"), None, None),
    ("humanize the snare", suite_v("humanize the snare a bit"), None, None),
    ("make the bass staccato", suite_v("shorten the bass notes, make them staccato"), None, None),
    ("the 3rd kick is late fix it", suite_v("the 3rd kick is late, fix it"), None, None),
    ("nudge the lead later", suite_v("nudge the whole lead slightly later, about a 32nd"), None, None),
    ("push the lead a bit later", suite_v("nudge the whole lead slightly later, about a 32nd"), None, None),
    ("pan the pad left", suite_v("pan the pad a little to the left"), None, None),
    ("put a little delay on the lead",
     lambda b, p: any(f.get("id") == "fx_delay" for f in T(p, "lead").get("fx", []))
     and unchanged(b, p, OTHERS("lead")), None, None),
    ("make the pad wider",
     lambda b, p: any(f.get("id") == "fx_widen" for f in T(p, "pad").get("fx", []))
     and unchanged(b, p, OTHERS("pad")), None, None),
    ("make the drop harder", suite_v("make the drop hit harder"), None, None),
    ("swing the hats", suite_v("swing the hats a little"), None, None),
    ("double the lead an octave up",
     lambda b, p: len(T(p, "lead")["notes"]) == 2 * len(T(b, "lead")["notes"])
     and all(any(abs(m["start"] - n["start"]) < 0.03 and m["pitch"] == n["pitch"] + 12
                 and m["vel"] < n["vel"] for m in T(p, "lead")["notes"])
             for n in T(b, "lead")["notes"])
     and unchanged(b, p, OTHERS("lead")), None, None),
    ("make the squelchy one 3db louder",
     lambda b, p: abs(T(p, "bass")["gainDb"] - (T(b, "bass")["gainDb"] + 3)) <= 0.5
     and unchanged(b, p, OTHERS("bass")), None, {"squelchy one": "bass"}),
    # -------- wave 2 paraphrases --------
    ("set the bpm to 128",
     lambda b, p: abs(float(p.get("bpm", 0)) - 128.0) < 0.5, None, None),
    ("drop the lead an octave",
     lambda b, p: len(T(p, "lead")["notes"]) == len(T(b, "lead")["notes"])
     and all(any(abs(m["start"] - n["start"]) < 0.02 and m["pitch"] == n["pitch"] - 12
                 for m in T(p, "lead")["notes"]) for n in T(b, "lead")["notes"])
     and unchanged(b, p, OTHERS("lead")), None, None),
    ("remove the pad track", suite_v("delete the pad track entirely"), None, None),
    ("mute the hats and the pad and pan the lead hard left",
     lambda b, p: T(p, "hats").get("muted") is True and T(p, "pad").get("muted") is True
     and float(T(p, "lead").get("pan", 0)) <= -0.7
     and unchanged(b, p, OTHERS("hats", "pad", "lead")), None, None),
    ("flatten the snare velocities",
     lambda b, p: len({round(n["vel"], 3) for n in T(p, "snare")["notes"]}) == 1
     and len(T(p, "snare")["notes"]) == len(T(b, "snare")["notes"])
     and unchanged(b, p, OTHERS("snare")), None, None),
    ("make the kick twice as loud",
     lambda b, p: abs(T(p, "kick")["gainDb"] - (T(b, "kick")["gainDb"] + 6)) <= 0.75
     and unchanged(b, p, OTHERS("kick")), None, None),
    ("add a reverb send to the lead",
     suite_v("give the lead some space with a send to a reverb bus"), None, None),
    ("double time the hats in the bar before the drop",
     suite_v("double-time the hats in the bar before the drop"), None, None),
    ("fade the bass in over the intro",
     lambda b, p: any("gain" in str(a.get("target", "")).lower()
                      and len(a.get("points", [])) >= 2
                      and a["points"][0]["v"] < a["points"][-1]["v"] - 6
                      for a in T(p, "bass").get("automation", []))
     and unchanged(b, p, OTHERS("bass")), None, None),
    # -------- wave 4 paraphrases (source swap) --------
    ("change the lead to a rhodes", suite_v("swap the lead sound for an epiano"), None, None),
    ("replace the lead sound with a jazz piano",
     lambda b, p: T(p, "lead").get("source", {}).get("id") == "jazz_piano"
     and sorted((round(n["start"], 3), n["pitch"]) for n in T(p, "lead")["notes"])
     == sorted((round(n["start"], 3), n["pitch"]) for n in T(b, "lead")["notes"])
     and unchanged(b, p, OTHERS("lead")), None, None),
    ("switch the pad to strings",
     lambda b, p: T(p, "pad").get("source", {}).get("kit") == "strings"
     and T(p, "pad").get("source", {}).get("kind") == "sample"
     and unchanged(b, p, OTHERS("pad")), None, None),
]

# ---------------------------------------------------------------- must-miss
# (text, fixture_fn) — ANY compile here is a precision violation.
ADVERSARIAL = [
    ("make it groove more", None),
    ("fix the mix", None),
    ("mute the hats in the verse", None),          # scoped mute = ambiguous -> cloud
    ("make the kick louder in the mix", None),     # 'mix' is not a section
    ("delete the guitar in the intro", None),      # no such track
    ("make the vocals warmer", None),
    ("delete the snare", None),                    # notes or the whole track? -> cloud
    ("delete the snare in bars 5-8", None),        # bar indexing deferred (off-by-one trap)
    ("transpose the lead up a third in the drop", None),   # span diatonic = v2
    ("transpose the lead up a fifth", None),       # chromatic-vs-diatonic ambiguity
    ("double the lead", None),                     # no interval given
    ("add some chorus to the pad", None),          # no fx_chorus in the rack
    ("add reverb", None),                          # no target
    ("add some width to the bass", None),          # mono-below-120 law
    ("quantize the hats", None),                   # already on-grid -> no_op honesty
    ("the 99th kick is late, fix it", None),       # nth out of range
    ("speed it up", None),
    ("make the verse longer", None),
    ("what did we change in the hook?", None),     # questions never compile
    ("", None),
    ("swing the guitar a little", None),
    ("mute the bass and the guitar", None),        # all-or-nothing track lists
    ("pitch the last lead note up a third", keyless),      # diatonic needs song.key
    ("make the squelchy one 3db louder", None),    # alias only via T2 facts
    ("strip the intro down to just kick and hats and snare and bass and lead and pad",
     None),                                        # nothing left to strip
    # -------- wave 2 adversarial --------
    ("reverse the last 99 lead notes", None),      # only 32 notes exist
    ("bump the tempo to 999", None),               # bpm range guard
    ("delete everything after bar 99", None),      # beyond the song
    ("widen the bass", None),                      # mono-below-120 law
    ("delete the drums track", None),              # no such track
    ("transpose the lead an octave", None),        # no direction (drop implies, transpose doesn't)
    ("make everything except the bass and the pad quieter by 3db", None),  # multi-except = v2
    ("mute the hats and make it groove", None),    # compound: unprovable right clause
    ("fade the pad in", None),                     # over WHAT? needs a span
    ("double time the hats", None),                # no zone given
    ("give the lead some space", None),            # bare idiom: space could mean EQ/pan
    # -------- wave 4 adversarial (source swap precision) --------
    ("swap the lead for the pad", None),           # 'pad' is a TRACK: swap-vs-route ambiguity
    ("change the lead to a guitar", None),         # 4 guitars in the rack -> which?
    ("swap the lead sound for an organ", None),    # hammond_organ|organ_soul -> which?
    ("swap the lead for a vocoder", None),         # no such voice anywhere
]


def main():
    fails, rows = [], []

    def grade(tag, text, verify, fixture_fn=None, facts=None, context=None):
        base = (fixture_fn or base_song)()
        plan, why = parse_lane.compile_debug(text, base, context, facts=facts)
        if plan is None:
            rows.append((tag, text, "MISS", why))
            return None
        try:
            prop, rep = execute(plan, base)
            ok = bool(verify(base, prop))
            clean = bool(rep.get("clean")) and not rep.get("empty")
        except Exception as e:
            ok, clean = False, False
            why = f"execute crashed: {e}"
        detail = plan["summary"]
        if not ok or not clean:
            fails.append(f"{tag} PRECISION: {text!r} -> {detail} "
                         f"(ok={ok} clean={clean}) {why}")
            rows.append((tag, text, "WRONG", detail))
        else:
            rows.append((tag, text, "HIT", f"{plan['ms']}ms {detail}"))
        return plan

    print(f"== A. the full scalpel suite ({len(CASES)} sentences; claimed class = "
          f"{len(CLAIMED)}) ==")
    claimed_hit, bonus_hit, cloud_class = 0, 0, 0
    for i, (ask, verify) in enumerate(CASES):
        plan = grade(f"suite#{i:02d}", ask, verify)
        st, det = rows[-1][2], rows[-1][3]
        claimed = ask in CLAIMED
        if plan is not None:
            claimed_hit += 1 if claimed else 0
            bonus_hit += 0 if claimed else 1
        elif claimed:
            fails.append(f"COVERAGE: suite#{i:02d} {ask!r} missed ({det})")
        else:
            cloud_class += 1
            st = "CLOUD"                       # honest miss outside the claim
        print(f"  [{st:5s}] #{i:02d} {ask!r}" + (f" — {det}" if det else ""))
    print(f"  -> claimed {claimed_hit}/{len(CLAIMED)} compiled+verified, "
          f"{bonus_hit} bonus hits, {cloud_class} cloud-class honest misses")

    print("\n== B. paraphrases (same graders, new words) ==")
    for text, verify, fx, facts in PARAPHRASES:
        grade("para", text, verify, fx, facts)
        st, det = rows[-1][2], rows[-1][3]
        print(f"  [{st:5s}] {text!r}" + (f" — {det}" if det else ""))
        if st == "MISS":
            fails.append(f"COVERAGE: paraphrase {text!r} missed ({det})")

    print("\n== C. adversarial — every one of these MUST miss ==")
    for text, fx in ADVERSARIAL:
        base = (fx or base_song)()
        plan, why = parse_lane.compile_debug(text, base)
        if plan is None:
            print(f"  [MISS ] {text!r} ({why})")
        else:
            print(f"  [LEAK!] {text!r} -> {plan['summary']}")
            fails.append(f"FALSE POSITIVE: {text!r} compiled to {plan['summary']}")

    # -------- wave 5 (2026-08-08): SELECTION = CONTEXT + the whole-mix fader.
    # Live evidence: 'make it quieter' x3 / 'make it darker' missed as
    # track_empty:it while the UI was pointing at a track; 'make everything
    # louder' (old adversarial) now has DEFINED semantics — one uniform trim on
    # every track, balance kept. Pronouns without a selection stay honest
    # misses except pure gain, where 'it' = the mix fader.
    print("\n== E. selection rung — pronouns point, idioms scope ==")
    sel_of = lambda *names: {"selections": [{"type": "tracks", "names": list(names)}]}
    notes_sel = {"selections": [{"type": "notes", "track": "hats", "indices": [0, 1, 2]}]}

    def all_gain(delta):
        def v(b, p):
            return (all(abs(float(T(p, t["name"]).get("gainDb", 0))
                            - (float(T(b, t["name"]).get("gainDb", 0)) + delta)) <= 0.5
                        for t in b["tracks"])
                    and all(len(T(p, t["name"]).get("notes", []))
                            == len(T(b, t["name"]).get("notes", []))
                            for t in b["tracks"]))
        return v

    SELECTED = [
        ("make it quieter", sel_of("hats"),
         lambda b, p: abs(T(p, "hats")["gainDb"] - (T(b, "hats")["gainDb"] - 3)) <= 0.5
         and unchanged(b, p, OTHERS("hats"))),
        ("make it quieter", notes_sel,        # a notes selection names its track
         lambda b, p: abs(T(p, "hats")["gainDb"] - (T(b, "hats")["gainDb"] - 3)) <= 0.5
         and unchanged(b, p, OTHERS("hats"))),
        ("turn it down 2db", sel_of("kick"),
         lambda b, p: abs(T(p, "kick")["gainDb"] - (T(b, "kick")["gainDb"] - 2)) <= 0.5
         and unchanged(b, p, OTHERS("kick"))),
        ("mute it", sel_of("pad"),
         lambda b, p: T(p, "pad").get("muted") is True
         and unchanged(b, p, OTHERS("pad"))),
        ("pan it hard left", sel_of("lead"),
         lambda b, p: float(T(p, "lead").get("pan", 0)) <= -0.7
         and unchanged(b, p, OTHERS("lead"))),
        ("make it darker", sel_of("pad"),     # verb bus, scoped to the selection
         lambda b, p: p != b and unchanged(b, p, OTHERS("pad"))),
        ("quantize it", sel_of("lead"), suite_v("quantize the lead tight to the grid")),
        ("make it quieter", None, all_gain(-3)),   # nothing selected = the mix fader
        ("make everything louder", None, all_gain(3)),
        ("make everything quieter by 3db", None, all_gain(-3)),
        ("mute everything", None,
         lambda b, p: all(T(p, t["name"]).get("muted") is True for t in b["tracks"])),
    ]
    for text, sctx, verify in SELECTED:
        grade("sel", text, verify, None, None, sctx)
        st, det = rows[-1][2], rows[-1][3]
        print(f"  [{st:5s}] {text!r} ctx={'sel' if sctx else 'none'} — {det}")
        if st == "MISS":
            fails.append(f"COVERAGE: selection-rung {text!r} missed ({det})")
    MUST_MISS_SEL = [
        ("make it quieter", sel_of("hats", "pad"), "pronoun_multi_selection"),
        ("make it darker", None, "pronoun_no_selection"),   # taste stays cloud
        ("mute it", None, "pronoun_no_selection"),
        ("pan it left", None, "pronoun_no_selection"),
        ("quantize it", None, "pronoun_no_selection"),
    ]
    for text, sctx, want in MUST_MISS_SEL:
        plan, why = parse_lane.compile_debug(text, base_song(), sctx)
        if plan is not None:
            print(f"  [LEAK!] {text!r} -> {plan['summary']}")
            fails.append(f"FALSE POSITIVE (selection rung): {text!r} -> {plan['summary']}")
        elif want not in why:
            print(f"  [MISS ] {text!r} ({why}) — WRONG REASON, wanted {want}")
            fails.append(f"WRONG MISS REASON: {text!r} -> {why} (wanted {want})")
        else:
            print(f"  [MISS ] {text!r} ({why})")

    print("\n== D. compile speed ==")
    texts = [c[0] for c in CASES] + [p[0] for p in PARAPHRASES]
    base = base_song()
    tms = []
    for _ in range(3):
        for t in texts:
            t0 = time.time()
            parse_lane.compile_debug(t, base)
            tms.append((time.time() - t0) * 1000.0)
    med, mx = statistics.median(tms), max(tms)
    print(f"  {len(tms)} compiles: median {med:.2f}ms, max {mx:.2f}ms")
    if med >= 50:
        fails.append(f"SPEED: compile median {med:.1f}ms >= 50ms bar")

    n_para = sum(1 for r in rows if r[0] == "para" and r[2] == "HIT")
    print(f"\n== PARSE BATTERY: claimed {claimed_hit}/{len(CLAIMED)} of the "
          f"{len(CASES)}-case suite (+{cloud_class} cloud-class honest) | "
          f"paraphrases {n_para}/{len(PARAPHRASES)} | "
          f"adversarial {sum(1 for _ in ADVERSARIAL)} probed | "
          f"precision {'100%' if not any('PRECISION' in f or 'FALSE' in f for f in fails) else 'BROKEN'} | "
          f"median {med:.1f}ms ==")
    if fails:
        print(f"\n{len(fails)} FAILURE(S):")
        for f in fails:
            print("  - " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        for f in os.listdir(SONGS):
            if f.startswith(SCRATCH) or f.startswith(f"_prop_{SCRATCH}"):
                os.remove(os.path.join(SONGS, f))
        shutil.rmtree(IPC, ignore_errors=True)
    sys.exit(rc)
