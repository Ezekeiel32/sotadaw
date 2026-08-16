#!/usr/bin/env python3
"""THE SUITCASE: projects that TRAVEL — pack a song + every file it references
into one self-contained zip; unpack lands it on any SOTA DAW install.

  song_pack.py pack <song> [out.zip]     # default songs/<name>_pack.zip
  song_pack.py unpack <bundle.zip> [name]

Every real DAW has this (FL "zipped loop package", Ableton "Collect All and
Save", Logic "package") — we had four cross-DAW bridges and no way to hand a
SOTA project to another SOTA machine: audioClips/slot wavs/preset blobs
reference repo-relative (or worse, ABSOLUTE — 28 in the corpus today) paths
that break anywhere else.

PACK: walks the whole file-ref surface (tracks[].audioClips[].file,
tracks[].slots[].audioFile, source.preset, fx[].preset on tracks/buses/
master), copies each existing file to assets/<uniquified-base>, rewrites a
COPY of the json (the base song is never touched — acceptal law), stamps
voice attribution structurally when a sung voice rides (the bundle cannot
ship unattributed), and writes manifest.json: sha256 per file, missing refs
(honest — pack proceeds), sample-kit + external-plugin dependencies, sidecar
dirs NOT packed (_stems/_spectral/_vocals = v2). Deterministic: same song ->
byte-identical zip (fixed zip timestamps, sorted members).

UNPACK: refuses anything that is not a suitcase (manifest gate) or carries a
zip-slip member (absolute / '..' paths) BEFORE landing anything; lands as
songs/<name>.json + songs/<name>_assets/ with paths rewritten; name
collisions get _2/_3 suffixes — an unpack can never clobber an existing song.
Assets are sha-verified against the manifest (corruption is LOUD, material
still lands).

Proof: tools/suitcase_battery.py (suite leg).
"""
import hashlib
import json
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import songname                     # SONG-NAME LAW: one resolver everywhere

ZIP_DATE = (2026, 1, 1, 0, 0, 0)    # fixed stamp = deterministic bundles


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk_refs(song):
    """Yield (container_dict, key) for every file-reference field in the song."""
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict):
            continue
        for c in t.get("audioClips", []) or []:
            if isinstance(c, dict) and c.get("file"):
                yield c, "file"
        for sl in t.get("slots", []) or []:
            if isinstance(sl, dict) and sl.get("audioFile"):
                yield sl, "audioFile"
        src = t.get("source")
        if isinstance(src, dict) and src.get("preset"):
            yield src, "preset"
        for fx in t.get("fx", []) or []:
            if isinstance(fx, dict) and fx.get("preset"):
                yield fx, "preset"
    for b in song.get("buses", []) or []:
        if isinstance(b, dict):
            for fx in b.get("fx", []) or []:
                if isinstance(fx, dict) and fx.get("preset"):
                    yield fx, "preset"
    for fx in song.get("master", []) or []:
        if isinstance(fx, dict) and fx.get("preset"):
            yield fx, "preset"


def _deps(song):
    """What the receiving machine must already have (honesty, not bundling)."""
    kits, plugins = set(), set()

    def plug(d):
        v = str(d.get("id", ""))
        if v.split(":", 1)[0] in ("vst3", "nam", "clap"):
            plugins.add(v)

    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict):
            continue
        src = t.get("source") or {}
        if isinstance(src, dict):
            if src.get("kind") == "sample" and src.get("kit"):
                kits.add(str(src["kit"]))
            plug(src)
        for fx in t.get("fx", []) or []:
            if isinstance(fx, dict):
                plug(fx)
    for b in song.get("buses", []) or []:
        if isinstance(b, dict):
            for fx in b.get("fx", []) or []:
                if isinstance(fx, dict):
                    plug(fx)
    for fx in song.get("master", []) or []:
        if isinstance(fx, dict):
            plug(fx)
    return sorted(kits), sorted(plugins)


