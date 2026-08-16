cmake_minimum_required(VERSION 3.22)
project(m1 VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# PORT_SPEC.md: MSVC hygiene (utf-8 literals, 21K-line TU, min/max macros, M_PI)
if(MSVC)
  add_compile_options(/utf-8 /bigobj)
  add_compile_definitions(NOMINMAX _USE_MATH_DEFINES WIN32_LEAN_AND_MEAN)
endif()
# Ableton Link platform define (was hardcoded LINUX pre-port)
if(WIN32)
  set(SOTADAW_LINK_PLATFORM LINK_PLATFORM_WINDOWS=1)
elseif(APPLE)
  set(SOTADAW_LINK_PLATFORM LINK_PLATFORM_MACOSX=1)
else()
  set(SOTADAW_LINK_PLATFORM LINK_PLATFORM_LINUX=1)
endif()

# SOTA DAW vendored-engine patches: the tracktion clone is git-ignored, so
# app/patches/*.patch are the git truth — applied idempotently at configure.
execute_process(COMMAND bash ${CMAKE_CURRENT_SOURCE_DIR}/../tools/apply_engine_patches.sh
                RESULT_VARIABLE SOTADAW_PATCH_RC)
if(NOT SOTADAW_PATCH_RC EQUAL 0)
  message(FATAL_ERROR "vendored-engine patch apply failed (tools/apply_engine_patches.sh)")
endif()

# Bring in JUCE + Tracktion Engine (defines juce:: and tracktion_engine targets)
add_subdirectory(tracktion_engine/modules/juce ${CMAKE_BINARY_DIR}/_juce)
add_subdirectory(tracktion_engine/modules      ${CMAKE_BINARY_DIR}/_tracktion)

juce_add_console_app(m1 PRODUCT_NAME "M1")
target_sources(m1 PRIVATE main.cpp)
target_include_directories(m1 PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/signalsmith-stretch
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/signalsmith-linear/include
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/faust_vendor)
# Ableton Link (W14): vendored SDK, DEV-ONLY until the commercial license lands
# (LICENSE_LEDGER law; SPEC V23). Restore: git clone --recurse-submodules
#   https://github.com/Ableton/link app/link
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/link/include)
  target_include_directories(m1 PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/link/include
      ${CMAKE_CURRENT_SOURCE_DIR}/link/modules/asio-standalone/asio/include)
  target_compile_definitions(m1 PRIVATE TRACKTION_ENABLE_ABLETON_LINK=1 ${SOTADAW_LINK_PLATFORM})
  message(STATUS "Ableton Link: ENABLED (dev build; ship gate = commercial license)")
endif()

# Trim optional Linux deps we don't need for a headless engine app
target_compile_definitions(m1 PRIVATE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_MODAL_LOOPS_PERMITTED=1
    JUCE_PLUGINHOST_VST3=1
    TRACKTION_ENABLE_TIMESTRETCH_SOUNDTOUCH=1
    TRACKTION_ENABLE_TIMESTRETCH_SIGNALSMITH=1
    SOTADAW_ROOT="${CMAKE_CURRENT_SOURCE_DIR}/..")

# JIT needs modern libfaust (interpreter backend); old distros (e.g. focal) build
# AOT-only with -DSOTADAW_ENABLE_JIT=OFF — faust HEADERS still required (dsp.h/UI.h).
option(SOTADAW_ENABLE_JIT "JIT unregistered instruments/.dsp via libfaust" ON)
# PORT_SPEC round-4: point at an extracted faust release dist (Windows/macOS CI)
# instead of system libfaust. Layout: <dist>/include/faust/..., <dist>/lib/...
set(SOTADAW_FAUST_DIST "" CACHE PATH "external faust distribution root (win/mac JIT)")
if(NOT SOTADAW_ENABLE_JIT)
  add_compile_definitions(SOTADAW_NO_JIT)
  set(SOTADAW_FAUST_LIB "")
elseif(SOTADAW_FAUST_DIST)
  include_directories(BEFORE ${SOTADAW_FAUST_DIST}/include)
  if(WIN32)
    set(SOTADAW_FAUST_LIB ${SOTADAW_FAUST_DIST}/lib/faust.lib)
  elseif(APPLE)
    set(SOTADAW_FAUST_LIB ${SOTADAW_FAUST_DIST}/lib/libfaust.a z)
  else()
    # Linux packaged builds (focal container): static interp libfaust — the
    # deb/AppImage then need no libfaust package on ANY distro (t64 or not).
    set(SOTADAW_FAUST_LIB ${SOTADAW_FAUST_DIST}/lib/libfaust.a z)
  endif()
  message(STATUS "JIT: external faust dist at ${SOTADAW_FAUST_DIST}")
else()
  set(SOTADAW_FAUST_LIB faust)
endif()

