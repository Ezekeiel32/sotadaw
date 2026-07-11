#!/usr/bin/env python3
"""SoundCloud connector — publish from the DAW (SPEC connectivity T3).

MCP stdio server. OAuth 2.1 + PKCE (SoundCloud opened self-serve app registration
2026-05 for Artist Pro): sc_connect runs the one-click browser flow against a
loopback listener; tokens auto-refresh (refresh tokens are single-use — always
persist the rotated pair). Uploads default to PRIVATE — publishing to the world
is the human's click (sharing="public" only on an explicit user ask).

Setup (once): create the app at https://developers.soundcloud.com (Artist Pro),
register redirect URI http://127.0.0.1:8899/callback, then put
  {"client_id": "...", "client_secret": "..."}
in agent/.soundcloud.json (gitignored). Then ask the agent to connect.
"""
import base64, hashlib, json, os, secrets, sys, threading, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRED = os.path.join(ROOT, "agent", ".soundcloud.json")
TOK = os.path.join(ROOT, "agent", ".soundcloud_token.json")
AUTH_URL = "https://secure.soundcloud.com/authorize"
TOKEN_URL = "https://secure.soundcloud.com/oauth/token"
API = "https://api.soundcloud.com"
REDIRECT = "http://127.0.0.1:8899/callback"


def creds():
    return json.load(open(CRED)) if os.path.exists(CRED) else None


def token():
    return json.load(open(TOK)) if os.path.exists(TOK) else None


def save_token(t):
    t["saved_at"] = time.time()
    with open(TOK, "w") as f:
        json.dump(t, f)
    os.chmod(TOK, 0o600)


def token_request(form):
    data = urllib.parse.urlencode(form).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def refresh():
    c, t = creds(), token()
    if not (c and t and t.get("refresh_token")):
        return None
    try:
        nt = token_request({"grant_type": "refresh_token", "refresh_token": t["refresh_token"],
                            "client_id": c["client_id"], "client_secret": c["client_secret"]})
        save_token(nt)
        return nt
    except Exception:
        return None