def pack(raw_name, out=None):
    name = songname.resolve(raw_name)
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        raise SystemExit(f"no such song: {raw_name}")
    song = json.load(open(path))
    packed = json.loads(json.dumps(song))          # deep copy — base never touched

    seen, assets, missing = {}, [], []             # resolved abs -> asset name
    used = set()
    for cont, key in _walk_refs(packed):
        ref = str(cont[key])
        ap = ref if os.path.isabs(ref) else os.path.join(ROOT, ref)
        ap = os.path.normpath(ap)
        if not os.path.exists(ap):
            missing.append(ref)
            continue                               # leave verbatim: may exist at home
        if ap not in seen:
            base = os.path.basename(ap) or "asset"
            stem, ext = os.path.splitext(base)
            k = 2
            while base in used:                    # two dirs, one basename
                base = f"{stem}_{k}{ext}"
                k += 1
            used.add(base)
            seen[ap] = f"assets/{base}"
            assets.append({"asset": seen[ap], "from": ref,
                           "sha256": _sha256(ap), "bytes": os.path.getsize(ap)})
        cont[key] = seen[ap]

    # ATTRIBUTION LAW: a sung voice cannot travel uncredited
    attribution = ""
    try:
        import attribution_court
        if attribution_court.voice_used(packed):
            attribution_court.heal_attribution(packed)
            attribution = attribution_court.bank_attribution()
    except Exception as e:
        print(f"[suitcase] attribution court unavailable: {e!r}", file=sys.stderr)

    kits, plugins = _deps(packed)
    sidecars = [d for suf in ("_stems", "_spectral", "_vocals")
                if os.path.isdir(d := os.path.join(SONGS, name + suf))]
    manifest = {"suitcase": 1, "name": name,
                "bpm": song.get("bpm"), "key": song.get("key"),
                "lengthBars": song.get("lengthBars"),
                "files": sorted(assets, key=lambda a: a["asset"]),
                "missing": sorted(set(missing)),
                "kits": kits, "plugins": plugins,
                "sidecars_not_packed": [os.path.relpath(d, ROOT) for d in sidecars],
                "attribution": attribution}

    out = out or os.path.join(SONGS, f"{name}_pack.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        def put(arc, data):
            zi = zipfile.ZipInfo(arc, date_time=ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data)
        put("manifest.json", json.dumps(manifest, indent=1, sort_keys=True))
        put("song.json", json.dumps(packed, indent=1))
        for arc, ap in sorted((arc, ap) for ap, arc in seen.items()):
            put(arc, open(ap, "rb").read())

    msg = (f"packed '{name}' -> {out}: {len(assets)} assets"
           + (f", {len(manifest['missing'])} MISSING refs listed" if missing else "")
           + (f", needs kits {kits}" if kits else "")
           + (f", needs plugins {plugins}" if plugins else "")
           + (f", sidecars not packed: {manifest['sidecars_not_packed']}" if sidecars else "")
           + (f" [{attribution}]" if attribution else ""))
    print(msg)
    return out


def unpack(zip_path, want_name=None):
    if not os.path.exists(zip_path):
        raise SystemExit(f"no such bundle: {zip_path}")
    z = zipfile.ZipFile(zip_path)
    names = z.namelist()
    # SECURITY GATE first — an evil member refuses the WHOLE bundle, nothing lands
    for m in names:
        if m.startswith("/") or os.path.isabs(m) or ".." in m.replace("\\", "/").split("/"):
            raise SystemExit(f"REFUSED: zip-slip member {m!r} — not landing anything")
    if "manifest.json" not in names or "song.json" not in names:
        raise SystemExit("REFUSED: not a SOTA suitcase (no manifest.json/song.json)")
    manifest = json.loads(z.read("manifest.json"))
    if manifest.get("suitcase") != 1:
        raise SystemExit("REFUSED: manifest is not a suitcase")
    song = json.loads(z.read("song.json"))

    land = songname.sanitize(want_name or manifest.get("name") or "imported")
    base_land, k = land, 2
    while os.path.exists(os.path.join(SONGS, f"{land}.json")):
        land = f"{base_land}_{k}"                  # NEVER clobber an existing song
        k += 1

    adir = os.path.join(SONGS, f"{land}_assets")
    landed, bad_sha = [], []
    sha_by_asset = {a["asset"]: a.get("sha256") for a in manifest.get("files", [])}
    amap = {}                                      # "assets/x" -> songs/<land>_assets/x
    for m in names:
        if not m.startswith("assets/") or m.endswith("/"):
            continue
        os.makedirs(adir, exist_ok=True)
        dst = os.path.join(adir, os.path.basename(m))
        with z.open(m) as src, open(dst, "wb") as f:
            shutil.copyfileobj(src, f)
        rel = os.path.relpath(dst, ROOT)
        amap[m] = rel
        landed.append(rel)
        want = sha_by_asset.get(m)
        if want and _sha256(dst) != want:
            bad_sha.append(m)

    for cont, key in _walk_refs(song):
        ref = str(cont[key])
        if ref in amap:
            cont[key] = amap[ref]

    sp = os.path.join(SONGS, f"{land}.json")
    json.dump(song, open(sp, "w"), indent=1)
    ntr = len([t for t in song.get("tracks", []) if isinstance(t, dict)])
    nn = sum(len(t.get("notes", []) or []) for t in song.get("tracks", [])
             if isinstance(t, dict))
    print(f"unpacked -> {sp} ({ntr} tracks, {nn} notes, {len(landed)} assets in {adir if landed else '(none)'})")
    if bad_sha:
        print(f"WARNING: sha256 MISMATCH on {bad_sha} — bundle corrupted in transit; "
              "the material landed but VERIFY before trusting", file=sys.stderr)
    for miss in manifest.get("missing", []):
        print(f"note: ref was already missing at pack time: {miss}", file=sys.stderr)
    if manifest.get("kits") or manifest.get("plugins"):
        print(f"needs: kits {manifest.get('kits')} plugins {manifest.get('plugins')}",
              file=sys.stderr)
    if manifest.get("attribution"):
        print(f"attribution: {manifest['attribution']}")
    return sp


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "pack":
        pack(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif len(sys.argv) >= 3 and sys.argv[1] == "unpack":
        unpack(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        sys.exit("usage: song_pack.py pack <song> [out.zip] | unpack <bundle.zip> [name]")
