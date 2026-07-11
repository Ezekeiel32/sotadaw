#!/usr/bin/env python3
"""Build skills/registry.json: index of all skills with sha256 integrity + parsed frontmatter.
The MCP server refuses to serve a skill whose hash doesn't match (immutable-registry pattern)."""
import hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    meta, cur_key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\S.*:", line):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if val in ("", ">", "|"):
                meta[key] = [] if key in ("tags", "hard_constraints") else ""
                cur_key = key
            elif val.startswith("[") and val.endswith("]"):
                meta[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
                cur_key = None
            else:
                meta[key] = val
                cur_key = None
        elif line.strip().startswith("- ") and cur_key and isinstance(meta.get(cur_key), list):
            meta[cur_key].append(line.strip()[2:])
        elif cur_key and isinstance(meta.get(cur_key), str):
            meta[cur_key] = (meta[cur_key] + " " + line.strip()).strip()
    return meta

entries = {}
for fn in sorted(os.listdir(SKILLS)):
    if not fn.endswith(".md"):
        continue
    path = os.path.join(SKILLS, fn)
    raw = open(path, "rb").read()
    meta = parse_frontmatter(raw.decode("utf-8"))
    name = meta.get("name") or fn.split(".")[0]
    version = int(meta.get("version", 1))
    # highest version wins — lexical listdir order puts v9 AFTER v10/v11, so
    # last-wins silently pinned every >9-version skill to v9
    if name in entries and entries[name]["version"] >= version:
        continue
    entries[name] = {
        "file": fn,
        "version": version,
        "kind": meta.get("kind", ""),
        "tags": meta.get("tags", []),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }

reg = {"registry_version": 1, "skills": entries}
out = os.path.join(SKILLS, "registry.json")
json.dump(reg, open(out, "w"), indent=2)
print(f"registry: {len(entries)} skills -> {out}")
for n, e in entries.items():
    print(f"  {n}@v{e['version']}  tags={','.join(e['tags'])}  sha={e['sha256'][:12]}")
