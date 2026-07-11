#!/usr/bin/env python3
"""Zero-token regression net for the Codex producer rail."""

import json
import os
import sys
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import codex_agent


def check(ok, message):
    if not ok:
        raise AssertionError(message)
    print("  PASS", message)


with tempfile.TemporaryDirectory(prefix="sotadaw_codex_battery_") as td:
    config = os.path.join(td, "mcp.json")
    with open(config, "w") as fh:
        json.dump({"mcpServers": {
            "daw": {"command": "/usr/bin/python3", "args": ["/repo/daw_mcp.py"]},
            "external": {"command": "/bin/external", "args": [],
                         "env": {"EXTERNAL_SECRET": "do-not-mount"}},
        }}, fh)

    command = codex_agent.build_command(
        "codex:gpt-5.6-sol", config,
        allowed_tools="mcp__daw__start_session,mcp__daw__update_track",
        binary="/opt/codex", root="/repo",
        extra_env={"SOTADAW_IPC": "/tmp/ipc"})
    joined = "\n".join(command)
    check(command[:3] == ["/opt/codex", "--ask-for-approval", "never"],
          "approval policy is top-level (installed CLI grammar)")
    check(command[-1] == "-" and "gpt-5.6-sol" in command
          and "codex:gpt-5.6-sol" not in command,
          "prompt uses stdin and provider namespace never reaches Codex")
    check("apps" in command and "shell_tool" in command
          and "read-only" in command and "--ignore-user-config" in command,
          "personal apps/config and filesystem write tools are isolated")
    check("mcp_servers.daw.enabled_tools=[\"start_session\",\"update_track\"]" in joined,
          "DAW MCP allowlist is translated to raw Codex tool names")
    check('mcp_servers.daw.default_tools_approval_mode="approve"' in joined,
          "trusted headless DAW tools are approved instead of silently canceled")
    check("mcp_servers.external.command" not in joined,
          "an ungranted external connector is not mounted")
    process_env = codex_agent.subprocess_env(
        config, "mcp__daw__start_session,mcp__daw__update_track",
        {"SOTADAW_IPC": "/tmp/ipc"})
    check('mcp_servers.daw.env_vars=["SOTADAW_IPC"]' in joined
          and "/tmp/ipc" not in joined and process_env["SOTADAW_IPC"] == "/tmp/ipc",
          "the proposal fence reaches DAW MCP without leaking its value in argv")
    check("EXTERNAL_SECRET" not in process_env,
          "an unmounted connector's environment is not exposed to Codex")
    check("model_reasoning_effort" not in joined,
          "model catalog default effort wins when the UI did not override it")

    messages, action, final, completed, failure, usage = codex_agent.event_updates({
        "type": "item.started", "item": {"type": "mcp_tool_call",
        "server": "daw", "tool": "update_track", "arguments": "{\"song\":\"x\"}"}})
    check(action == ("mcp__daw__update_track", {"song": "x"}),
          "MCP JSONL events become structured DAW actions")
    messages, action, final, completed, failure, usage = codex_agent.event_updates({
        "type": "item.completed", "item": {"type": "agent_message", "text": "Done."}})
    check(final == "Done." and messages[-1][0] == "activity",
          "final Codex message reaches the transcript")
    messages, action, final, completed, failure, usage = codex_agent.event_updates({
        "type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}})
    check(completed and usage["input_tokens"] == 10,
          "turn completion and usage are recognized")
    messages, action, final, completed, failure, usage = codex_agent.event_updates({
        "type": "item.completed", "item": {"type": "mcp_tool_call",
        "server": "daw", "tool": "start_session", "status": "failed",
        "error": {"message": "user cancelled MCP tool call"}}})
    check(failure and "start_session" in failure and "cancel" in failure.lower()
          and any(kind == "error" for kind, _ in messages),
          "headless MCP approval cancellation is a provider failure, not an empty edit")
    # A CLEAN tool completion must be silent — no status, no error. str(None)
    # once became the truthy string "None" and spammed a fake "failed" on every
    # successful tool (a real GPT take logged 13 phantom failures, 0 real).
    messages, action, final, completed, failure, usage = codex_agent.event_updates({
        "type": "item.completed", "item": {"type": "mcp_tool_call",
        "server": "daw", "tool": "add_track"}})
    check(not failure and not any(kind == "error" for kind, _ in messages),
          "a clean tool completion emits no phantom failure (no error/status)")
    messages, action, final, completed, failure, usage = codex_agent.event_updates({
        "type": "item.completed", "item": {"type": "mcp_tool_call",
        "server": "daw", "tool": "add_track", "status": "completed", "error": None}})
    check(not failure and not any(kind == "error" for kind, _ in messages),
          "an explicit completed status with error=None stays silent too")

    # The MOST LIKELY real failure (a nearly-spent GPT account) must read
    # clearly and point at the fallback, not dump a raw error.
    q = codex_agent._friendly_failure("stream error: You have hit your rate limit; "
                                      "please try again later.")
    check("QUOTA" in q and ("AUTO" in q or "Claude" in q),
          "a rate-limit/quota failure says QUOTA and points at the AUTO/Claude fallback")
    n = codex_agent._friendly_failure(
        "stream disconnected before completion: error sending request for url (chatgpt.com)")
    check("connection" in n.lower() and "retry" in n.lower(),
          "a dropped connection reads as transient with a retry hint")
    raw = codex_agent._friendly_failure("some unmapped internal error 500")
    check(raw.startswith("Codex rail failed:"),
          "an unmapped failure still falls through to the raw-but-labeled message")

    class FakeInput:
        def __init__(self): self.text = ""
        def write(self, text): self.text += text
        def close(self): pass

    class FakeProcess:
        def __init__(self):
            self.stdin = FakeInput()
            self.stdout = iter([
                json.dumps({"type": "thread.started", "thread_id": "t"}) + "\n",
                json.dumps({"type": "item.started", "item": {"type": "mcp_tool_call",
                            "server": "daw", "tool": "update_track",
                            "arguments": {"song": "x"}}}) + "\n",
                json.dumps({"type": "item.completed", "item": {"type": "agent_message",
                            "text": "Shipped."}}) + "\n",
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 20,
                            "cached_input_tokens": 5, "output_tokens": 3}}) + "\n",
            ])
            self.returncode = 0
        def wait(self, timeout=None): return self.returncode

    fake = FakeProcess()
    old_popen, old_bin = codex_agent.subprocess.Popen, codex_agent.codex_bin
    codex_agent.subprocess.Popen = lambda *args, **kwargs: fake
    codex_agent.codex_bin = lambda: "/opt/codex"
    events, actions = [], []
    try:
        result = codex_agent.run(
            "PRODUCE", "codex:gpt-5.6-sol", config,
            allowed_tools="mcp__daw__update_track",
            on_event=lambda kind, text: events.append((kind, text)),
            on_action=lambda name, args: actions.append((name, args)))
    finally:
        codex_agent.subprocess.Popen, codex_agent.codex_bin = old_popen, old_bin
    check(result["ok"] and result["final"] == "Shipped." and fake.stdin.text == "PRODUCE",
          "stream pump returns a successful final result without a paid call")
    check(actions == [("mcp__daw__update_track", {"song": "x"})]
          and any("tokens:" in text for _, text in events),
          "stream pump forwards structured actions and token usage")

    old_build = codex_agent.build_command
    codex_agent.build_command = lambda *args, **kwargs: [
        sys.executable, "-c", "import time; time.sleep(60)"]
    cancel_events = []
    try:
        canceled = codex_agent.run(
            "CANCEL", "codex:gpt-5.6-sol", config,
            allowed_tools="mcp__daw__update_track",
            on_event=lambda kind, text: cancel_events.append((kind, text)),
            cancel_check=lambda: "canceled by battery")
    finally:
        codex_agent.build_command = old_build
    check(canceled["canceled"] and not canceled["ok"]
          and ("status", "canceled by battery") in cancel_events,
          "cancel terminates and reaps the Codex/MCP process group")

    # A UI/event callback bug must not strand the authenticated Codex process.
    old_build, real_popen = codex_agent.build_command, codex_agent.subprocess.Popen
    callback_children = []
    codex_agent.build_command = lambda *args, **kwargs: [
        sys.executable, "-c",
        "import json,time; print(json.dumps({'type':'item.started','item':"
        "{'type':'mcp_tool_call','server':'daw','tool':'update_track',"
        "'arguments':{}}}),flush=True); time.sleep(60)"]
    def capture_popen(*args, **kwargs):
        child = real_popen(*args, **kwargs)
        callback_children.append(child)
        return child
    codex_agent.subprocess.Popen = capture_popen
    callback_raised = False
    try:
        codex_agent.run(
            "CALLBACK", "codex:gpt-5.6-sol", config,
            allowed_tools="mcp__daw__update_track",
            on_action=lambda name, args: (_ for _ in ()).throw(RuntimeError("UI callback")))
    except RuntimeError:
        callback_raised = True
    finally:
        codex_agent.build_command, codex_agent.subprocess.Popen = old_build, real_popen
    check(callback_raised and callback_children[0].poll() is not None,
          "callback exceptions still terminate and reap the process group")

    # Likewise, an unexpected stdout iterator failure must deliver EOF to the
    # pump, terminate the child, and return a normal failed result.
    class BrokenOutput:
        def __iter__(self): return self
        def __next__(self): raise OSError("reader broke")

    class WrappedProcess:
        def __init__(self, child):
            self.child, self.stdin, self.stdout, self.pid = (
                child, child.stdin, BrokenOutput(), child.pid)
        def poll(self): return self.child.poll()
        def wait(self, timeout=None): return self.child.wait(timeout=timeout)
        def terminate(self): return self.child.terminate()
        def kill(self): return self.child.kill()

    reader_children = []
    codex_agent.build_command = lambda *args, **kwargs: [
        sys.executable, "-c", "import time; time.sleep(60)"]
    def broken_popen(*args, **kwargs):
        child = real_popen(*args, **kwargs)
        reader_children.append(child)
        return WrappedProcess(child)
    codex_agent.subprocess.Popen = broken_popen
    reader_events = []
    try:
        reader_result = codex_agent.run(
            "READER", "codex:gpt-5.6-sol", config,
            allowed_tools="mcp__daw__update_track",
            on_event=lambda kind, text: reader_events.append((kind, text)))
    finally:
        codex_agent.build_command, codex_agent.subprocess.Popen = old_build, real_popen
    check(not reader_result["ok"] and reader_children[0].poll() is not None
          and any(kind == "error" and "reader failed" in text
                  for kind, text in reader_events),
          "stdout reader failures signal EOF and reap instead of hanging")

print("CODEX AGENT BATTERY GREEN")
