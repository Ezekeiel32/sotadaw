#!/usr/bin/env python3
"""THE SKILL COMPILER — knowledge graph -> skill.md (SPEC S6-V35).

  skill_compiler.py <genre>            draft skills/<genre>-arrangement.v<N>.md from the graph
  skill_compiler.py <genre> --publish  also rebuild the registry (skills_build.py)

Deterministic compilation: the graph is the source of truth; the output is a normal
versioned skill (same format as hand-written ones). Provenance flows: every fact in
the skill cites the node's provenance; the SkillDoc node + COMPILED_INTO edges land
back in the graph. Existing skill of same name -> version bumps (immutability law).
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")

def next_version(base):
    versions = [int(m.group(1)) for f in os.listdir(SKILLS)
                if (m := re.match(rf"{re.escape(base)}\.v(\d+)\.md$", f))]
    return max(versions, default=0) + 1

# TASTE CORRECTIONS: verdict-weighted complaint buckets (kg_ingest_telemetry v2)
# become skill guidance. One-off complaints are noise; the user's words ride verbatim.
CORRECTIONS = {
    "bright": "bias DARKER: lower lead octaves, cap filter cutoffs on leads, gentler high shelves; check himid share before shipping",
    "dark":   "bias BRIGHTER/CLEARER: open the filters, add lead presence (2-6kHz), trim the mud band (200-400Hz)",
    "groove": "the FEEL failed: apply the genre's NAMED groove profile (never uniform swing), keep kick anchors, humanize velocities",
    "busy":   "THIN the arrangement: fewer simultaneous voices per section, carve space (rest a layer every 8 bars), shorter tails",
    "empty":  "ADD motion: a counter-voice or arp, real density contrast between sections, fills at the turnarounds",
    "level":  "staging: reach the LUFS window with fx_trim INTO the wall, never masterGainDb; fix hot/cold track gains first",
    "vibe":   "identity miss: re-read the TOP techniques above and follow the pocket + palette LITERALLY before any creative drift",
}

def taste_section(props):
    comp = str(props.get("complaints") or "")
    if not comp:
        return []
    counts = {}
    for part in comp.split(";"):
        if ":" in part:
            k, _, n = part.partition(":")
            try:
                counts[k] = int(n)
            except ValueError:
                pass
    total = sum(counts.values())
    if total < 2:
        return []                    # a single complaint is noise, not taste
    lines = ["", "## TASTE CORRECTIONS (this user's verdicts — they outrank defaults)"]
    for k, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if k in CORRECTIONS and (n >= 2 or n / total >= 0.4):
            lines.append(f"- rejected {n}x as '{k}': {CORRECTIONS[k]}")
    whys = str(props.get("last_whys") or "")
    if len(lines) > 2 and whys:
        lines.append(f"- their words, verbatim: \"{whys}\"")
    return lines if len(lines) > 2 else []

def compile_genre(genre, publish=False):
    kg = KG()
    v = kg.genre_view(genre)
    if v is None:
        raise SystemExit(f"genre '{genre}' not in the graph — seed it first (kg_seed.py or curation)")
    if not v["techniques"]:
        raise SystemExit(f"genre '{genre}' has no USES_TECHNIQUE edges — nothing to compile")

    props = v["props"]
    mt = v["mixtargets"][0] if v["mixtargets"] else {}
    base = f"{genre}-arrangement"
    version = next_version(base)
    parents = v["parents"]
    # constraints = top-3 UNION any technique curated as LAW (weight >= 0.9):
    # the relative rule keeps skills tight; the absolute rule stops promotions
    # from evicting genre-defining techniques (the W19m displacement audit).
    techs = v["techniques"]
    top = list(techs[:3])
    for t in techs[3:]:
        w = t.get("weight")
        if w is not None and float(w) >= 0.9:
            top.append(t)

    hard = [
        f"BPM {props.get('bpm_lo','?')}-{props.get('bpm_hi','?')}; set the song key (suggested: {props.get('common_key','minor')}).",
        f"Mix: clipped_samples == {mt.get('clipped_samples', 0)}, LUFS {mt.get('lufs_lo','-18')}..{mt.get('lufs_hi','-9')}, band order {mt.get('band_order','low>mid>high')}.",
    ]
    if props.get("harmony_ext"):    # taste wave 1: documented extended-chord practice
        hard.append(f"Harmony: {props['harmony_ext']}.")
    for t in top:
        hard.append(f"{t['name'].replace('_',' ').upper()} is non-negotiable: {t['desc']}")
    # conflicts reachable from this genre's techniques
    conflicts = kg.q(
        f"MATCH (g:Genre {{name: '{genre}'}})-[:USES_TECHNIQUE]->(t:Technique)"
        f"<-[:CONFLICTS_WITH]-(bad:Technique) RETURN DISTINCT bad.name, bad.desc")
    for c in conflicts:
        hard.append(f"FORBIDDEN: {c[0].replace('_',' ')} — {c[1]}")

    lines = ["---",
             f"name: {base}",
             f"version: {version}",
             "kind: genre",
             f"tags: [{', '.join([genre] + parents + ['arrangement'])}]",
             "compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)",
             "hard_constraints:"]
    lines += [f"  - {h}" for h in hard]
    lines += ["---",
              f"# {genre.title()} arrangement (graph-compiled)",
              ""]
    if parents:
        lines += [f"{genre.title()} is a child of **{', '.join(parents)}** — its groove laws apply "
                  f"unless overridden below.", ""]
    for p in v["patterns"]:
        pocket_extra = ""
        try:
            _g = json.loads(p.get("grid") or "{}")
            if abs(float(_g.get("swing", 0.5)) - 0.5) > 0.005:
                pocket_extra = (f" Swing {_g['swing']} rides the {_g.get('swing_grid', '16th')} grid"
                                f" — keep swing.grid matched to where the hats live.")
        except Exception:
            pass
        lines += [f"## The pocket — {p['name']}",
                  f"{p.get('desc','')}{pocket_extra}  *(source: {p.get('provenance','?')})*", ""]
    lines += ["## Techniques (weight order — the top ones DEFINE the genre)"]
    for t in v["techniques"]:
        lines += [f"- **{t['name'].replace('_',' ')}** (w{t.get('weight','?')}): {t.get('desc','')} "
                  f"*({t.get('provenance','?')})*"]
    if v["inherited_techniques"]:
        lines += ["", f"## Inherited from {', '.join(parents)}"]
        seen = {t["name"] for t in v["techniques"]}
        for t in v["inherited_techniques"]:
            if t["name"] not in seen:
                lines += [f"- {t['name'].replace('_',' ')}: {t.get('desc','')}"]
    if v["sounds"]:
        lines += ["", "## Sound recipes (this palette, these moves)"]
        for s_ in v["sounds"]:
            lines += [f"- **{s_['name'].replace('_',' ')}**: {s_.get('desc','')}"]
    if v.get("grooves"):
        lines += ["", "## The groove (timing DNA — apply it, don't fake it)"]
        for gr in v["grooves"]:
            lines += [f"- PREFER apply_groove(track='drums'-like tracks, name='{gr['name']}', amount 0.8-1.0) "
                      f"OVER the global swing object: swing{{}} is a uniform shuffle, the named profile "
                      f"carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid "
                      f"notes first, then apply. *({gr.get('provenance','')})*"]
    lines += taste_section(props)
    lines += ["", "## Verify (the ears will check)",
              f"After render: analyze_wav must show clipped_samples {mt.get('clipped_samples',0)}, "
              f"LUFS in {mt.get('lufs_lo','?')}..{mt.get('lufs_hi','?')}, "
              f"band order {mt.get('band_order','?')}. "
              "If a filter build was used, centroid_by_quarter must RISE into the drop.", ""]

    out_path = os.path.join(SKILLS, f"{base}.v{version}.md")
    open(out_path, "w").write("\n".join(lines))

    kg.upsert("SkillDoc", f"{base}@v{version}", "tools/skill_compiler.py",
              file=os.path.basename(out_path))
    kg.link("Genre", genre, "COMPILED_INTO", "SkillDoc", f"{base}@v{version}")

    print(f"compiled -> skills/{base}.v{version}.md ({len(v['techniques'])} techniques, "
          f"{len(v['sounds'])} sound recipes, {len(hard)} hard constraints)")
    if publish:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "skills_build.py")],
                           capture_output=True, text=True, cwd=ROOT)
        print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:])
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: skill_compiler.py <genre> [--publish]")
    compile_genre(sys.argv[1], "--publish" in sys.argv)
