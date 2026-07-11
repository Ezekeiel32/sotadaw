#!/usr/bin/env python3
"""W17: THE DOCS SITE — the knowledge IS the documentation.

docs_site.py  ->  dist/docs/index.html  (one self-contained file, no deps, offline)

Generated, never hand-written: the skills registry (every version, every law), the
constitution (SPEC), the axis (HORIZON), the instrument panel (PROGRESS). Client-side
search over skills. Deterministic output for a given repo state.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dist", "docs")


def frontmatter(md):
    m = re.match(r"---\n(.*?)\n---\n(.*)", md, re.S)
    if not m:
        return {}, md
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, m.group(2)


def esc(s):
    return html.escape(str(s), quote=False)


def main():
    reg = json.load(open(os.path.join(ROOT, "skills", "registry.json")))
    entries = reg.get("skills", reg) if isinstance(reg, dict) else reg
    cards, laws = [], []
    items = entries.items() if isinstance(entries, dict) else [(e.get("name"), e) for e in entries]
    for name, meta in sorted(items):
        f = meta.get("file") or meta.get("path") or ""
        p = os.path.join(ROOT, "skills", os.path.basename(f)) if f else None
        body, fm = "", {}
        if p and os.path.exists(p):
            fm, body = frontmatter(open(p).read())
        kind = fm.get("kind", meta.get("kind", ""))
        ver = fm.get("version", meta.get("version", ""))
        tags = fm.get("tags", "")
        hard = []
        if p and os.path.exists(p):
            raw = open(p).read()
            m = re.search(r"hard_constraints:\n((?:\s+-.*\n?)+)", raw)
            if m:
                hard = re.findall(r"^\s+- (.+)$", m.group(1), re.M)
        card = (f'<div class="card" data-k="{esc(name)} {esc(kind)} {esc(tags)}">'
                f'<h3>{esc(name)} <span class="v">v{esc(ver)}</span> '
                f'<span class="k">{esc(kind)}</span></h3>'
                + (f'<ul>{"".join(f"<li>{esc(h)}</li>" for h in hard[:4])}</ul>' if hard else "")
                + (f'<details><summary>full skill</summary><pre>{esc(body[:4000])}</pre></details>'
                   if kind != "genre" else "")
                + "</div>")
        (laws if kind != "genre" else cards).append(card)

    def doc(path, title):
        p = os.path.join(ROOT, "docs", path)
        return (f'<details class="doc"><summary><b>{esc(title)}</b> <span class="k">docs/{path}'
                f'</span></summary><pre>{esc(open(p).read())}</pre></details>'
                if os.path.exists(p) else "")

    page = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SOTA DAW — the knowledge</title><style>
body{{font:15px/1.5 system-ui;margin:0;background:#0e0f12;color:#e8e6e0}}
header{{padding:28px 20px 10px;border-bottom:1px solid #26282e}}
h1{{margin:0;font-size:22px}} .sub{{color:#9a9790}}
main{{max-width:980px;margin:0 auto;padding:18px}}
input{{width:100%;padding:10px;border-radius:8px;border:1px solid #33363d;background:#17181c;color:#e8e6e0;font-size:15px}}
.card{{border:1px solid #26282e;border-radius:10px;padding:10px 14px;margin:10px 0;background:#131418}}
.card h3{{margin:2px 0;font-size:15px}} .v{{color:#7ec8a3;font-weight:400;font-size:12px}}
.k{{color:#8f8cd0;font-weight:400;font-size:12px}}
ul{{margin:6px 0 2px;padding-left:18px;color:#b9b6ae;font-size:13px}}
pre{{white-space:pre-wrap;font-size:12.5px;color:#c9c6be;overflow-x:auto}}
details.doc{{margin:10px 0;border:1px solid #26282e;border-radius:10px;padding:8px 14px;background:#131418}}
h2{{font-size:17px;margin:26px 0 6px;color:#d8d5cd}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:10px}}
.grid .card{{margin:0}}</style></head><body>
<header><h1>SOTA DAW — the knowledge</h1>
<div class="sub">generated from the repo by tools/docs_site.py — the skills registry, the
constitution, the axis. Position: see PROGRESS/HORIZON below.</div></header><main>
<h2>The constitution &amp; the axis</h2>
{doc("SPEC.md", "SPEC — the product constitution (v2.5)")}
{doc("HORIZON_100000.md", "THE HORIZON — 0.076% → 100.000%")}
{doc("PROGRESS_100.md", "MAP COVERAGE — the instrument panel")}
{doc("ROADMAP_0.080.md", "ROADMAP 0.080 — the ratified doubling")}
<h2>The laws ({len(laws)} always-on / cross-cutting skills)</h2>
{"".join(laws)}
<h2>The genres ({len(cards)} factory-born skills)</h2>
<input id="q" placeholder="search {len(cards)} genre skills… (name, tag)">
<div class="grid" id="g">{"".join(cards)}</div>
<script>
const q=document.getElementById('q'),g=document.getElementById('g');
q.addEventListener('input',()=>{{const s=q.value.toLowerCase();
for(const c of g.children)c.style.display=c.dataset.k.toLowerCase().includes(s)?'':'none';}});
</script></main></body></html>"""
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "index.html")
    open(out, "w").write(page)
    print(f"docs site: {out} ({os.path.getsize(out)//1024} KB, {len(laws)} laws + {len(cards)} genres)")


if __name__ == "__main__":
    main()