# THE NAM RAIL (V51): NeuralAmpModelerCore — Eigen stays quarantined in
# nam_core's own TUs (nam_bridge.cpp is the only doorway). OBJECT library, NOT
# static: the architecture parsers (WaveNet/LSTM) self-register via statics
# that a static-lib link DEAD-STRIPS ("No config parser registered" at load).
# The vendor (37MB) is git-ignored like the tracktion clone. Restore:
#   git clone --depth 1 https://github.com/sdatkinson/NeuralAmpModelerCore \
#     app/third_party/nam-core && cd app/third_party/nam-core && \
#   git submodule update --init --depth 1
# Absent vendor -> the stub links: loads fail with that recipe, audio passes through.
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/third_party/nam-core/NAM)
  file(GLOB NAM_CORE_SRC ${CMAKE_CURRENT_SOURCE_DIR}/third_party/nam-core/NAM/*.cpp
                         ${CMAKE_CURRENT_SOURCE_DIR}/third_party/nam-core/NAM/wavenet/*.cpp)
  add_library(nam_core OBJECT ${NAM_CORE_SRC} ${CMAKE_CURRENT_SOURCE_DIR}/nam_bridge.cpp)
  target_include_directories(nam_core PRIVATE
      ${CMAKE_CURRENT_SOURCE_DIR}/third_party/nam-core
      ${CMAKE_CURRENT_SOURCE_DIR}/third_party/nam-core/NAM
      ${CMAKE_CURRENT_SOURCE_DIR}/third_party/nam-core/Dependencies/eigen
      ${CMAKE_CURRENT_SOURCE_DIR}/third_party/nam-core/Dependencies/nlohmann)
  target_compile_definitions(nam_core PRIVATE NAM_SAMPLE_FLOAT)   # engine buffers are float
  message(STATUS "NAM rail: ENABLED (vendored core)")
else()
  add_library(nam_core OBJECT ${CMAKE_CURRENT_SOURCE_DIR}/nam_bridge_stub.cpp)
  message(STATUS "NAM rail: vendor absent -> stub (see restore recipe in CMakeLists)")
endif()
target_compile_options(nam_core PRIVATE -O2)
set_target_properties(nam_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

# CLAP HOSTING (V50): a direct C-ABI host (JUCE/tracktion host no CLAP). Headers
# are vendored (MIT, header-only, committed — hosting is runtime dlopen, so no
# .clap needed at build). clap_bridge is the only TU that sees clap/*.h.
add_library(clap_host OBJECT ${CMAKE_CURRENT_SOURCE_DIR}/clap_bridge.cpp)
target_include_directories(clap_host PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/third_party/clap/include)
target_compile_options(clap_host PRIVATE -O2)
set_target_properties(clap_host PROPERTIES POSITION_INDEPENDENT_CODE ON)

# juce_cryptography: the render seal's SHA256 print (docs/THE_PHYSICS.md E11) — m1 only
target_link_libraries(m1 PRIVATE tracktion_engine juce::juce_cryptography ${SOTADAW_FAUST_LIB} nam_core clap_host ${CMAKE_DL_LIBS})

# THE TYPE IS THE PRODUCT (relight v8): Inter (UI) + JetBrains Mono (LCDs/digits)
# embedded as BinaryData — the same face on every machine. Public builds used to
# render with whatever fontconfig offered (Noto here, DejaVu elsewhere). SIL OFL
# licenses ride in app/fonts/. UI-only: m1 never links this.
juce_add_binary_data(sotadaw_fonts SOURCES
    fonts/Inter-Regular.ttf
    fonts/Inter-SemiBold.ttf
    fonts/JetBrainsMono-Regular.ttf
    fonts/JetBrainsMono-Bold.ttf
    fonts/Bravura.otf
    icon.png)
set_target_properties(sotadaw_fonts PROPERTIES POSITION_INDEPENDENT_CODE ON)

# --- GUI app (UI seam v0) ---
juce_add_gui_app(sotadaw PRODUCT_NAME "SOTA DAW")
target_sources(sotadaw PRIVATE ui_main.cpp)
target_include_directories(sotadaw PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/signalsmith-stretch
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/signalsmith-linear/include
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/faust_vendor)
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/link/include)
  target_include_directories(sotadaw PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/link/include
      ${CMAKE_CURRENT_SOURCE_DIR}/link/modules/asio-standalone/asio/include)
  target_compile_definitions(sotadaw PRIVATE TRACKTION_ENABLE_ABLETON_LINK=1 ${SOTADAW_LINK_PLATFORM})
endif()
target_compile_definitions(sotadaw PRIVATE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_MODAL_LOOPS_PERMITTED=1
    JUCE_PLUGINHOST_VST3=1
    TRACKTION_ENABLE_TIMESTRETCH_SOUNDTOUCH=1
    TRACKTION_ENABLE_TIMESTRETCH_SIGNALSMITH=1
    SOTADAW_ROOT="${CMAKE_CURRENT_SOURCE_DIR}/..")
target_link_libraries(sotadaw PRIVATE tracktion_engine ${SOTADAW_FAUST_LIB} nam_core clap_host sotadaw_fonts ${CMAKE_DL_LIBS})

juce_add_console_app(uismoke PRODUCT_NAME "uismoke")
target_sources(uismoke PRIVATE uismoke.cpp)
target_include_directories(uismoke PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_definitions(uismoke PRIVATE
    JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0
    SOTADAW_ROOT="${CMAKE_CURRENT_SOURCE_DIR}/..")
target_link_libraries(uismoke PRIVATE
    juce::juce_gui_basics juce::juce_graphics juce::juce_gui_extra
    sotadaw_fonts
    juce::juce_recommended_config_flags)

# THE VOICE GPU RAIL (Chezy: "BUILD IT IN TO CMAKE>"): every build keeps the
# repo venv able to sing on CUDA — tools/ensure_ort_gpu.sh probes the venv's
# onnxruntime for the CUDA provider (mirroring sing.py's torch-wheel preload)
# and installs onnxruntime-gpu via the venv's own pip only when missing (bare
# pip is PEP-668 blocked on this OS). NEVER fails the build: offline or
# GPU-less boxes keep the CPU voice. Probe cost when satisfied: ~1s.
add_custom_target(ort_gpu_rail
    COMMAND bash "${CMAKE_CURRENT_SOURCE_DIR}/../tools/ensure_ort_gpu.sh"
    COMMENT "voice GPU rail: onnxruntime CUDA provider in .venv"
    VERBATIM)
add_dependencies(m1 ort_gpu_rail)
add_dependencies(sotadaw ort_gpu_rail)
