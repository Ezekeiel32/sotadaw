#!/usr/bin/env python3
"""THE INBOX battery — machine law for agent/attachments.py.

Plants one file of every family in a scratch inbox (songs/.attach/_attach_probe),
ingests each, and holds the block to its contract: kinds correct, summaries
carry the real content, caching works (second read = cache hit), the LAW line
rides, the cap holds, and an empty inbox yields an EMPTY string (no block).
Pure python + the repo's own bridges; no daemon, no build.
"""
import json
import os
import shutil
import struct
import subprocess
import sys
import wave
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import attachments  # noqa: E402

PROBE = "_attach_probe"
DIR = attachments.attach_dir(PROBE)
PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {str(detail)[:220]}")


def tiny_png(path):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">II", 7, 5) + b"\x08\x02\x00\x00\x00"
    import binascii
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", binascii.crc32(tag + data) & 0xffffffff))
    import zlib
    raw = b"".join(b"\x00" + b"\x80\x40\x20" * 7 for _ in range(5))
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw))
                + chunk(b"IEND", b""))


def tiny_wav(path):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        import math
        frames = b"".join(struct.pack("<h", int(12000 * math.sin(i * 0.0625)))
                          for i in range(int(44100 * 0.3)))
        w.writeframes(frames)


def tiny_docx(path):
    doc = ('<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/'
           'wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Verse idea: banjo answers '
           'the fiddle, darker second half.</w:t></w:r></w:p></w:body></w:document>')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", doc)


def main():
    shutil.rmtree(DIR, ignore_errors=True)
    # EMPTY INBOX FIRST: no dir -> no block
    check("empty inbox -> empty block", attachments.attachments_context_block(PROBE) == "")
    os.makedirs(DIR, exist_ok=True)

    with open(os.path.join(DIR, "note.txt"), "w") as f:
        f.write("chorus wants a key change to Eb\nkeep the banjo roll\n")
    with open(os.path.join(DIR, "table.csv"), "w") as f:
        f.write("bar,section,energy\n1,intro,0.2\n17,verse,0.5\n33,chorus,0.9\n")
    tiny_docx(os.path.join(DIR, "memo.docx"))
    tiny_png(os.path.join(DIR, "pic.png"))
    tiny_wav(os.path.join(DIR, "clip.wav"))
    with open(os.path.join(DIR, "junk.bin"), "wb") as f:
        f.write(os.urandom(64))
    # a real .mid via the bridge (export a 2-note song)
    song = {"version": 2, "bpm": 120, "key": "C major", "lengthBars": 1,
            "tracks": [{"name": "lead", "source": {"kind": "faust", "id": "pluck2"},
                        "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8},
                                  {"start": 1, "len": 1, "pitch": 64, "vel": 0.8}]}]}
    sj = os.path.join(DIR, ".src.json")
    with open(sj, "w") as f:
        json.dump(song, f)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "midi_bridge.py"),
                    "export", sj, os.path.join(DIR, "riff.mid")],
                   capture_output=True, timeout=120)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "musicxml_export.py"),
                    sj, os.path.join(DIR, "chart.musicxml")],
                   capture_output=True, timeout=120)
    os.unlink(sj)

    s = attachments.summarize(os.path.join(DIR, "note.txt"))
    check("txt kind + content", s["kind"] == "text" and "key change" in s["summary"], s)
    s = attachments.summarize(os.path.join(DIR, "table.csv"))
    check("csv kind + columns", s["kind"] == "table" and "section" in s["summary"]
          and "3 rows" in s["summary"], s)
    s = attachments.summarize(os.path.join(DIR, "memo.docx"))
    check("docx text extracted", s["kind"] == "doc" and "banjo answers" in s["summary"], s)
    s = attachments.summarize(os.path.join(DIR, "pic.png"))
    check("png dims", s["kind"] == "image" and "7x5" in s["summary"], s)
    s = attachments.summarize(os.path.join(DIR, "riff.mid"))
    check("midi notes counted", s["kind"] == "midi" and "2 notes" in s["summary"], s)
    s = attachments.summarize(os.path.join(DIR, "chart.musicxml"))
    check("musicxml score stats", s["kind"] == "score" and "SCORE" in s["summary"], s)
    s = attachments.summarize(os.path.join(DIR, "junk.bin"))
    check("unknown type honest", "Read" in s["summary"], s)
    s = attachments.summarize(os.path.join(DIR, "clip.wav"))
    check("wav measured (ears or duration)",
          s["kind"] == "audio" and ("EARS" in s["summary"] or "0.3s" in s["summary"]), s)

    # cache: ingest -> stored -> second call returns the SAME dict from cache
    p = os.path.join(DIR, "note.txt")
    fp = attachments.fingerprint(p)
    first = attachments.ingest(p)
    check("cache stored after ingest", attachments.cache_get(fp) is not None)
    second = attachments.ingest(p)
    check("cache hit returns same summary", first == second, (first, second))

    block = attachments.attachments_context_block(PROBE)
    check("block carries filenames", "note.txt" in block and "table.csv" in block
          and "riff.mid" in block, block[:200])
    check("block carries the LAW", "never instructions" in block, block[-200:])
    check("block under cap", len(block) <= attachments.BLOCK_CAP, len(block))
    check("block headlines the inbox path", ".attach/" + PROBE in block, block[:120])

    shutil.rmtree(DIR, ignore_errors=True)
    print(f"\nattach_battery: {PASS} ok, {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
