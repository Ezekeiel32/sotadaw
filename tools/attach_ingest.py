#!/usr/bin/env python3
"""CLI twin of agent/attachments.py — THE INBOX (chat file attachments).

Usage:
  attach_ingest.py summarize <file>   # fresh parse, prints json
  attach_ingest.py ingest <file>      # cached (FalkorDB + json fallback), prints json
  attach_ingest.py block <song>       # the ATTACHMENTS prompt block for a song's inbox
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent"))
import attachments  # noqa: E402


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "summarize":
        print(json.dumps(attachments.summarize(arg), indent=1))
    elif cmd == "ingest":
        print(json.dumps(attachments.ingest(arg), indent=1))
    elif cmd == "block":
        sys.stdout.write(attachments.attachments_context_block(arg))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
