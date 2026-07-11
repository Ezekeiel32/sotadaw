#!/usr/bin/env python3
"""Codex CLI rail for the in-app DAW producer.

The user's saved Codex login pays for inference; the DAW supplies only its MCP
servers and prompt.  The command deliberately ignores personal Codex config,
apps, rules, and shell tools so a model pick cannot inherit unrelated tools or
an unsupported global reasoning effort.  Codex's own filesystem tools run in a
read-only sandbox; the explicitly mounted DAW MCP server remains the sole write
surface (local MCP processes execute outside the Codex command sandbox).

``run`` is intentionally stdlib-only and exposes small pure helpers so the
provider can be regression-tested without spending tokens or touching a song.
"""

import json
import os
import queue
import re
import shutil
import signal
import subprocess
import threading
import time


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODEX_PREFIX = "codex:"


def is_codex_model(model):
    return str(model or "").startswith(CODEX_PREFIX)


def model_slug(model):
    value = str(model or "").strip()
    return value[len(CODEX_PREFIX):] if value.startswith(CODEX_PREFIX) else value


def codex_bin():
    """Resolve Codex even when the desktop app did not inherit ~/.local/bin."""
    found = shutil.which("codex")
    if found:
        return found
    for candidate in (os.path.expanduser("~/.local/bin/codex"),
                      "/usr/local/bin/codex", "/usr/bin/codex"):
        if os.path.exists(candidate):
            return candidate
    return None


def _toml(value):
    """Encode the scalar/list/map subset used by Codex's ``-c key=value``."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_toml(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(str(k)) + "=" + _toml(v)
                               for k, v in value.items()) + "}"
    return json.dumps(str(value))


def _allowed_by_server(allowed_tools):
    """Claude-style MCP names -> Codex's per-server raw tool allowlists.

    ``mcp__server`` means the whole server.  ``mcp__server__tool`` means one
    raw MCP tool.  Returning ``None`` for a server means no filter.
    """
    out = {}
    for token in str(allowed_tools or "").split(","):
        token = token.strip()
        if not token.startswith("mcp__"):
            continue
        parts = token.split("__", 2)
        if len(parts) < 2 or not parts[1]:
            continue
        server = parts[1]
        if len(parts) == 2:
            out[server] = None
        elif out.get(server, []) is not None:
            out.setdefault(server, []).append(parts[2])
    return out


def mcp_config_args(mcp_config, allowed_tools="", extra_env=None):
    """Translate Claude's mcp.json shape to repeatable Codex CLI overrides."""
    data = json.load(open(mcp_config))
    allowed = _allowed_by_server(allowed_tools)
    args = []
    for name, raw in (data.get("mcpServers") or {}).items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+", str(name)):
            continue
        if allowed_tools and name not in allowed:
            continue                         # ungranted connector stays unmounted
        spec = dict(raw or {})
        command = spec.get("command")
        if not command:
            continue
        prefix = f"mcp_servers.{name}."
        fields = {
            "command": command,
            "args": list(spec.get("args") or []),
            "required": True,
            # `codex exec` has no interactive approval handler.  Without this,
            # unannotated MCP calls complete as "user cancelled MCP tool call"
            # even under top-level --ask-for-approval never.  Every mounted
            # server/tool has already crossed the DAW's explicit allowlist.
            "default_tools_approval_mode": "approve",
            "startup_timeout_sec": 30,
            "tool_timeout_sec": 600,
        }
        if spec.get("cwd"):
            fields["cwd"] = spec["cwd"]
        env = dict(spec.get("env") or {})
        if name == "daw" and extra_env:
            env.update({str(k): str(v) for k, v in extra_env.items()
                        if v is not None})
        if env:
            # Values ride the spawned Codex environment, never argv/`ps`.
            fields["env_vars"] = sorted(env)
        if name in allowed and allowed[name] is not None:
            fields["enabled_tools"] = sorted(set(allowed[name]))
        for key, value in fields.items():
            args += ["-c", prefix + key + "=" + _toml(value)]
    return args


def subprocess_env(mcp_config, allowed_tools="", extra_env=None):
    """Environment for Codex, including MCP literals kept out of argv."""
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)        # provider-local BYOK never crosses rails
    env.pop("OPENROUTER_API_KEY", None)
    data = json.load(open(mcp_config))
    allowed = _allowed_by_server(allowed_tools)
    for name, raw in (data.get("mcpServers") or {}).items():
        if allowed_tools and name not in allowed:
            continue
        for key, value in ((raw or {}).get("env") or {}).items():
            env[str(key)] = str(value)
        if name == "daw" and extra_env:
            env.update({str(k): str(v) for k, v in extra_env.items()
                        if v is not None})
    return env


