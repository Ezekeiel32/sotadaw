#!/usr/bin/env python3
"""Reference external connector (and smoke-test fixture) for THE SECOND WEDGE.

Shape of a DAW connector: an MCP stdio server exposing that DAW's verbs. This stub
stands in for ableton-mcp/reaper-mcp in tests — proves the sidecar mounts foreign
servers and the agent can call their tools alongside the daw toolset.
"""
import json, sys

TOOLS = {
    "external_status": ("Report the external DAW's status (stub: always ready).",
                        {"type": "object", "properties": {}}),
    "external_echo": ("Echo a message back from the external DAW (stub).",
                      {"type": "object", "properties": {"message": {"type": "string"}},
                       "required": ["message"]}),
}

def reply(id_, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": id_, "result": result}) + "\n")
    sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
    except json.JSONDecodeError:
        continue
    m, id_ = req.get("method"), req.get("id")
    if m == "initialize":
        reply(id_, {"protocolVersion": req["params"].get("protocolVersion", "2024-11-05"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "stub-daw-connector", "version": "0.1.0"}})
    elif m == "tools/list":
        reply(id_, {"tools": [{"name": n, "description": d, "inputSchema": s}
                              for n, (d, s) in TOOLS.items()]})
    elif m == "tools/call":
        name = req["params"]["name"]
        args = req["params"].get("arguments") or {}
        text = ("EXTERNAL DAW READY (stub connector; transport ok)" if name == "external_status"
                else f"external echo: {args.get('message', '')}" if name == "external_echo"
                else f"unknown tool {name}")
        reply(id_, {"content": [{"type": "text", "text": text}], "isError": False})
    elif m == "ping":
        reply(id_, {})
    elif id_ is not None:
        reply(id_, {})
