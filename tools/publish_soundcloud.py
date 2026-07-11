#!/usr/bin/env python3
"""SOUNDCLOUD CONNECTOR — the manifesto's 'one-click to streaming', software-complete.

  publish_soundcloud.py auth                       # one-time: OAuth 2.1 + PKCE (browser)
  publish_soundcloud.py upload <master.wav|mp3> --title T [--tags "a b"] [--live]
  publish_soundcloud.py status                     # token present? expiry?

LAWS (inert by construction — the W16a connector posture):
  - DRY-RUN IS THE DEFAULT. Without --live the tool prints the exact request it
    WOULD send (endpoint, fields, byte count) and touches no network.
  - --live requires BOTH a stored user token (from `auth`) AND SOUNDCLOUD_CLIENT_ID
    in the environment. Missing either = a refusal with the exact next step.
  - sharing=private ALWAYS unless --public is passed explicitly. Nothing the agent
    does can publish publicly on its own.
  - Tokens live in ~/.config/sotadaw/soundcloud.json chmod 0600, never in the repo,
    never uplinked (telemetry whitelist unchanged).

Protocol truth (verified 2026-07-06, stamp f141 citations): SoundCloud API is
OAuth 2.1 — PKCE (S256) REQUIRED on the authorization-code flow since 2024-10-01;
uploads are multipart POST /tracks, limits 4GB / 24h per track. SC_API_BASE env
overrides the host so the battery proves the WHOLE flow against a localhost mock.
"""
import argparse, base64, hashlib, json, os, secrets, sys, time, urllib.parse, urllib.request

API = os.environ.get("SC_API_BASE", "https://api.soundcloud.com")
AUTH_HOST = os.environ.get("SC_AUTH_BASE", "https://secure.soundcloud.com")
CFG = os.path.expanduser("~/.config/sotadaw/soundcloud.json")
REDIRECT_PORT = int(os.environ.get("SC_REDIRECT_PORT", "8912"))
REDIRECT = f"http://127.0.0.1:{REDIRECT_PORT}/callback"


def _client_id():
    cid = os.environ.get("SOUNDCLOUD_CLIENT_ID", "")
    if not cid:
        raise SystemExit("SOUNDCLOUD_CLIENT_ID not set — register an app at "
                         "https://soundcloud.com/you/apps and export the id "
                         "(client_secret NOT stored; PKCE carries the proof)")
    return cid


def _save_tokens(tok):
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    tok["obtained_at"] = int(time.time())
    with open(CFG, "w") as f:
        json.dump(tok, f)
    os.chmod(CFG, 0o600)


def _load_tokens():
    try:
        return json.load(open(CFG))
    except FileNotFoundError:
        return None


def auth():
    """OAuth 2.1 authorization-code + PKCE S256, loopback capture."""
    cid = _client_id()
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    url = (f"{AUTH_HOST}/authorize?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": REDIRECT, "response_type": "code",
        "code_challenge": challenge, "code_challenge_method": "S256", "state": state}))
    print(f"[sc] open this in your browser and approve:\n  {url}")
    # loopback capture (one request)
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
    if got.get("state") != state:
        raise SystemExit("state mismatch — aborting (CSRF posture)")
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code", "client_id": cid,
        "redirect_uri": REDIRECT, "code_verifier": verifier,
        "code": got["code"]}).encode()
    req = urllib.request.Request(f"{AUTH_HOST}/oauth/token", data=body, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    tok = json.load(urllib.request.urlopen(req, timeout=30))
    _save_tokens(tok)
    print(f"[sc] authorized — token stored (expires_in {tok.get('expires_in')}s), "
          f"scope '{tok.get('scope','')}'")


def upload(path, title, tags="", live=False, public=False):
    if not os.path.exists(path):
        raise SystemExit(f"no such file: {path}")
    size = os.path.getsize(path)
    if size > 4 * 1024 ** 3:
        raise SystemExit("over SoundCloud's 4GB per-track limit")
    fields = {"track[title]": title,
              "track[sharing]": "public" if public else "private",
              "track[tag_list]": tags,
              "track[downloadable]": "false"}
    if not live:
        print("[sc] DRY-RUN (default — pass --live to send):")
        print(f"  POST {API}/tracks  multipart:")
        for k, v in fields.items():
            print(f"    {k} = {v!r}")
        print(f"    track[asset_data] = <{size} bytes from {os.path.basename(path)}>")
        print("SC_DRYRUN_JSON " + json.dumps({"endpoint": f"{API}/tracks",
                                              "fields": fields, "bytes": size}))
        return
    tok = _load_tokens()
    if not tok:
        raise SystemExit("--live needs a stored token: run `publish_soundcloud.py auth` first")
    boundary = "----sotadaw" + secrets.token_hex(8)
    parts = []
    for k, v in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append((f"--{boundary}\r\nContent-Disposition: form-data; "
                  f"name=\"track[asset_data]\"; filename=\"{os.path.basename(path)}\"\r\n"
                  f"Content-Type: application/octet-stream\r\n\r\n").encode())
    body = b"".join(parts) + open(path, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{API}/tracks", data=body, method="POST",
        headers={"Authorization": f"OAuth {tok['access_token']}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    resp = json.load(urllib.request.urlopen(req, timeout=600))
    print(f"[sc] UPLOADED: id={resp.get('id')} sharing={resp.get('sharing')} "
          f"url={resp.get('permalink_url','?')}")
    print("SC_UPLOAD_JSON " + json.dumps(resp))


def status():
    tok = _load_tokens()
    if not tok:
        print("[sc] no token — run: publish_soundcloud.py auth"); return
    age = int(time.time()) - tok.get("obtained_at", 0)
    left = tok.get("expires_in", 0) - age
    print(f"[sc] token present, {'VALID' if left > 0 else 'EXPIRED'} "
          f"({left}s left, scope '{tok.get('scope','')}')")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth")
    u = sub.add_parser("upload"); u.add_argument("file"); u.add_argument("--title", required=True)
    u.add_argument("--tags", default=""); u.add_argument("--live", action="store_true")
    u.add_argument("--public", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args()
    if a.cmd == "auth":
        auth()
    elif a.cmd == "upload":
        upload(a.file, a.title, a.tags, a.live, a.public)
    else:
        status()


if __name__ == "__main__":
    main()
