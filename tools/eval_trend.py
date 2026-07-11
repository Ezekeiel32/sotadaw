#!/usr/bin/env python3
"""eval/history.jsonl + eval/lessons.jsonl -> eval/trend.html : the factory's
report card over time, including the measured lesson ladder per genre."""
import json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "eval", "history.jsonl")
LESSONS = os.path.join(ROOT, "eval", "lessons.jsonl")
OUT = os.path.join(ROOT, "eval", "trend.html")

rows = []
if os.path.exists(HIST):
    for line in open(HIST):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("kind") == "judge" or "score" not in r:
            continue
        rows.append(r)

by_genre = {}
for r in rows:
    by_genre.setdefault(r.get("genre", "?"), []).append(r)

html = ["<meta charset='utf-8'><title>SOTA DAW eval trend</title>",
        "<style>body{background:#0e0f12;color:#e7e9ec;font:14px system-ui;padding:24px}"
        "h1{font-size:18px} table{border-collapse:collapse;margin:12px 0}"
        "td,th{padding:4px 10px;border-bottom:1px solid #26282f;text-align:left}"
        ".good{color:#81c995}.bad{color:#e8837b}.dim{color:#9aa0a8}</style>",
        f"<h1>Eval trend - {len(rows)} runs</h1><table><tr><th>genre</th><th>runs</th>"
        "<th>scores (oldest→newest)</th><th>latest checks failing</th></tr>"]
for g in sorted(by_genre):
    rs = by_genre[g]
    scores = " → ".join(f"<span class='{'good' if r['score'] >= 0.8 else 'bad'}'>{r['score']:.2f}</span>" for r in rs)
    fails = ", ".join(k for k, v in rs[-1].get("checks", {}).items() if not v) or "<span class='good'>none</span>"
    html.append(f"<tr><td><b>{g}</b></td><td class='dim'>{len(rs)}</td><td>{scores}</td><td>{fails}</td></tr>")
html.append("</table>")

# the measured lesson ladder: advisor_cycle verdicts (kept lessons = the factory learning)
lessons = []
if os.path.exists(LESSONS):
    for line in open(LESSONS):
        try:
            lessons.append(json.loads(line))
        except json.JSONDecodeError:
            continue
if lessons:
    html.append("<h1>Lesson ladder (measured cycles)</h1><table>"
                "<tr><th>genre</th><th>pre → post</th><th>verdict</th><th>checks fixed</th></tr>")
    for l in lessons:
        v = ("<span class='good'>KEPT</span>" if l.get("kept")
             else "<span class='bad'>no gain</span>")
        html.append(f"<tr><td><b>{l.get('genre','?')}</b></td>"
                    f"<td>{l.get('pre',0):.3f} → {l.get('post',0):.3f}</td>"
                    f"<td>{v}</td><td class='dim'>{', '.join(l.get('fixed', [])) or '-'}</td></tr>")
    html.append("</table>")

html.append(f"<p class='dim'>generated {time.strftime('%Y-%m-%d %H:%M')} - "
            "red row = knowledge gap = next graph patch</p>")
open(OUT, "w").write("\n".join(html))
print(f"eval/trend.html: {len(by_genre)} genres, {len(rows)} runs, {len(lessons)} lesson verdicts")
