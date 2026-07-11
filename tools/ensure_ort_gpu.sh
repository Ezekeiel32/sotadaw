#!/usr/bin/env bash
# THE VOICE GPU RAIL (Chezy live 2026-07-09: "BUILD IT IN TO CMAKE>"): keep the
# repo venv able to run the DiffSinger voice on CUDA. Bare `pip install` on this
# OS is PEP-668 blocked — everything goes through .venv's own pip. Idempotent
# (a passing probe costs ~1s, installs nothing) and NEVER fails the build:
# offline / GPU-less boxes compile fine and keep the CPU voice.
# The CUDA libs themselves come from torch's pip wheels (site-packages/nvidia/
# */lib) — tools/sing.py preloads them with RTLD_GLOBAL at session creation, so
# no system CUDA toolkit is required. Probe mirrors that exact preload.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || { echo "[ort-gpu] no .venv - skipped (python side unmanaged here)"; exit 0; }

probe() {
  "$PY" - <<'EOF'
import ctypes, glob, os, site, sys, sysconfig
roots = set()
cands = list(getattr(site, "getsitepackages", lambda: [])())
cands.append(site.getusersitepackages())
cands.append(sysconfig.get_paths().get("purelib"))
for sp in cands:
    if sp and os.path.isdir(os.path.join(sp, "nvidia")):
        roots.add(os.path.join(sp, "nvidia"))
for name in ("libcudart.so.*", "libcublasLt.so.*", "libcublas.so.*",
             "libcufft.so.*", "libcurand.so.*", "libnvrtc.so.*",
             "libcudnn.so.*"):
    for r in sorted(roots):
        for p in sorted(glob.glob(os.path.join(r, "*", "lib", name))):
            try:
                ctypes.CDLL(p, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass
try:
    import onnxruntime as o
except Exception as e:
    print(f"[ort-gpu] onnxruntime import broken: {type(e).__name__}: {e}")
    sys.exit(1)
ok = "CUDAExecutionProvider" in o.get_available_providers()
print(f"[ort-gpu] onnxruntime {o.__version__} CUDA={'YES' if ok else 'no'}")
sys.exit(0 if ok else 1)
EOF
}

if probe; then exit 0; fi
if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "[ort-gpu] no NVIDIA GPU - CPU voice stays"
  exit 0
fi
echo "[ort-gpu] installing onnxruntime-gpu into .venv (one-time)..."
if ! "$PY" -m pip install --quiet onnxruntime-gpu; then
  echo "[ort-gpu] pip install failed (offline?) - CPU voice stays"
  exit 0
fi
probe || echo "[ort-gpu] installed but CUDA provider still unavailable - CPU voice stays"
exit 0