def api(method, path, data=None, headers=None, retry=True):
    t = token()
    if not t:
        raise RuntimeError("not connected — run sc_connect first")
    h = {"Authorization": f"OAuth {t['access_token']}", "Accept": "application/json"}
    h.update(headers or {})
    req = urllib.request.Request(API + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            body = r.read()
            return json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry and refresh():
            return api(method, path, data=data, headers=headers, retry=False)
        raise RuntimeError(f"SoundCloud API {e.code}: {e.read()[:300].decode(errors='replace')}")


def multipart(fields, files):
    """fields: {name: str}; files: {name: (filename, bytes, mime)} -> (body, content_type)"""
    bound = "----sotadaw" + secrets.token_hex(12)
    out = []
    for k, v in fields.items():
        out.append(f"--{bound}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    for k, (fn, blob, mime) in files.items():
        out.append(f"--{bound}\r\nContent-Disposition: form-data; name=\"{k}\"; "
                   f"filename=\"{fn}\"\r\nContent-Type: {mime}\r\n\r\n".encode() + blob + b"\r\n")
    out.append(f"--{bound}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={bound}"


# ---------------- tools ----------------

def t_sc_setup_status(_):
    c, t = creds(), token()
    lines = []
    if not c:
        return ("NOT CONFIGURED. One-time setup: 1) SoundCloud Artist Pro account; "
                "2) register an app at https://developers.soundcloud.com (self-serve since 2026-05); "
                f"3) add redirect URI {REDIRECT} in the app settings; "
                "4) write agent/.soundcloud.json with {\"client_id\":..., \"client_secret\":...}. "
                "Then call sc_connect.")
    lines.append(f"app credentials: OK (client_id ...{c['client_id'][-6:]})")
    if not t:
        lines.append("token: none — call sc_connect (opens the browser for a one-click OAuth).")
        return "\n".join(lines)
    try:
        me = api("GET", "/me")
        lines.append(f"connected as: {me.get('username')} ({me.get('permalink_url')}) — "
                     f"followers {me.get('followers_count', '?')}")
    except Exception as e:
        lines.append(f"token present but not working ({e}) — call sc_connect to re-auth.")
    return "\n".join(lines)


def t_sc_connect(args):
    c = creds()
    if not c:
        return t_sc_setup_status({})
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    q = urllib.parse.urlencode({"client_id": c["client_id"], "redirect_uri": REDIRECT,
                                "response_type": "code", "code_challenge": challenge,
                                "code_challenge_method": "S256", "state": state})
    url = f"{AUTH_URL}?{q}"

    got = {}
    import http.server

    class CB(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            p = urllib.parse.urlparse(self.path)
            if p.path != "/callback":
                self.send_response(404); self.end_headers(); return
            qs = urllib.parse.parse_qs(p.query)
            got["code"] = (qs.get("code") or [None])[0]
            got["state"] = (qs.get("state") or [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html"); self.end_headers()
            self.wfile.write(b"<h2>SOTA DAW connected to SoundCloud. You can close this tab.</h2>")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 8899), CB)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass
    deadline = time.time() + float(args.get("timeout_sec", 180))
    while time.time() < deadline and "code" not in got:
        time.sleep(0.5)
    srv.shutdown()
    if not got.get("code"):
        return f"no callback received. Open this URL and approve, then call sc_connect again:\n{url}"
    if got.get("state") != state:
        return "state mismatch — aborted (possible CSRF); try sc_connect again."
    t = token_request({"grant_type": "authorization_code", "client_id": c["client_id"],
                       "client_secret": c["client_secret"], "redirect_uri": REDIRECT,
                       "code_verifier": verifier, "code": got["code"]})
    save_token(t)
    me = api("GET", "/me")
    return f"CONNECTED as {me.get('username')} ({me.get('permalink_url')}). Tokens stored (auto-refresh)."


def t_sc_upload(args):
    path = args["file"]
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    if not os.path.exists(path):
        return f"no such file: {args['file']}"
    sharing = args.get("sharing", "private")
    if sharing not in ("private", "public"):
        return "sharing must be private|public"
    fields = {"track[title]": str(args["title"]), "track[sharing]": sharing}
    if args.get("description"):
        fields["track[description]"] = str(args["description"])
    if args.get("genre"):
        fields["track[genre]"] = str(args["genre"])
    if args.get("tags"):
        fields["track[tag_list]"] = str(args["tags"])
    files = {"track[asset_data]": (os.path.basename(path), open(path, "rb").read(),
                                   "audio/wav" if path.lower().endswith(".wav") else "audio/mpeg")}
    if args.get("artwork") and os.path.exists(os.path.join(ROOT, args["artwork"])):
        ap = os.path.join(ROOT, args["artwork"])
        files["track[artwork_data]"] = (os.path.basename(ap), open(ap, "rb").read(), "image/png")
    body, ctype = multipart(fields, files)
    tr = api("POST", "/tracks", data=body, headers={"Content-Type": ctype})
    return (f"UPLOADED ({sharing}): {tr.get('title')} -> {tr.get('permalink_url')} "
            f"(id {tr.get('id')}, {tr.get('duration', 0)//1000}s). "
            + ("Private — flip to public on SoundCloud (or re-upload sharing=public) when the user wants it live."
               if sharing == "private" else "LIVE."))


def t_sc_my_tracks(args):
    lim = int(args.get("limit", 10))
    res = api("GET", f"/me/tracks?limit={lim}&linked_partitioning=true")
    items = res.get("collection", res if isinstance(res, list) else [])
    if not items:
        return "no tracks on the connected account."
    return "\n".join(f"- {t.get('title')} [{t.get('sharing')}] {t.get('permalink_url')}"
                     for t in items[:lim])


TOOLS = {
    "sc_setup_status": (t_sc_setup_status,
                        "SoundCloud connection status: app creds, token, connected profile. Start here.",
                        {"type": "object", "properties": {}}),
    "sc_connect": (t_sc_connect,
                   "One-click SoundCloud OAuth (2.1+PKCE): opens the browser, catches the loopback callback, stores auto-refreshing tokens.",
                   {"type": "object", "properties": {"timeout_sec": {"type": "number"}}}),
    "sc_upload": (t_sc_upload,
                  "Upload a track (wav/mp3) to the connected SoundCloud account. DEFAULTS TO PRIVATE — pass sharing='public' ONLY when the user explicitly asked to publish. Prefer the C2PA-signed master from export.",
                  {"type": "object", "properties": {
                      "file": {"type": "string"}, "title": {"type": "string"},
                      "description": {"type": "string"}, "genre": {"type": "string"},
                      "tags": {"type": "string", "description": "space-separated, quote multiword"},
                      "sharing": {"type": "string", "enum": ["private", "public"]},
                      "artwork": {"type": "string", "description": "png/jpg path"}},
                   "required": ["file", "title"]}),
    "sc_my_tracks": (t_sc_my_tracks, "List the connected account's uploads (title, sharing, link).",
                     {"type": "object", "properties": {"limit": {"type": "number"}}}),
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
        except json.JSONDecodeError:
            continue
        m, id_ = req.get("method"), req.get("id")
        if m == "initialize":
            reply(id_, {"protocolVersion": req["params"].get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "soundcloud-connector", "version": "0.1.0"}})
        elif m == "tools/list":
            reply(id_, {"tools": [{"name": n, "description": d, "inputSchema": s}
                                  for n, (f, d, s) in TOOLS.items()]})
        elif m == "tools/call":
            name = req["params"]["name"]
            args = req["params"].get("arguments") or {}
            try:
                text = TOOLS[name][0](args) if name in TOOLS else f"unknown tool {name}"
                err = False
            except Exception as e:
                text, err = f"{type(e).__name__}: {e}", True
            reply(id_, {"content": [{"type": "text", "text": text}], "isError": err})
        elif m == "ping":
            reply(id_, {})
        elif id_ is not None:
            reply(id_, {})


if __name__ == "__main__":
    main()
