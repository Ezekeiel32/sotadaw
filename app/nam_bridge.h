// nam_bridge — the ONLY doorway to NeuralAmpModelerCore (V51 THE NAM RAIL).
// NAM core is Eigen-heavy; this C-ish interface quarantines those headers in
// nam_bridge.cpp so SongLoader/ui_main/m1 TUs never pay the compile (the same
// isolation law as the OOM-proof ui_main compile).
#pragma once

struct NamHandle;                       // opaque: owns one loaded .nam model

// Load a .nam capture. Returns nullptr on failure (err gets one actionable line).
NamHandle* nam_load (const char* path, char* err, int errLen);
// REQUIRED before processing (and on sample-rate/block changes): allocates the
// model's internal buffers and prewarms away its startup transient.
void nam_reset (NamHandle* h, double sampleRate, int maxBlock);
// Mono in -> mono out, n frames. Stateful; call from ONE thread (the audio graph).
void nam_process (NamHandle* h, const float* in, float* out, int n);
// The sample rate the capture was trained at (-1 = unknown).
double nam_expected_rate (NamHandle* h);
void nam_free (NamHandle* h);
