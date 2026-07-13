// clap_bridge.cpp — the one TU that includes the CLAP headers (see clap_bridge.h).
// A minimal CLAP HOST: enough to load a .clap effect and pump stereo audio through
// it with a fixed preset. Host extensions all return null (legal — plugins must
// tolerate an absent host extension); empty event queues; no GUI/state/params.
#include "clap_bridge.h"

#include <clap/clap.h>

#include <cstdio>
#include <cstring>
#ifdef _WIN32
 // PORT_SPEC.md: minimal dl* shim over LoadLibrary — a .clap on Windows is a DLL.
 #ifndef WIN32_LEAN_AND_MEAN
  #define WIN32_LEAN_AND_MEAN
 #endif
 #include <windows.h>
 #define RTLD_LOCAL 0
 #define RTLD_NOW 0
 static void* dlopen (const char* p, int) { return (void*) ::LoadLibraryA (p); }
 static int   dlclose (void* h) { return ::FreeLibrary ((HMODULE) h) ? 0 : 1; }
 static void* dlsym (void* h, const char* s) { return (void*) ::GetProcAddress ((HMODULE) h, s); }
 static const char* dlerror() { static char b[64]; std::snprintf (b, sizeof b, "win32 error %lu", ::GetLastError()); return b; }
#else
 #include <dlfcn.h>
#endif
#include <string>
#include <vector>

namespace
{
// The host we present to every plugin. Bare by design: get_extension returns
// null for all ids, the request_* callbacks are no-ops (we never defer work).
const void* CLAP_ABI host_get_extension (const clap_host*, const char*) { return nullptr; }
void CLAP_ABI host_request_restart (const clap_host*) {}
void CLAP_ABI host_request_process (const clap_host*) {}
void CLAP_ABI host_request_callback (const clap_host*) {}

const clap_host g_host = {
    CLAP_VERSION_INIT,
    nullptr,                       // host_data
    "SOTA DAW", "SOTA DAW", "https://local", "1.0",
    host_get_extension, host_request_restart, host_request_process, host_request_callback
};

// Empty input event queue + a swallow-all output queue (fixed-preset fx: no
// automation in, drop any events out).
uint32_t CLAP_ABI in_size (const clap_input_events*) { return 0; }
const clap_event_header_t* CLAP_ABI in_get (const clap_input_events*, uint32_t) { return nullptr; }
bool CLAP_ABI out_try_push (const clap_output_events*, const clap_event_header_t*) { return true; }

const clap_input_events  g_in_events  = { nullptr, in_size, in_get };
const clap_output_events g_out_events = { nullptr, out_try_push };
} // namespace

struct ClapHandle
{
    void* dso = nullptr;
    const clap_plugin_entry* entry = nullptr;
    const clap_plugin* plugin = nullptr;
    std::string name;
    bool activated = false;
    bool processing = false;
    int64_t steady = 0;
    std::vector<float> inL, inR, outL, outR;   // scratch (process wants writable float**)
};

ClapHandle* clap_load (const char* path, int index, char* err, int errLen)
{
    auto fail = [&] (const std::string& m) -> ClapHandle*
    {
        if (err != nullptr) std::snprintf (err, (size_t) errLen, "%s", m.c_str());
        return nullptr;
    };
    void* dso = dlopen (path, RTLD_LOCAL | RTLD_NOW);
    if (dso == nullptr)
    {
        const char* e = dlerror();       // consume ONCE — a 2nd dlerror() returns null
        return fail (std::string ("dlopen failed: ") + (e != nullptr ? e : "?"));
    }

    auto* entry = reinterpret_cast<const clap_plugin_entry*> (dlsym (dso, "clap_entry"));
    if (entry == nullptr) { dlclose (dso); return fail ("no clap_entry symbol"); }
    if (entry->init == nullptr || ! entry->init (path)) { dlclose (dso); return fail ("entry.init failed"); }

    auto* factory = reinterpret_cast<const clap_plugin_factory*> (
        entry->get_factory (CLAP_PLUGIN_FACTORY_ID));
    if (factory == nullptr || factory->get_plugin_count (factory) == 0)
    { entry->deinit(); dlclose (dso); return fail ("no plugin factory / zero plugins"); }

    const uint32_t count = factory->get_plugin_count (factory);
    const uint32_t idx = (index >= 0 && (uint32_t) index < count) ? (uint32_t) index : 0;
    const clap_plugin_descriptor* desc = factory->get_plugin_descriptor (factory, idx);
    if (desc == nullptr) { entry->deinit(); dlclose (dso); return fail ("null descriptor"); }

    const clap_plugin* plugin = factory->create_plugin (factory, &g_host, desc->id);
    if (plugin == nullptr) { entry->deinit(); dlclose (dso); return fail ("create_plugin returned null"); }
    if (plugin->init == nullptr || ! plugin->init (plugin))
    { if (plugin->destroy) plugin->destroy (plugin); entry->deinit(); dlclose (dso); return fail ("plugin.init failed"); }

    auto* h = new ClapHandle();
    h->dso = dso; h->entry = entry; h->plugin = plugin;
    h->name = desc->name ? desc->name : "";
    return h;
}

