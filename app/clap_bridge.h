// clap_bridge — the ONLY doorway to CLAP hosting (V50). Mirrors nam_bridge:
// a C-ish interface so SongLoader/ui_main/m1 TUs never include the CLAP headers.
// Hosts any .clap effect as a fixed-preset stereo insert (dlopen -> factory ->
// create -> activate -> process). Instruments load too but need note events to
// sound (fx are the provable audio-in->audio-out case).
#pragma once

struct ClapHandle;   // opaque: owns one loaded .clap plugin (+ its DSO)

// Load plugin `index` from a .clap bundle. Returns nullptr on failure (err gets
// one actionable line). The DSO stays open until clap_unload.
ClapHandle* clap_load (const char* path, int index, char* err, int errLen);
// REQUIRED before processing (and on sample-rate/block changes).
bool clap_activate (ClapHandle* h, double sampleRate, int maxBlock);
// Stereo in -> stereo out, n frames. Stateful; call from ONE (audio) thread.
void clap_process_audio (ClapHandle* h, const float* inL, const float* inR,
                         float* outL, float* outR, int n);
// The plugin's display name (from its descriptor), or "" if unknown.
const char* clap_name (ClapHandle* h);
void clap_unload (ClapHandle* h);