def build_command(model, mcp_config, allowed_tools="", effort=None,
                  root=ROOT, binary=None, extra_env=None):
    """Build one isolated, non-interactive Codex producer invocation."""
    binary = binary or codex_bin()
    if not binary:
        return None
    slug = model_slug(model)
    if not slug:
        raise ValueError("empty Codex model")
    cmd = [binary,
           "--ask-for-approval", "never",
           "--disable", "apps",
           "--disable", "shell_tool",
           "--disable", "skill_mcp_dependency_install",
           "exec", "--json", "--ephemeral", "--ignore-user-config",
           "--ignore-rules", "--strict-config",
           "--model", slug, "--sandbox", "read-only", "--cd", root,
           "-c", "project_doc_max_bytes=0"]
    if effort:
        cmd += ["-c", "model_reasoning_effort=" + _toml(effort)]
    cmd += mcp_config_args(mcp_config, allowed_tools, extra_env=extra_env)
    cmd.append("-")                         # prompt comes only from stdin
    return cmd


def event_updates(event):
    """Normalize one Codex JSONL event.

    Returns ``(messages, action, final, completed, failure, usage)``.  Messages
    are ``(kind, text)`` pairs; action is ``(qualified_name, arguments)``.
    """
    messages, action, final = [], None, None
    completed, failure, usage = False, None, None
    etype = event.get("type", "")
    item = event.get("item") or {}
    itype = item.get("type", "")
    if etype in ("item.started", "item.completed"):
        if itype == "mcp_tool_call":
            server = str(item.get("server") or item.get("server_name") or "daw")
            tool = str(item.get("tool") or item.get("name") or "tool")
            if etype == "item.started":
                raw_args = item.get("arguments", item.get("args", {}))
                if isinstance(raw_args, str):
                    try:
                        raw_args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        raw_args = {}
                if not isinstance(raw_args, dict):
                    raw_args = {}
                qualified = tool if tool.startswith("mcp__") else f"mcp__{server}__{tool}"
                action = (qualified, raw_args)
            elif etype == "item.completed":
                status = str(item.get("status") or "").lower()
                raw_error = item.get("error")
                # A clean completion carries no error; str(None) would become the
                # truthy string "None" and spam a false "failed" on EVERY tool
                # (caught live: a real GPT take logged 13 fake failures, 0 real).
                if isinstance(raw_error, dict):
                    detail = str(raw_error.get("message") or "").strip()
                elif raw_error:
                    detail = str(raw_error).strip()
                else:
                    detail = ""
                failed = status in ("failed", "declined", "cancelled", "canceled")
                if failed or detail:
                    detail = detail or f"tool status: {status or 'failed'}"
                    label = f"Codex MCP tool {server}.{tool} failed: {detail}"
                    messages.append(("error", label[:1200]))
                    # Approval cancellation in headless exec is structural: the
                    # model cannot recover by retrying the same tool this turn.
                    low = detail.lower()
                    if "cancel" in low or "approval" in low or "declin" in low:
                        failure = label
        elif itype == "agent_message" and etype == "item.completed":
            text = str(item.get("text") or "").strip()
            if text:
                final = text
                messages.append(("activity", "codex: " + text[:4000]))
        elif itype == "reasoning" and etype == "item.completed":
            text = str(item.get("text") or item.get("summary") or "").strip()
            if text:
                messages.append(("activity", "codex: " + text[:1000]))
        elif itype == "command_execution":
            command = str(item.get("command") or "").strip()
            if command:
                messages.append(("activity", "codex command (read-only): " + command[:240]))
        elif itype == "file_change" and etype == "item.completed":
            messages.append(("activity", "codex reported a file change"))
        elif itype == "error" and etype == "item.completed":
            msg = str(item.get("message") or "Codex item failed")
            messages.append(("activity", "codex: " + msg[:1000]))
    elif etype == "turn.completed":
        completed, usage = True, event.get("usage") or {}
    elif etype == "turn.failed":
        err = event.get("error") or {}
        failure = str(err.get("message") if isinstance(err, dict) else err)
    elif etype == "error":
        # Most error events are retry notices.  The terminal turn.failed event is
        # the one that flips the run to failure; show retries as activity only.
        msg = str(event.get("message") or "Codex error")
        messages.append(("activity", "codex: " + msg[:1000]))
    return messages, action, final, completed, failure, usage


def _kill_tree(proc):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=2)
        return
    except Exception:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
    try:
        proc.wait(timeout=2)                 # reap; no Codex/MCP zombies
    except Exception:
        pass


