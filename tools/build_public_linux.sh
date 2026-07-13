#!/bin/bash
# PUBLIC LINUX BUILD (2026-07-13): one-shot — focal-glibc (2.31) binaries with
# STATIC interp libfaust (JIT ON everywhere, zero libfaust package dep) and
# static libstdc++/libgcc (stock-focal safe), then the .deb + AppImage are
# packaged INSIDE the container so the bundled-lib closure and dpkg Depends are
# focal truth: t64-free names that resolve on every Ubuntu 20.04 -> current
# (noble+ satisfies them via the t64 packages' Provides).
#   tools/build_public_linux.sh   -> dist/public_linux/{sotadaw_*.deb,SOTA_DAW-x86_64.AppImage}
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dist/public_linux"
mkdir -p "$OUT"
# appimagetool cache (avoids the github download inside the container)
[ -x "$ROOT/dist/appimagetool-x86_64.AppImage" ] && \
  cp -n "$ROOT/dist/appimagetool-x86_64.AppImage" "$OUT/" 2>/dev/null || true

docker build -t sotadaw-focal "$ROOT/tools/focal"
docker run --rm \
  -v sotadaw_public_build:/build \
  -v "$ROOT":/src:ro \
  -v "$ROOT/tools/focal/faust_include":/usr/include/faust:ro \
  -v "$OUT":/out \
  sotadaw-focal bash -c '
  set -euo pipefail
  git config --global --add safe.directory /src

  # ---- faust dist (cached in the volume): static interp libfaust + stdlib ----
  if [ ! -f /build/faustdist/lib/libfaust.a ]; then
    echo "== building faust 2.85.9 (interp, static) =="
    rm -rf /build/fsrc /build/fb /build/flibs /build/faustdist
    git clone --depth 1 --branch 2.85.9 https://github.com/grame-cncm/faust /build/fsrc
    git clone --depth 1 https://github.com/grame-cncm/faustlibraries /build/flibs
    cmake -S /build/fsrc/build -B /build/fb -C /build/fsrc/build/backends/interp.cmake \
          -DINCLUDE_STATIC=ON -DINCLUDE_DYNAMIC=OFF -DINCLUDE_EXECUTABLE=OFF \
          -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc-11 -DCMAKE_CXX_COMPILER=g++-11
    cmake --build /build/fb --target staticlib -j2 || cmake --build /build/fb -j2
    mkdir -p /build/faustdist/lib /build/faustdist/include /build/faustdist/share/faust
    cp "$(find /build/fb /build/fsrc/build -name "libfaust*.a" | head -1)" /build/faustdist/lib/libfaust.a
    cp -R /build/fsrc/architecture/faust /build/faustdist/include/faust
    cp /build/flibs/*.lib /build/faustdist/share/faust/
    rm -rf /build/fsrc /build/fb /build/flibs
  fi
  echo "== faustdist: $(ls /build/faustdist/lib) + $(ls /build/faustdist/share/faust | wc -l) stdlib files =="

  # ---- app: focal glibc floor, static C++ runtime, JIT via the static dist ----
  cmake -B /build -S /src/app -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_C_COMPILER=gcc-11 -DCMAKE_CXX_COMPILER=g++-11 \
        -DSOTADAW_ENABLE_JIT=ON -DSOTADAW_FAUST_DIST=/build/faustdist \
        -DCMAKE_EXE_LINKER_FLAGS="-static-libstdc++ -static-libgcc"
  cmake --build /build -j2 --target sotadaw m1

  echo "== glibc floor (must be <= 2.31) =="
  for b in /build/m1_artefacts/Release/m1 "/build/sotadaw_artefacts/Release/SOTA DAW"; do
    echo "$b: $(objdump -T "$b" | grep -o "GLIBC_2\.[0-9]*" | sort -Vu | tail -1)  libstdc++ NEEDED: $(objdump -p "$b" | grep -c libstdc++ || true)"
  done

  # ---- package INSIDE the rig: focal ldd closure + focal dep names ----
  export SOTADAW_BUILD=/build SOTADAW_DIST=/out SOTADAW_FAUSTLIBS=/build/faustdist/share/faust
  bash /src/tools/make_deb.sh
  bash /src/tools/make_appimage.sh
  rm -rf /out/debroot /out/AppDir
  chown -R "$(stat -c %u:%g /out)" /out
'
echo "== public linux artifacts =="
ls -lh "$OUT"/*.deb "$OUT"/*.AppImage