bool clap_activate (ClapHandle* h, double sampleRate, int maxBlock)
{
    if (h == nullptr || h->plugin == nullptr) return false;
    if (h->processing) { h->plugin->stop_processing (h->plugin); h->processing = false; }
    if (h->activated)  { h->plugin->deactivate (h->plugin); h->activated = false; }
    const uint32_t mb = (uint32_t) (maxBlock > 0 ? maxBlock : 512);
    if (! h->plugin->activate (h->plugin, sampleRate, 1, mb)) return false;
    h->activated = true;
    if (h->plugin->start_processing != nullptr)
        h->processing = h->plugin->start_processing (h->plugin);
    else
        h->processing = true;
    h->inL.assign (mb, 0.0f); h->inR.assign (mb, 0.0f);
    h->outL.assign (mb, 0.0f); h->outR.assign (mb, 0.0f);
    return h->activated;
}

void clap_process_audio (ClapHandle* h, const float* inL, const float* inR,
                         float* outL, float* outR, int n)
{
    if (h == nullptr || h->plugin == nullptr || ! h->activated || n <= 0)
        return;
    if ((int) h->inL.size() < n)
    { h->inL.resize (n); h->inR.resize (n); h->outL.resize (n); h->outR.resize (n); }
    std::memcpy (h->inL.data(), inL, sizeof (float) * (size_t) n);
    std::memcpy (h->inR.data(), inR, sizeof (float) * (size_t) n);

    float* inCh[2]  = { h->inL.data(),  h->inR.data() };
    float* outCh[2] = { h->outL.data(), h->outR.data() };
    clap_audio_buffer inBuf { inCh,  nullptr, 2, 0, 0 };
    clap_audio_buffer outBuf { outCh, nullptr, 2, 0, 0 };

    clap_process p {};
    p.steady_time = h->steady;
    p.frames_count = (uint32_t) n;
    p.transport = nullptr;
    p.audio_inputs = &inBuf;
    p.audio_outputs = &outBuf;
    p.audio_inputs_count = 1;
    p.audio_outputs_count = 1;
    p.in_events = &g_in_events;
    p.out_events = &g_out_events;

    const clap_process_status st = h->plugin->process (h->plugin, &p);
    h->steady += n;
    if (st == CLAP_PROCESS_ERROR)   // plugin refused: pass audio through untouched
    { std::memcpy (outL, inL, sizeof (float) * (size_t) n);
      std::memcpy (outR, inR, sizeof (float) * (size_t) n); return; }
    std::memcpy (outL, h->outL.data(), sizeof (float) * (size_t) n);
    std::memcpy (outR, h->outR.data(), sizeof (float) * (size_t) n);
}

const char* clap_name (ClapHandle* h) { return (h != nullptr) ? h->name.c_str() : ""; }

void clap_unload (ClapHandle* h)
{
    if (h == nullptr) return;
    if (h->plugin != nullptr)
    {
        if (h->processing) h->plugin->stop_processing (h->plugin);
        if (h->activated)  h->plugin->deactivate (h->plugin);
        if (h->plugin->destroy) h->plugin->destroy (h->plugin);
    }
    if (h->entry != nullptr && h->entry->deinit != nullptr) h->entry->deinit();
    if (h->dso != nullptr) dlclose (h->dso);
    delete h;
}