def _friendly_failure(text):
    low = str(text or "").lower()
    if "mcp tool" in low and ("cancel" in low or "approval" in low or "declin" in low):
        return ("CODEX TOOL BLOCKED: Codex canceled a DAW tool before it ran. "
                "The trusted headless MCP approval policy is missing or unsupported.")
    if any(word in low for word in ("not logged in", "authentication", "unauthorized",
                                    "login required", "missing auth")):
        return ("CODEX RAIL BLOCKED: run 'codex login' in a terminal, then retry. "
                "The GPT entries use your saved Codex/ChatGPT login.")
    if "user namespace" in low or "bubblewrap" in low or "bwrap" in low:
        return ("CODEX SANDBOX BLOCKED: bubblewrap could not create its user namespace. "
                "Reload the codex/codex-bwrap AppArmor profiles and retry.")
    if (any(w in low for w in ("rate limit", "rate-limit", "usage limit", "quota",
                               "too many requests", "429", "insufficient_quota"))
            or ("limit" in low and ("reset" in low or "reached" in low))):
        return ("CODEX QUOTA REACHED: your GPT/Codex usage limit is spent for now "
                "(it resets on OpenAI's schedule — check 'codex' /status). Switch the "
                "model selector to AUTO or a Claude pick to keep producing.")
    if any(w in low for w in ("stream disconnected", "connection", "timed out", "timeout",
                              "network", "sending request", "temporarily")):
        return ("CODEX RAIL: the connection to ChatGPT dropped mid-turn (transient). "
                "Retry the ask; if it keeps failing, check your network or 'codex' /status.")
    return "Codex rail failed: " + str(text or "unknown error")[:1200]


def run(prompt, model, mcp_config, allowed_tools="", effort=None,
        on_event=lambda kind, text: None,
        on_action=lambda name, args: None,
        cancel_check=lambda: "", extra_env=None):
    """Run a Codex producer turn and stream normalized events.

    ``cancel_check`` returns an empty string while live or the user-facing cancel
    reason.  The result dict always includes ok/canceled/final/returncode.
    """
    cmd = build_command(model, mcp_config, allowed_tools, effort=effort,
                        extra_env=extra_env)
    if cmd is None:
        on_event("error", "CODEX RAIL BLOCKED: codex CLI not found. Install with "
                          "'npm i -g @openai/codex', then run 'codex login'.")
        return {"ok": False, "canceled": False, "final": "", "returncode": 127}
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, cwd=ROOT,
                                env=subprocess_env(mcp_config, allowed_tools, extra_env),
                                start_new_session=True, bufsize=1)
    except OSError as exc:
        on_event("error", _friendly_failure(exc))
        return {"ok": False, "canceled": False, "final": "", "returncode": 127}
    try:
        proc.stdin.write(str(prompt))
        proc.stdin.close()
    except Exception as exc:
        _kill_tree(proc)
        on_event("error", _friendly_failure(exc))
        return {"ok": False, "canceled": False, "final": "", "returncode": 1}

    lines, reader_errors = queue.Queue(), []
    def reader():
        try:
            for line in proc.stdout:
                lines.put(line)
        except Exception as exc:
            reader_errors.append(exc)
        finally:
            lines.put(None)                 # the pump can never wait forever
    threading.Thread(target=reader, daemon=True).start()

    final, failure, completed, usage = "", "", False, None
    plain_tail, t0, last_heartbeat = [], time.time(), 0.0
    try:
        while True:
            reason = str(cancel_check() or "")
            if reason:
                _kill_tree(proc)
                on_event("status", reason)
                return {"ok": False, "canceled": True, "final": final,
                        "returncode": proc.poll()}
            try:
                line = lines.get(timeout=0.5)
            except queue.Empty:
                elapsed = time.time() - t0
                if elapsed - last_heartbeat >= 25.0:
                    last_heartbeat = elapsed
                    on_event("activity", f"codex: …producing ({int(elapsed)}s), still streaming…")
                continue
            if line is None:
                if reader_errors:
                    failure = f"Codex output reader failed: {reader_errors[-1]}"
                    _kill_tree(proc)
                break
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                if ("warning: proceeding" not in line.lower()
                        and "reading prompt from stdin" not in line.lower()):
                    plain_tail = (plain_tail + [line])[-8:]
                continue
            messages, action, text, done, err, event_usage = event_updates(event)
            if action:
                on_action(*action)              # structured card precedes bare activity
            for kind, message in messages:
                on_event(kind, message)
            if text:
                final = text
            completed = completed or done
            failure = err or failure
            usage = event_usage or usage
    except BaseException:
        _kill_tree(proc)                       # callbacks/cancel checks cannot orphan it
        raise

    try:
        returncode = proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        failure = failure or "Codex closed its output without exiting"
        _kill_tree(proc)
        returncode = proc.poll()
    if usage:
        inp = int(usage.get("input_tokens", 0) or 0)
        cached = int(usage.get("cached_input_tokens", 0) or 0)
        out = int(usage.get("output_tokens", 0) or 0)
        on_event("activity", f"tokens: {inp / 1000:.1f}k in ({cached / 1000:.1f}k cached) "
                             f"/ {out / 1000:.1f}k out · codex/{model_slug(model)}")
    ok = returncode == 0 and completed and not failure
    if not ok:
        detail = failure or ("\n".join(plain_tail[-4:])) or f"process exited {returncode}"
        on_event("error", _friendly_failure(detail))
    return {"ok": ok, "canceled": False, "final": final,
            "returncode": returncode, "failure": failure}


if __name__ == "__main__":
    print(json.dumps({"codex": codex_bin(), "prefix": CODEX_PREFIX}))
