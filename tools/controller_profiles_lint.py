#!/usr/bin/env python3
"""Schema lint for agent/controller_profiles.json (pure, no UI needed)."""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "agent", "controller_profiles.json")))
vocab = set(d["actions_vocabulary"])
ids = set(); errs = []
for p in d["profiles"]:
    if p["id"] in ids: errs.append(f"dup id {p['id']}")
    ids.add(p["id"])
    try: re.compile(p["match"])
    except re.error as e: errs.append(f"{p['id']}: bad regex ({e})")
    if not p.get("provenance"): errs.append(f"{p['id']}: NO PROVENANCE")
    for c in p["controls"]:
        if c["type"] not in ("cc", "note"): errs.append(f"{p['id']}/{c['name']}: type")
        if not (0 <= c["ch"] <= 16): errs.append(f"{p['id']}/{c['name']}: ch {c['ch']}")
        for k in ("num", "num_hi"):
            if k in c and not (0 <= c[k] <= 127): errs.append(f"{p['id']}/{c['name']}: {k}")
        if c["action"] not in vocab: errs.append(f"{p['id']}/{c['name']}: action '{c['action']}' not in vocabulary")
if errs:
    print("LINT FAIL:"); [print(" ", e) for e in errs]; sys.exit(1)
n = sum(len(p["controls"]) for p in d["profiles"])
print(f"controller profiles LINT CLEAN: {len(d['profiles'])} profiles, {n} controls, all actions in vocabulary")
