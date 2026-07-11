#!/usr/bin/env python3
"""BRIDGE MODE alpha: drive a RUNNING REAPER from the agent (NIGGUN §11.3 wedge).

MCP stdio server speaking REAPER's built-in web-RC protocol (Options →
Preferences → Control/OSC/web → "Web browser interface", default port 8080):
  GET http://host:port/_/CMD;CMD2   → tab-separated record lines.
Zero dependencies (urllib). Enable in agent/connectors.json; point REAPER_RC
at the interface (default http://127.0.0.1:8080).

Verified against a protocol mock (tools- and parse-level); live REAPER
verification pending a user-side run with the web interface enabled.
"""
import json, os, sys, urllib.request

RC = os.environ.get("REAPER_RC", "http://127.0.0.1:8080").rstrip("/")
PLAYSTATE = {0: "stopped", 1: "playing", 2: "paused", 5: "recording", 6: "record-paused"}
ACTIONS = {"play": 1007, "stop": 1016, "pause": 1008, "record": 1013, "toggle": 40044}


def rc(cmds):
    """One web-RC round-trip; cmds like 'TRANSPORT;TRACK'. Returns raw text."""
    with urllib.request.urlopen(f"{RC}/_/{cmds}", timeout=4) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_status(raw):
    out = {"tracks": []}
    for line in raw.splitlines():
        f = line.split("\t")
        if f[0] == "TRANSPORT" and len(f) >= 5:
            out["transport"] = {"state": PLAYSTATE.get(int(float(f[1])), f[1]),
                                "position_seconds": float(f[2]),
                                "repeat": f[3] == "1", "position": f[4],
                                "beats": f[5] if len(f) > 5 else ""}
        elif f[0] == "TRACK" and len(f) >= 7 and f[1].isdigit():
            flags = int(f[3])
            out["tracks"].append({"index": int(f[1]), "name": f[2],
                                  "volume_db": round(20 * __import__("math").log10(max(1e-6, float(f[4]))), 2),
                                  "pan": float(f[5]),
                                  "muted": bool(flags & 8), "soloed": bool(flags & 16),
                                  "rec_armed": bool(flags & 64), "selected": bool(flags & 2)})
    return out


def t_status(_a):
    return json.dumps(parse_status(rc("TRANSPORT;TRACK")), indent=1)


def t_transport(a):
    act = str(a.get("action", "toggle")).lower()
    if act == "locate":
        rc(f"SETPOS/{float(a.get('seconds', 0.0))}")
        return f"located to {a.get('seconds', 0)}s"
    if act not in ACTIONS:
        return f"unknown action '{act}' (play/stop/pause/record/toggle/locate)"
    rc(str(ACTIONS[act]))
    return f"transport: {act}"


def t_track(a):
    i = int(a.get("track", 1))
    done = []
    if a.get("volume_db") is not None:
        rc(f"SETTRACKVOL/{i}/{10 ** (float(a['volume_db']) / 20.0):.6f}")
        done.append(f"vol {a['volume_db']}dB")
    if a.get("pan") is not None:
        rc(f"SETTRACKPAN/{i}/{max(-1.0, min(1.0, float(a['pan'])))}")
        done.append(f"pan {a['pan']}")
    if a.get("mute") is not None:
        rc(f"SETTRACKMUTE/{i}/{1 if a['mute'] else 0}")
        done.append("mute" if a["mute"] else "unmute")
    if a.get("solo") is not None:
        rc(f"SETTRACKSOLO/{i}/{1 if a['solo'] else 0}")
        done.append("solo" if a["solo"] else "unsolo")
    return f"track {i}: " + (", ".join(done) if done else "nothing to do")


def t_action(a):
    cid = str(a.get("command", "")).strip()
    if not cid:
        return "need a command id (e.g. 40157 = insert marker; named _RS... ReaScript ids work too)"
    rc(cid)
    return f"action {cid} sent"


TOOLS = {
    "reaper_status": (t_status, "Transport state + all tracks (name, vol dB, pan, mute/solo/arm) of the RUNNING REAPER",
                      {"type": "object", "properties": {}}),
    "reaper_transport": (t_transport, "Drive REAPER's transport: play|stop|pause|record|toggle|locate(seconds)",
                         {"type": "object", "properties": {"action": {"type": "string"},
                                                           "seconds": {"type": "number"}}}),
    "reaper_track": (t_track, "Set a REAPER track's volume_db/pan/mute/solo (1-based track index)",
                     {"type": "object", "properties": {"track": {"type": "integer"},
                                                       "volume_db": {"type": "number"},
                                                       "pan": {"type": "number"},
                                                       "mute": {"type": "boolean"},
                                                       "solo": {"type": "boolean"}},
                      "required": ["track"]}),
    "reaper_action": (t_action, "Trigger ANY REAPER action by command id (or named _RS ReaScript id)",
                      {"type": "object", "properties": {"command": {"type": "string"}},
                       "required": ["command"]}),
}


def reply(id_, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": id_, "result": result}) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        m, id_ = req.get("method", ""), req.get("id")
        if m == "initialize":
            reply(id_, {"protocolVersion": req["params"].get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "reaper", "version": "0.1"}})
        elif m == "notifications/initialized":
            continue
        elif m == "tools/list":
            reply(id_, {"tools": [{"name": n, "description": d, "inputSchema": sch}
                                  for n, (f, d, sch) in TOOLS.items()]})
        elif m == "tools/call":
            name = req["params"]["name"]
            args = req["params"].get("arguments") or {}
            try:
                text = TOOLS[name][0](args) if name in TOOLS else f"unknown tool {name}"
                err = False
            except Exception as e:
                text, err = f"REAPER unreachable at {RC} — is the Web browser interface on? ({e})", True
            reply(id_, {"content": [{"type": "text", "text": text}], "isError": err})
        elif id_ is not None:
            reply(id_, {})


if __name__ == "__main__":
    main()
