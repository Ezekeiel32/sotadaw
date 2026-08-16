#!/usr/bin/env python3
"""MUSHRA-LITE — wave 93 (r-32 item 252): the periodic HUMAN anchor
that keeps the courts honest against Goodhart. Self-contained (the
provenance gate bans GPL imports — webMUSHRA stays out of the graph;
this is the -lite in the name).

Protocol (the modern findings, encoded):
  NMR      the hidden reference is PRESENT but never named (kills
           reference-matching bias that punishes world-class masters)
  ANCHOR   a 3.5k lowpassed copy of the reference (standard low anchor)
  BLINDING items ship as content-hash names; the key stays server-side
  SCREEN   drop assessors who rate the hidden anchor >= the hidden
           reference on >15% of trials (mandatory post-screening)
  PURPOSE  per MILESTONE, never per take: measure how well the courts
           track humans (rank correlation) and detect proxy drift

  assemble(out_dir, candidates, reference)   -> trial dir + html page
  screen(ratings_jsonl, trial_json)          -> kept/dropped assessors
  proxy_report(ratings, trial, court_scores) -> the drift number
"""
import hashlib
import json
import os
import shutil
import sys
import wave as wv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402


def _read(path):
    w = wv.open(path, "rb")
    sr, sw, ch, n = (w.getframerate(), w.getsampwidth(), w.getnchannels(),
                     w.getnframes())
    raw = w.readframes(n)
    w.close()
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000,
                     x).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return x.reshape(-1, ch).mean(axis=1), sr


def _write(path, x, sr):
    w = wv.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
    w.close()


def make_anchor(reference_wav, out_wav, cutoff=3500.0):
    x, sr = _read(reference_wav)
    S = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    S[f > cutoff] = 0
    _write(out_wav, np.fft.irfft(S, len(x)).real, sr)
    return out_wav


def assemble(out_dir, candidates, reference):
    os.makedirs(out_dir, exist_ok=True)
    items = {}

    def blind(path, role):
        h = hashlib.sha256(open(path, "rb").read(1 << 18)).hexdigest()[:10]
        key = f"item_{h}"
        if key in items:
            raise RuntimeError(
                f"'{os.path.basename(path)}' is byte-identical to "
                f"'{items[key]['source']}' — a trial with duplicate "
                "takes measures nothing; fix the rig")
        shutil.copyfile(path, os.path.join(out_dir, key + ".wav"))
        items[key] = {"role": role, "source": os.path.basename(path)}
        return key

    for c in candidates:
        blind(c, "candidate")
    blind(reference, "hidden_reference")
    anchor_p = os.path.join(out_dir, "_anchor_src.wav")
    make_anchor(reference, anchor_p)
    blind(anchor_p, "hidden_anchor")
    os.remove(anchor_p)
    order = sorted(items)                     # content-hash order = shuffle
    trial = {"protocol": "MUSHRA-lite NMR", "items": items,
             "order": order,
             "instructions": ("Rate each item 0-100 for overall "
                              "production quality. There is no named "
                              "reference — judge the music.")}
    json.dump(trial, open(os.path.join(out_dir, "trial.json"), "w"),
              indent=1)
    rows = "\n".join(
        f'<div class="it"><b>{i + 1}</b> <audio controls '
        f'src="{name}.wav"></audio> <input type="range" min="0" '
        f'max="100" value="50" id="{name}">'
        f'<span id="{name}_v">50</span></div>'
        for i, name in enumerate(order))
    html = f"""<meta charset="utf-8"><title>MUSHRA-lite trial</title>
<style>body{{font-family:sans-serif;max-width:720px;margin:2em auto}}
.it{{margin:1em 0;display:flex;gap:1em;align-items:center}}</style>
<h2>Rate each item (0-100)</h2><p>{trial["instructions"]}</p>
<label>Your id: <input id="who" value="listener1"></label>
{rows}
<button onclick="save()">Save ratings</button>
<script>
document.querySelectorAll('input[type=range]').forEach(r =>
  r.oninput = () => document.getElementById(r.id + '_v').textContent
    = r.value);
function save() {{
  const out = {{assessor: document.getElementById('who').value,
               ratings: {{}}}};
  document.querySelectorAll('input[type=range]').forEach(r =>
    out.ratings[r.id] = +r.value);
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(out)]));
  a.download = 'ratings_' + out.assessor + '.json';
  a.click();
}}
</script>"""
    open(os.path.join(out_dir, "trial.html"), "w").write(html)
    return trial


