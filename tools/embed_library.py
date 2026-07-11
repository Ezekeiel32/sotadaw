#!/usr/bin/env python3
"""embed_library.py — build the SEMANTIC EARS index (V53).

Gathers every embeddable AUDIO item the box has (kit one-shots, indexed user
samples, rendered preset previews, optionally song renders), embeds each with
CLAP (tools/clap_embed.py), and writes:
  library/embeddings.npz   — ids (unicode) + vecs (float16, N×512)
  library/embeddings.json  — id -> {kind, path, name, category, tags}

Both are gitignored (a per-box derived cache; the audio is the source of truth).

  embed_library.py [--rebuild] [--songs] [--download] [--device cpu|cuda]

Incremental by default: only NEW ids (audio not already embedded) are computed;
--rebuild recomputes everything. --songs adds songs/*.wav renders (full mixes;
off by default so search stays a SOUND search, not a track search).
"""
import argparse
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
NPZ = os.path.join(ROOT, "library", "embeddings.npz")
META = os.path.join(ROOT, "library", "embeddings.json")


def _kit_items():
    items = []
    for kj in sorted(glob.glob(os.path.join(ROOT, "kits", "*", "kit.json"))):
        kdir = os.path.dirname(kj)
        kname = os.path.basename(kdir)
        try:
            kit = json.load(open(kj))
        except Exception:
            continue
        for s in kit.get("samples", []):
            f = s.get("file")
            if not f:
                continue
            p = os.path.join(kdir, f)
            if not os.path.exists(p):
                continue
            items.append({
                "id": f"kit:{kname}:{f}",
                "kind": "kit",
                "path": p,
                "name": f"{kname} {os.path.splitext(f)[0]}",
                "category": kname,
                "tags": [kname],
            })
    return items


def _sample_items():
    lib = os.path.join(ROOT, "library.json")
    if not os.path.exists(lib):
        return []
    try:
        d = json.load(open(lib))
    except Exception:
        return []
    out = []
    for s in d.get("samples", []):
        p = s.get("path")
        if not p or not os.path.exists(p):
            continue
        out.append({
            "id": f"sample:{p}",
            "kind": "sample",
            "path": p,
            "name": s.get("name", os.path.basename(p)),
            "category": "sample",
            "tags": s.get("tags", []),
        })
    return out


def _preview_items():
    """Rendered preset previews: filename sha1(plugin|name)[:16] -> real name."""
    lib = os.path.join(ROOT, "library.json")
    by_sha = {}
    if os.path.exists(lib):
        try:
            for p in json.load(open(lib)).get("vst_presets", []):
                k = hashlib.sha1(f"{p['plugin']}|{p['name']}".encode()).hexdigest()[:16]
                by_sha[k] = p
        except Exception:
            pass
    out = []
    for w in sorted(glob.glob(os.path.join(ROOT, "songs", ".preset_previews", "*.wav"))):
        k = os.path.splitext(os.path.basename(w))[0]
        p = by_sha.get(k)
        if not p:
            continue
        out.append({
            "id": f"preset:{k}",
            "kind": "preset",
            "path": w,
            "name": f"{p['plugin']} / {p['name']}",
            "category": p.get("category", ""),
            "tags": [p["plugin"], p.get("category", "")],
        })
    return out


def _song_items():
    out = []
    for w in sorted(glob.glob(os.path.join(ROOT, "songs", "*.wav"))):
        b = os.path.basename(w)
        if b.startswith("_") or "_tmp" in b:      # skip proposals/scratch
            continue
        out.append({
            "id": f"song:{b}",
            "kind": "song",
            "path": w,
            "name": os.path.splitext(b)[0],
            "category": "song",
            "tags": ["song"],
        })
    return out


def gather(include_songs=False):
    items = _kit_items() + _sample_items() + _preview_items()
    if include_songs:
        items += _song_items()
    seen, uniq = set(), []
    for it in items:
        if it["id"] in seen:
            continue
        seen.add(it["id"])
        uniq.append(it)
    return uniq


def load_index():
    """Return (ids:list, vecs:float32 N×512, meta:dict) or empty triple."""
    import numpy as np
    if not (os.path.exists(NPZ) and os.path.exists(META)):
        return [], np.zeros((0, 512), "float32"), {}
    z = np.load(NPZ)
    ids = [str(x) for x in z["ids"]]
    vecs = z["vecs"].astype("float32")
    meta = json.load(open(META))
    return ids, vecs, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--songs", action="store_true")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--device", default=None)
    a = ap.parse_args()

    import clap_embed
    if not clap_embed.available(allow_download=a.download):
        print("SKIP: CLAP unavailable (torch/transformers/librosa or checkpoint "
              "absent; --download to fetch). No index written.")
        return 0

    import numpy as np
    items = gather(include_songs=a.songs)
    if not items:
        print("no embeddable audio found (kits/samples/previews empty)")
        return 0

    old_ids, old_vecs, _ = ([], np.zeros((0, 512), "float32"), {})
    if not a.rebuild:
        old_ids, old_vecs, _ = load_index()
    have = {i: old_vecs[n] for n, i in enumerate(old_ids)}

    todo = [it for it in items if it["id"] not in have]
    print(f"corpus: {len(items)} items | cached: {len(have)} | to embed: {len(todo)}")
    if todo:
        import time
        clap_embed.load(device=a.device, allow_download=a.download)
        t0 = time.time()
        new_vecs = clap_embed.embed_audio([it["path"] for it in todo])
        for n, it in enumerate(todo):
            have[it["id"]] = new_vecs[n]
        print(f"embedded {len(todo)} in {time.time()-t0:.1f}s "
              f"(device={clap_embed._state['device']})")

    # rebuild ordered arrays over the CURRENT corpus (drops stale ids)
    ids = [it["id"] for it in items]
    vecs = np.stack([have[i] for i in ids]).astype("float16")
    meta = {it["id"]: {k: it[k] for k in ("kind", "path", "name", "category", "tags")}
            for it in items}
    os.makedirs(os.path.dirname(NPZ), exist_ok=True)
    np.savez(NPZ, ids=np.array(ids), vecs=vecs)
    json.dump(meta, open(META, "w"), indent=1)
    by_kind = {}
    for it in items:
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
    print(f"WROTE {os.path.relpath(NPZ, ROOT)} ({tuple(vecs.shape)}, "
          f"{vecs.nbytes/1e6:.2f} MB) + meta")
    print("  by kind: " + ", ".join(f"{k}={v}" for k, v in sorted(by_kind.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
