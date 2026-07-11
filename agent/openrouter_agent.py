#!/usr/bin/env python3
"""THE OPENROUTER RAIL — any tool-calling model becomes the DAW's producer.

First citizen: x-ai/grok-4.3 (verified on OpenRouter /models 2026-07-05:
tools=true, 1M context, $1.25/M prompt). The rail is model-agnostic: pass any
OpenRouter id whose model can call tools (grok-4.20, gemini, qwen, ...).

Design: IN-PROCESS tool loop — daw_mcp.TOOLS (name -> fn, desc, schema) becomes
OpenAI-format tool schemas; the model's tool_calls dispatch straight to the
python functions. No MCP transport, no proxy, no claude CLI on this path.
stdlib-only (urllib); OPENROUTER_API_KEY from the environment.

    from openrouter_agent import run
    run(prompt, "x-ai/grok-4.3", on_event=lambda kind, text: ..., max_turns=30)
    -> final assistant text (str) or None on hard failure.
"""
import importlib.util, json, os, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://openrouter.ai/api/v1/chat/completions"
TOOL_RESULT_CAP = 300_000        # chars per tool result (~75k tokens) — the
                                 # large-song guard; the marker tells the model
                                 # to reach for scoped gets instead

_daw = None
def _tools_module():
    global _daw
    if _daw is None:
        spec = importlib.util.spec_from_file_location(
            "daw_mcp", os.path.join(ROOT, "agent", "daw_mcp.py"))
        _daw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_daw)
    return _daw


def openai_tools():
    """daw_mcp.TOOLS -> OpenAI/OpenRouter function-calling schemas."""
    out = []
    for name, entry in _tools_module().TOOLS.items():
        fn, desc, schema = entry[0], entry[1], (entry[2] if len(entry) > 2 else
                                                {"type": "object", "properties": {}})
        out.append({"type": "function",
                    "function": {"name": name, "description": desc[:1024],
                                 "parameters": schema}})
    return out


def _post(payload, key, timeout=300):
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://sota-daw.local", "X-Title": "SOTA DAW"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 502, 503) and attempt < 2:
                time.sleep(4 * (attempt + 1))
                continue
            raise RuntimeError(f"openrouter HTTP {e.code}: {body}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 2:
                time.sleep(4 * (attempt + 1))
                continue
            raise RuntimeError(f"openrouter unreachable: {e}")


def _key():
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if k:
        return k
    byok = os.path.join(ROOT, "agent", ".byok")     # the in-app BYOK box (Agent
    if os.path.exists(byok):                        # menu) — sk-or-* lines are ours
        for line in open(byok).read().split():
            if line.startswith("sk-or-"):
                return line
    return ""


def run(prompt, model, on_event=lambda kind, text: None, max_turns=30):
    key = _key()
    if not key:
        on_event("error", "OPENROUTER RAIL BLOCKED: paste an OpenRouter key "
                          "(sk-or-..., from openrouter.ai/keys) into Agent -> API "
                          "Key (BYOK) — same box as the Anthropic key, one key per "
                          "line, both can live there. The claude rail still works "
                          "without it.")
        return None
    daw = _tools_module()
    tools = openai_tools()
    msgs = [{"role": "system", "content": prompt},
            {"role": "user", "content": "Begin. Do the work with your tools, then "
                                        "finish with the required bullets."}]
    in_tok = out_tok = calls = 0
    for turn in range(int(max_turns)):
        on_event("activity", f"{model.split('/')[-1]}: thinking (turn {turn + 1})…")
        try:
            resp = _post({"model": model, "messages": msgs, "tools": tools,
                          "tool_choice": "auto", "max_tokens": 16000}, key)
        except RuntimeError as e:
            on_event("error", str(e))
            return None
        u = resp.get("usage") or {}
        in_tok += u.get("prompt_tokens", 0); out_tok += u.get("completion_tokens", 0)
        choice = (resp.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        tcs = msg.get("tool_calls") or []
        msgs.append({"role": "assistant",
                     "content": msg.get("content") or "",
                     **({"tool_calls": tcs} if tcs else {})})
        if not tcs:
            on_event("activity", f"cost: ~{(in_tok + out_tok) / 1000:.0f}k tokens "
                                 f"({in_tok / 1000:.0f}k in / {out_tok / 1000:.0f}k out) "
                                 f"· {calls} tool calls · openrouter/{model}")
            return msg.get("content") or ""
        for tc in tcs:
            fname = tc.get("function", {}).get("name", "?")
            try:
                args = json.loads(tc.get("function", {}).get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            on_event("activity", f"{fname} {json.dumps(args)[:120]}")
            entry = daw.TOOLS.get(fname)
            if entry is None:
                result = f"unknown tool: {fname}"
            else:
                try:
                    result = str(entry[0](args))
                except Exception as e:
                    result = f"TOOL ERROR ({fname}): {type(e).__name__}: {e}"
            calls += 1
            if len(result) > TOOL_RESULT_CAP:
                result = (result[:TOOL_RESULT_CAP]
                          + f"\n[TRUNCATED {len(result) - TOOL_RESULT_CAP} chars — "
                            "this song is large: prefer scoped reads/edits "
                            "(duplicate_bars/clear_bars/update_track on one track).]")
            msgs.append({"role": "tool", "tool_call_id": tc.get("id", fname),
                         "content": result})
    on_event("status", f"openrouter rail hit max turns ({max_turns}) — salvage check runs")
    return ""


if __name__ == "__main__":
    # smoke: schema build + (with key) a 1-turn hello
    ts = openai_tools()
    print(f"[openrouter_agent] {len(ts)} tool schemas built, json-clean:",
          bool(json.dumps(ts)))
    if os.environ.get("OPENROUTER_API_KEY"):
        out = run("You are a test. Reply with the word READY and nothing else. "
                  "Do not call tools.", sys.argv[1] if len(sys.argv) > 1 else "x-ai/grok-4.3",
                  on_event=lambda k, t: print(f"  [{k}] {t}"), max_turns=2)
        print("[openrouter_agent] reply:", (out or "")[:80])
    else:
        print("[openrouter_agent] no OPENROUTER_API_KEY — network smoke skipped")
