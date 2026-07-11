#!/usr/bin/env python3
"""THE KNOWLEDGE GRAPH — FalkorDB substrate of the skills factory (SPEC S6-V33).

Graph 'sotadaw' on localhost:6380 (docker container `sotadaw-kg`, volume kg/data).

Schema v1 (provenance REQUIRED on every node):
  nodes: Genre, Technique, PatternArchetype, SoundRecipe, MixTarget, SkillDoc,
         Groove, Reference (R2: an imported record's production DNA, sha1-keyed)
  edges: SUBGENRE_OF, USES_TECHNIQUE{weight}, CHARACTERIZED_BY, TARGETS,
         DERIVED_FROM{citation}, COMPILED_INTO, COMPOSES_WITH, CONFLICTS_WITH,
         HAS_GROOVE, SOUNDS_LIKE{weight} (Reference -> nearest MixTarget Genre)

  kg.py stats            node/edge counts by label
  kg.py genre <name>     everything the graph knows about a genre (what the compiler sees)
  kg.py reference <name> a stored Reference's DNA + its edges
  kg.py query "<cypher>" raw cypher
"""
import json, sys

HOST, PORT, GRAPH = "127.0.0.1", 6380, "sotadaw"

def connect():
    from falkordb import FalkorDB
    return FalkorDB(host=HOST, port=PORT).select_graph(GRAPH)

def esc(s):
    return str(s).replace("\\", "\\\\").replace("'", "\\'")

DRUM_ZONE_VOICES = ("kick", "snare", "hat", "openhat", "clap", "rim", "ride",
                    "tom", "cymbal", "shaker", "crash")

def eligible_recipe_voice(v):
    """A SoundRecipe voice eligible to carry a genre's melodic COLOR lane.
    THE TASTE LAW (worldclass ledger + census 2026-07-12): genres carry many
    recipes including drum-ZONE recipes (snare_zones, hat_zones...) and the
    first-non-null pick handed boombap's chord lane a SNARE, ukgarage's a HAT,
    hard_techno's a KICK — pitchless drums playing "chords" is the off-putting
    sound Chezy flagged live. Pitched percussion (log_drum, marimba) stays
    eligible: amapiano's log drum IS its melody. vst3 voices pass (installed
    check happens downstream in resolve_color_source)."""
    if not v or not isinstance(v, str):
        return False
    base = (v[5:] if v.startswith("vst3:") else v).lower()
    return not any(base == d or base.startswith(d + "_") for d in DRUM_ZONE_VOICES)

def props(d):
    parts = []
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, (int, float)):
            parts.append(f"{k}: {v}")
        elif isinstance(v, (list, tuple)):
            parts.append(f"{k}: [" + ", ".join(f"'{esc(x)}'" for x in v) + "]")
        else:
            parts.append(f"{k}: '{esc(v)}'")
    return "{" + ", ".join(parts) + "}"

