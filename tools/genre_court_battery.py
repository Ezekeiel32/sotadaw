#!/usr/bin/env python3
"""THE GENRE COURT battery (Chezy law 2026-07-14: "the agent must select the
genre from the REQUEST unless ambiguous — and the selector must follow the
agent's selection automatically").

Proves the pure kernels + the event seam, isolated (SOTADAW_IPC = tmpdir):
  A. ask_genre         — the ask's own words resolve literally (word / phrase /
                         joined-bigram forms), scoped edits resolve to nothing
  B. genre_pref_block  — the dock enters the prompt as a FALLBACK law only:
                         user PIN vs agent ECHO wording, ask always outranks
  C. relay_genre       — one 'genre' event per distinct pick per run, dedup,
                         last_genres memo (attribution + loudness truth)
  D. relay_genre_stamp — daw_mcp's session stamp relays fresh, never stale
  E. t_start_session   — stamps ipc/genre_resolved.json with the genre the
                         session actually resolved

Usage: python3 tools/genre_court_battery.py
"""
import json, os, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPC = tempfile.mkdtemp(prefix="genre_court_ipc_")
os.environ["SOTADAW_IPC"] = IPC
sys.path.insert(0, os.path.join(ROOT, "agent"))
import sidecar as sc  # noqa: E402

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def events():
    p = os.path.join(IPC, "events.jsonl")
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p) if l.strip()]

# ---- A. ask_genre: the request owns the genre -------------------------------
cache = set(sc.dna_genres())
ok(len(cache) > 50, f"dna genre cache loaded ({len(cache)})")
ok(sc.ask_genre("make a dark trap beat in F minor at 142") == "trap",
   "literal word resolves (trap)")
ok(sc.ask_genre("make the hats quieter in the drop") == "",
   "scoped edit resolves to NOTHING (no phantom genre)")
if "acid_house" in cache:
    ok(sc.ask_genre("a warm acid house groove") == "acid_house",
       "longest match outranks its suffix (acid house != house)")
if "ukgarage" in cache:
    ok(sc.ask_genre("uk garage vibes with shuffled hats") == "ukgarage",
       "joined bigram resolves (uk garage -> ukgarage)")
ok(sc.ask_genre("") == "" and sc.ask_genre(None) == "", "empty/None safe")

# ---- B. genre_pref_block: the dock is a fallback, never a command -----------
b_user = sc.genre_pref_block("trap", "user")
b_echo = sc.genre_pref_block("trap", "agent")
b_old  = sc.genre_pref_block("trap", "")     # un-rebuilt UI sends no genre_src
ok(b_user.count("GENRE LAW") == 1 and "dock pin 'trap'" in b_user
   and "ONLY when" in b_user, "user PIN wording")
ok("resolve the genre from THE ASK" in b_user and
   "resolve the genre from THE ASK" in b_echo,
   "both flavors put the ASK first")
ok("NOT a user choice" in b_echo and "echoes 'trap'" in b_echo,
   "agent ECHO wording (weaker)")
ok(b_old == sc.genre_pref_block("trap", "AGENT".lower()) or "echoes" in b_old,
   "missing genre_src reads as echo, never as a command")
ok(sc.genre_pref_block("", "user") == "" and sc.genre_pref_block(None, "x") == "",
   "empty pref rides nothing")

# ---- C. relay_genre: one event per distinct pick, memo lands ----------------
n0 = len(events())
sc.relay_genre("rid_A", "songX", "Trap!", "ask")
ev = events()
ok(len(ev) == n0 + 1, "relay emits one event")
ok(ev and ev[-1].get("kind") == "genre" and ev[-1].get("genre") == "trap"
   and ev[-1].get("song") == "songX" and ev[-1].get("source") == "ask",
   "event shape: kind/genre(sanitized)/song/source")
ok(sc.last_genres.get("songX") == "trap", "attribution memo lands")
sc.relay_genre("rid_A", "songX", "trap", "vibe")
ok(len(events()) == n0 + 1, "same pick same run dedupes")
sc.relay_genre("rid_A", "songX", "dnb", "session")
ok(len(events()) == n0 + 2 and events()[-1]["genre"] == "dnb",
   "a DIFFERENT pick same run re-emits (agent refined)")
sc.relay_genre("rid_B", "songX", "", "ask")
ok(len(events()) == n0 + 2, "empty genre never emits")

# ---- D. relay_genre_stamp: fresh speaks, stale never ------------------------
stamp = os.path.join(IPC, "genre_resolved.json")
json.dump({"genre": "phonk", "source": "session", "t": time.time()},
          open(stamp, "w"))
n1 = len(events())
sc.relay_genre_stamp("rid_C", "songY", time.time() + 60)   # stamp older than run
ok(len(events()) == n1, "stale stamp (pre-run) never speaks")
sc.relay_genre_stamp("rid_C", "songY", time.time() - 60)   # fresh stamp
ev = events()
ok(len(ev) == n1 + 1 and ev[-1]["genre"] == "phonk"
   and ev[-1]["source"] == "session" and ev[-1]["song"] == "songY",
   "fresh stamp relays")
sc.relay_genre_stamp("rid_C", "songY", time.time() - 60)
ok(len(events()) == n1 + 1, "stamp relay dedupes per run")
open(stamp, "w").write("{torn")
sc.relay_genre_stamp("rid_D", "songY", 0)
ok(len(events()) == n1 + 1, "torn stamp never raises, never emits")
os.remove(stamp)

# ---- E. t_start_session stamps what it resolved -----------------------------
import daw_mcp as D  # noqa: E402
out = D.t_start_session({"genre": "trap"})
ok("Session start" in out, "start_session serves")
ok(os.path.exists(stamp), "session stamped genre_resolved.json")
try:
    d = json.load(open(stamp))
except Exception:
    d = {}
ok(d.get("genre") == "trap" and d.get("source") == "session"
   and d.get("asked") == "trap", f"stamp truth (got {d.get('genre')!r})")

print(f"genre_court_battery: {PASS} passed, {len(FAIL)} failed")
for f in FAIL:
    print("  FAIL:", f)
sys.exit(1 if FAIL else 0)
