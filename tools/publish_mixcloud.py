#!/usr/bin/env python3
"""MIXCLOUD CONNECTOR — DJ sets to the DJ platform (CC4 P4/P7; the AI-DJ's shopfront).

  publish_mixcloud.py auth                                   # one-time browser OAuth2
  publish_mixcloud.py upload <set.mp3|wav> --name N [--desc D] [--tags "a b"]
                      [--sections plan.json] [--live]
  publish_mixcloud.py status

sections plan.json = [{"artist": A, "song": S, "start": seconds}, ...] — rides as
Mixcloud's native tracklist chapters (sections-N-artist/song/start_time), so a
dj_set upload arrives CHAPTERED like a pro mix page.

LAWS (identical to the SoundCloud organ — inert by construction):
  - DRY-RUN default: prints the exact multipart plan, zero network without --live.
  - --live needs a stored token (`auth`) + MIXCLOUD_CLIENT_ID; refusals name the step.
  - Tokens ~/.config/sotadaw/mixcloud.json chmod 0600; client_secret only ever read
    from MIXCLOUD_CLIENT_SECRET env at auth time, never written to disk.
  - MX_API_BASE / MX_WWW_BASE env override the hosts -> the battery proves the whole
    flow against a localhost mock.

Protocol truth (verified 2026-07-06, stamp f143): OAuth2 authorization-code
(browser-based only), single multipart POST /upload/ (mp3+metadata+image together;
audio cap 4294967296 bytes, picture 10MB). NULL LEDGERED same firing: Spotify has
NO upload path by design (distributor-only; Feb-2026 purge even removed playlist
creation) — do not build a Spotify upload organ.
"""
import argparse, json, os, secrets, sys, time, urllib.parse, urllib.request

API = os.environ.get("MX_API_BASE", "https://api.mixcloud.com")
WWW = os.environ.get("MX_WWW_BASE", "https://www.mixcloud.com")
CFG = os.path.expanduser("~/.config/sotadaw/mixcloud.json")
REDIRECT_PORT = int(os.environ.get("MX_REDIRECT_PORT", "8913"))
REDIRECT = f"http://127.0.0.1:{REDIRECT_PORT}/callback"


def _client_id():
    cid = os.environ.get("MIXCLOUD_CLIENT_ID", "")
    if not cid:
        raise SystemExit("MIXCLOUD_CLIENT_ID not set — create an app at "
                         "https://www.mixcloud.com/developers/create/ and export the id")
    return cid


def _save(tok):
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    tok["obtained_at"] = int(time.time())
    with open(CFG, "w") as f:
        json.dump(tok, f)
    os.chmod(CFG, 0o600)


def _load():
    try:
        return json.load(open(CFG))
    except FileNotFoundError:
        return None


def auth():
    cid = _client_id()
    sec = os.environ.get("MIXCLOUD_CLIENT_SECRET", "")
    if not sec:
        raise SystemExit("MIXCLOUD_CLIENT_SECRET not set (needed once, at auth; never stored)")
    url = f"{WWW}/oauth/authorize?client_id={cid}&redirect_uri={urllib.parse.quote(REDIRECT)}"
    print(f"[mx] open this in your browser and approve:\n  {url}")
    import http.server
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200); self.end_headers()
            self.wfile.write(b"sotadaw: authorized - you can close this tab")
        def log_message(self, *a):
            pass
    srv = http.server.HTTPServer(("127.0.0.1", REDIRECT_PORT), H)
    srv.timeout = 300
    srv.handle_request()
    if "code" not in got:
        raise SystemExit("no code returned - authorization denied or timed out")
    q = urllib.parse.urlencode({"client_id": cid, "redirect_uri": REDIRECT,
                                "client_secret": sec, "code": got["code"]})
    tok = json.load(urllib.request.urlopen(f"{WWW}/oauth/access_token?{q}", timeout=30))
    _save(tok)
    print("[mx] authorized - token stored (Mixcloud tokens do not expire)")


def _sections_fields(path):
    out = {}
    if not path:
        return out
    plan = json.load(open(path))
    for i, s in enumerate(plan):
        out[f"sections-{i}-artist"] = str(s.get("artist", ""))
        out[f"sections-{i}-song"] = str(s.get("song", ""))
        out[f"sections-{i}-start_time"] = str(int(float(s.get("start", 0))))
    return out


def upload(path, name, desc="", tags="", sections=None, live=False):
    if not os.path.exists(path):
        raise SystemExit(f"no such file: {path}")
    size = os.path.getsize(path)
    if size > 4294967296:
        raise SystemExit("over Mixcloud's 4GB audio cap")
    fields = {"name": name}
    if desc:
        fields["description"] = desc
    for i, t in enumerate([t for t in tags.split() if t][:5]):
        fields[f"tags-{i}-tag"] = t
    fields.update(_sections_fields(sections))
    if not live:
        print("[mx] DRY-RUN (default — pass --live to send):")
        print(f"  POST {API}/upload/  multipart:")
        for k, v in sorted(fields.items()):
            print(f"    {k} = {v!r}")
        print(f"    mp3 = <{size} bytes from {os.path.basename(path)}>")
        print("MX_DRYRUN_JSON " + json.dumps({"endpoint": f"{API}/upload/",
                                              "fields": fields, "bytes": size}))
        return
    tok = _load()
    if not tok:
        raise SystemExit("--live needs a stored token: run `publish_mixcloud.py auth` first")
    boundary = "----sotadaw" + secrets.token_hex(8)
    parts = []
    for k, v in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append((f"--{boundary}\r\nContent-Disposition: form-data; "
                  f"name=\"mp3\"; filename=\"{os.path.basename(path)}\"\r\n"
                  f"Content-Type: application/octet-stream\r\n\r\n").encode())
    body = b"".join(parts) + open(path, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
    url = f"{API}/upload/?access_token={urllib.parse.quote(tok['access_token'])}"
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    resp = json.load(urllib.request.urlopen(req, timeout=900))
    print(f"[mx] UPLOADED: {resp.get('result', {}).get('key', resp)}")
    print("MX_UPLOAD_JSON " + json.dumps(resp))


def status():
    tok = _load()
    print("[mx] token present (Mixcloud tokens do not expire)" if tok
          else "[mx] no token — run: publish_mixcloud.py auth")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth")
    u = sub.add_parser("upload"); u.add_argument("file"); u.add_argument("--name", required=True)
    u.add_argument("--desc", default=""); u.add_argument("--tags", default="")
    u.add_argument("--sections", default=None); u.add_argument("--live", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "auth":
        auth()
    elif a.cmd == "upload":
        upload(a.file, a.name, a.desc, a.tags, a.sections, a.live)
    else:
        status()


if __name__ == "__main__":
    main()
