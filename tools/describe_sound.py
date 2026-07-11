#!/usr/bin/env python3
"""DESCRIBE_SOUND — zero-shot audio→WORDS through the CLAP kernel (semantic ears speak).

  describe_sound.py <audio> [audio2 ...] [--k N] [--json]

The ears could measure (analyze2), see (hear), and retrieve (sound_neighbors /
clap_query). The missing verb was DESCRIBE: rank any wav against curated tag
banks (role / timbre / energy / space) in CLAP's joint space and return ranked
words + one honest sentence — so the agent can say "punchy aggressive kick,
dry" about a sample it has never been told about, and library moves stop being
blind. Zero-shot classification, no training, no black box audio generation.

Graceful law (clap_query convention): CLAP unavailable → {"available":false,
"reason"} exit 3; unreadable/silent files get {"available":false} per-file.
Bank text embeddings are content-hashed and cached (~/.cache/sotadaw).
Machine line: DESCRIBE_JSON {...}
"""
import argparse, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

BANKS = {
    "role": ["kick drum", "snare drum", "hi-hat cymbal", "clap", "tom drum",
             "crash cymbal", "drum loop", "percussion", "808 sub bass",
             "bass guitar", "synth bass", "synth lead", "synth pad",
             "arpeggiated synth", "piano", "electric piano", "organ",
             "acoustic guitar", "electric guitar", "strings", "brass", "flute",
             "bell", "pluck", "choir", "male vocals", "female vocals",
             "rap vocals", "spoken word", "riser sound effect", "noise sweep",
             "ambient texture", "full song mix"],
    "timbre": ["dark", "bright", "warm", "harsh", "distorted", "clean",
               "punchy", "soft", "metallic", "airy", "gritty", "lo-fi",
               "vintage analog", "digital", "hollow", "thick"],
    "energy": ["aggressive", "calm", "melancholic", "euphoric", "tense",
               "dreamy", "driving", "laid-back", "epic", "playful"],
    "space": ["dry close-miked", "reverberant hall", "small room",
              "wide stereo", "narrow mono", "echoing delay"],
    # NO genre bank BY VERDICT (2026-07-10 pass 3): zero-shot CLAP genre fails
    # the family-precision law on this checkpoint — real stems read gospel/
    # dancehall for rap/choir, synthetic renders read footwork for blues.
    # Genre stays with the KG + import DNA rails, not the word rail.
}
PROMPT = {"role": "This is a sound of a {}.", "timbre": "This sound is {}.",
          "energy": "This sound feels {}.", "space": "This sound is {}."}


def bank_matrix():
    """(tags, prompts, np.ndarray) with a content-hashed disk cache."""
    import numpy as np
    tags, prompts = [], []
    for bank, words in BANKS.items():
        for w in words:
            tags.append((bank, w))
            prompts.append(PROMPT[bank].format(w))
    key = hashlib.sha256(("\n".join(prompts)).encode()).hexdigest()[:12]
    cache_dir = os.path.expanduser("~/.cache/sotadaw")
    cache = os.path.join(cache_dir, f"clap_bank_{key}.npz")
    if os.path.exists(cache):
        try:
            return tags, np.load(cache)["T"]
        except Exception:
            pass
    import clap_embed
    T = clap_embed.embed_texts(prompts)
    try:
        os.makedirs(cache_dir, exist_ok=True)
        np.savez(cache, T=T)
    except Exception:
        pass
    return tags, T


def describe(paths, k=5):
    import numpy as np
    import clap_embed
    if not clap_embed.available():
        return {"available": False,
                "reason": "CLAP checkpoint not cached — run once with network or embed_library first"}
    tags, T = bank_matrix()
    A = clap_embed.embed_audio(list(paths))
    files = []
    for i, p in enumerate(paths):
        a = A[i]
        if float(np.linalg.norm(a)) < 1e-6:
            files.append({"path": p, "available": False, "reason": "unreadable or silent"})
            continue
        cos = T @ a
        by_bank = {}
        for (bank, w), c in zip(tags, cos):
            by_bank.setdefault(bank, []).append({"tag": w, "score": round(float(c), 4)})
        for bank in by_bank:
            by_bank[bank].sort(key=lambda x: (-x["score"], x["tag"]))
            by_bank[bank] = by_bank[bank][:k]
        sent = (f"{by_bank['timbre'][0]['tag']}, {by_bank['energy'][0]['tag']} "
                f"{by_bank['role'][0]['tag']} ({by_bank['space'][0]['tag']})")
        files.append({"path": p, "available": True, "tags": by_bank, "sentence": sent})
    return {"available": True, "files": files}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", nargs="+")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="machine line only")
    a = ap.parse_args()
    out = describe(a.audio, a.k)
    if not out["available"]:
        print("DESCRIBE_JSON " + json.dumps(out))
        sys.exit(3)
    if not a.json:
        for f in out["files"]:
            if f.get("available"):
                roles = " ".join(f"{t['tag']}:{t['score']}" for t in f["tags"]["role"][:3])
                print(f"[describe] {os.path.basename(f['path'])}: {f['sentence']}   ({roles})")
            else:
                print(f"[describe] {os.path.basename(f['path'])}: {f['reason']}")
    print("DESCRIBE_JSON " + json.dumps(out))


if __name__ == "__main__":
    main()