def screen(ratings_rows, trial):
    """Mandatory post-screening: an assessor who rates the hidden
    anchor >= the hidden reference is mis-hearing; >15% of such trials
    drops them (here: one trial = one comparison)."""
    ref = next(k for k, v in trial["items"].items()
               if v["role"] == "hidden_reference")
    anc = next(k for k, v in trial["items"].items()
               if v["role"] == "hidden_anchor")
    kept, dropped = [], []
    for row in ratings_rows:
        r = row.get("ratings", {})
        if r.get(anc, 0) >= r.get(ref, 100):
            dropped.append(row.get("assessor", "?"))
        else:
            kept.append(row)
    return {"kept": kept, "dropped": dropped}


def _rank_corr(a, b):
    """Spearman via rank Pearson (pure)."""
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        for r, i in enumerate(order):
            rk[i] = float(r)
        return rk
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra)
           * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0.0


def proxy_report(ratings_rows, trial, court_scores):
    """THE DRIFT NUMBER: rank correlation between screened human means
    and the courts' scores over the CANDIDATES. Under ~0.5 = the
    automated courts have drifted from human preference (Goodhart)."""
    sc = screen(ratings_rows, trial)
    cands = [k for k, v in trial["items"].items()
             if v["role"] == "candidate"]
    if not sc["kept"] or len(cands) < 3:
        return {"ok": False, "why": "not enough screened data"}
    means = []
    courts = []
    for c in cands:
        vals = [row["ratings"].get(c) for row in sc["kept"]
                if row["ratings"].get(c) is not None]
        src = trial["items"][c]["source"]
        if not vals or src not in court_scores:
            continue
        means.append(sum(vals) / len(vals))
        courts.append(float(court_scores[src]))
    if len(means) < 3:
        return {"ok": False, "why": "not enough matched candidates"}
    rho = _rank_corr(means, courts)
    return {"ok": True, "rank_corr": round(rho, 3),
            "assessors_kept": len(sc["kept"]),
            "assessors_dropped": sc["dropped"],
            "drifting": rho < 0.5,
            "why": ("courts track humans" if rho >= 0.5 else
                    "PROXY DRIFT: the automated courts no longer track "
                    "human preference — recalibrate before trusting "
                    "another learned metric")}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="MUSHRA-LITE (w93)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("assemble")
    a1.add_argument("out_dir")
    a1.add_argument("--reference", required=True)
    a1.add_argument("candidates", nargs="+")
    a2 = sub.add_parser("report")
    a2.add_argument("trial_dir")
    a2.add_argument("--scores", required=True,
                    help="json: {source_wav_basename: court_score}")
    a = ap.parse_args()
    if a.cmd == "assemble":
        t = assemble(a.out_dir, a.candidates, a.reference)
        print(f"[mushra] {len(t['items'])} blinded items -> "
              f"{a.out_dir}/trial.html")
    else:
        trial = json.load(open(os.path.join(a.trial_dir, "trial.json")))
        rows = []
        for f in os.listdir(a.trial_dir):
            if f.startswith("ratings_") and f.endswith(".json"):
                rows.append(json.load(open(os.path.join(a.trial_dir, f))))
        print(json.dumps(proxy_report(
            rows, trial, json.load(open(a.scores))), indent=1))