class KG:
    def __init__(self):
        self.g = connect()

    def upsert(self, label, name, provenance, **attrs):
        assert provenance, f"provenance required for {label}:{name} (SPEC S6 law)"
        attrs = {k: v for k, v in attrs.items() if v is not None}
        sets = ", ".join(f"n.{k} = {json.dumps(v) if not isinstance(v, str) else chr(39)+esc(v)+chr(39)}"
                         for k, v in attrs.items())
        q = (f"MERGE (n:{label} {{name: '{esc(name)}'}}) "
             f"SET n.provenance = '{esc(provenance)}'" + (", " + sets if sets else ""))
        self.g.query(q)

    def link(self, a_label, a, rel, b_label, b, **attrs):
        q = (f"MATCH (a:{a_label} {{name: '{esc(a)}'}}), (b:{b_label} {{name: '{esc(b)}'}}) "
             f"MERGE (a)-[r:{rel}]->(b)")
        if attrs:
            q += " SET " + ", ".join(
                f"r.{k} = {json.dumps(v) if not isinstance(v, str) else chr(39)+esc(v)+chr(39)}"
                for k, v in attrs.items())
        self.g.query(q)

    def q(self, cypher):
        return self.g.query(cypher).result_set

    # ---- R2 THE REFERENCE CIRCLE: imported records feed the graph ----
    def ensure_reference(self, name, source_file_hash, provenance, **attrs):
        """(:Reference) keyed by the SOURCE FILE sha1 — importing the same
        record twice lands on the same node (idempotent MERGE). name is a
        display property, never the key (two sessions can import one file
        under different song names)."""
        assert provenance, f"provenance required for Reference:{name} (SPEC S6 law)"
        assert source_file_hash, "source_file_hash is the Reference key"
        attrs = {k: v for k, v in attrs.items() if v is not None}
        attrs["name"], attrs["provenance"] = name, provenance
        sets = ", ".join(
            f"n.{k} = {json.dumps(v) if not isinstance(v, str) else chr(39)+esc(v)+chr(39)}"
            for k, v in attrs.items())
        self.g.query(f"MERGE (n:Reference {{source_file_hash: "
                     f"'{esc(source_file_hash)}'}}) SET {sets}")

    def link_reference(self, source_file_hash, rel, b_label, b, **attrs):
        """Edge from a Reference (matched by its hash key, not name)."""
        q = (f"MATCH (a:Reference {{source_file_hash: '{esc(source_file_hash)}'}}), "
             f"(b:{b_label} {{name: '{esc(b)}'}}) MERGE (a)-[r:{rel}]->(b)")
        if attrs:
            q += " SET " + ", ".join(
                f"r.{k} = {json.dumps(v) if not isinstance(v, str) else chr(39)+esc(v)+chr(39)}"
                for k, v in attrs.items())
        self.g.query(q)

    def nearest_genre_by_mix(self, lufs, band_pct):
        """(genre, weight 0..1) whose MixTarget sits closest to a measured mix:
        lufs distance in window-halfwidth units + band-order misses (3 each)
        + floor misses (2 each). None when the graph has no MixTargets."""
        rows = self.q("MATCH (g:Genre)-[:TARGETS]->(m:MixTarget) "
                      "RETURN g.name, properties(m)")
        short = {"low": "low_20_120", "lowmid": "lowmid_120_500", "mid": "mid_500_2k"}
        best = None
        for gname, m in rows:
            d = 0.0
            lo, hi = m.get("lufs_lo"), m.get("lufs_hi")
            if lo is not None and hi is not None and lufs is not None:
                d += abs(lufs - (lo + hi) / 2.0) / max(1.0, (hi - lo) / 2.0)
            names = [n for n in str(m.get("band_order") or "").split(">") if n in short]
            if len(names) >= 2 and band_pct:
                vals = [band_pct.get(short[n], 0.0) for n in names]
                d += 3.0 * sum(1 for i in range(len(vals) - 1) if vals[i] <= vals[i + 1])
            for fk, band in (("mid_floor_pct", "mid_500_2k"),
                             ("himid_floor_pct", "himid_2k_6k")):
                if m.get(fk) is not None and band_pct \
                        and band_pct.get(band, 0.0) < m[fk]:
                    d += 2.0
            if best is None or d < best[1]:
                best = (gname, d)
        return (best[0], round(1.0 / (1.0 + best[1]), 3)) if best else None

    def reference_view(self, name_or_hash):
        """A stored Reference's props + its SOUNDS_LIKE / HAS_GROOVE edges."""
        r = self.q(f"MATCH (n:Reference) WHERE n.name = '{esc(name_or_hash)}' "
                   f"OR n.source_file_hash STARTS WITH '{esc(name_or_hash)}' "
                   f"RETURN properties(n) LIMIT 1")
        if not r:
            return None
        out = dict(r[0][0])
        h = esc(out.get("source_file_hash", ""))
        out["sounds_like"] = [
            {"genre": x[0], "weight": x[1]} for x in
            self.q(f"MATCH (n:Reference {{source_file_hash: '{h}'}})"
                   f"-[s:SOUNDS_LIKE]->(g:Genre) RETURN g.name, s.weight")]
        out["grooves"] = [x[0] for x in
                          self.q(f"MATCH (n:Reference {{source_file_hash: '{h}'}})"
                                 f"-[:HAS_GROOVE]->(gr:Groove) RETURN gr.name")]
        return out

    # ---- the queries the skill compiler runs ----
    def genre_view(self, genre):
        """Everything the compiler needs to draft a skill for a genre."""
        out = {"genre": genre}
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}}) RETURN properties(g)")
        if not r:
            return None
        out["props"] = r[0][0]
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:SUBGENRE_OF]->(p:Genre) RETURN p.name")
        out["parents"] = [x[0] for x in r]
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[u:USES_TECHNIQUE]->(t:Technique) "
                   f"RETURN t.name, properties(t), u.weight ORDER BY u.weight DESC")
        out["techniques"] = [{"name": x[0], **(x[1] or {}), "weight": x[2]} for x in r]
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
                   f"RETURN p.name, properties(p)")
        out["patterns"] = [{"name": x[0], **(x[1] or {})} for x in r]
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:CHARACTERIZED_BY]->(s:SoundRecipe) "
                   f"RETURN s.name, properties(s)")
        out["sounds"] = [{"name": x[0], **(x[1] or {})} for x in r]
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:TARGETS]->(m:MixTarget) RETURN properties(m)")
        out["mixtargets"] = [x[0] for x in r]
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:HAS_GROOVE]->(gr:Groove) "
                   f"RETURN gr.name, properties(gr)")
        out["grooves"] = [{"name": x[0], **(x[1] or {})} for x in r]
        if not out["grooves"]:   # inherit the parent's feel one hop (like techniques below)
            r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:SUBGENRE_OF]->(:Genre)"
                       f"-[:HAS_GROOVE]->(gr:Groove) RETURN gr.name, properties(gr)")
            out["grooves"] = [{"name": x[0], **(x[1] or {}), "inherited": True} for x in r]
        # inherited techniques from parent genres (one hop)
        r = self.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})-[:SUBGENRE_OF]->(:Genre)"
                   f"-[u:USES_TECHNIQUE]->(t:Technique) RETURN t.name, properties(t), u.weight")
        out["inherited_techniques"] = [{"name": x[0], **(x[1] or {}), "weight": x[2]} for x in r]
        return out

    def stats(self):
        out = {}
        for lbl in ("Genre", "Technique", "PatternArchetype", "SoundRecipe",
                    "MixTarget", "SkillDoc", "Groove", "Reference"):
            out[lbl] = self.q(f"MATCH (n:{lbl}) RETURN count(n)")[0][0]
        out["edges"] = self.q("MATCH ()-[r]->() RETURN count(r)")[0][0]
        return out

if __name__ == "__main__":
    kg = KG()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "stats":
        print(json.dumps(kg.stats(), indent=1))
    elif cmd == "genre" and len(sys.argv) > 2:
        print(json.dumps(kg.genre_view(sys.argv[2]), indent=1))
    elif cmd == "reference" and len(sys.argv) > 2:
        print(json.dumps(kg.reference_view(sys.argv[2]), indent=1))
    elif cmd == "query" and len(sys.argv) > 2:
        print(json.dumps(kg.q(sys.argv[2]), indent=1, default=str))
