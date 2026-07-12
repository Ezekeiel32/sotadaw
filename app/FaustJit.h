// FaustJit.h — the AOT escape hatch: any instruments/<name>.dsp NOT compiled into
// the registry is JIT-compiled at load via libfaust's interpreter backend. New
// instruments play IMMEDIATELY — no gen_faust, no rebuild, no app restart.
// Factories cache per name; editing a .dsp and reloading the song re-JITs it
// (SongLoader rebuilds plugins per edit, and the cache keys on file mtime).
#pragma once

#ifdef SOTADAW_NO_JIT
// Old-distro build (SOTADAW_ENABLE_JIT=OFF, no modern libfaust): AOT registry
// only — unregistered .dsp names resolve to null and the voice is silent
// instead of JIT'd. All registry-baked voices work normally.
#include <string>
class dsp;   // faust base class; full decl comes from faust/dsp/dsp.h in AOT TUs
namespace sotadaw
{
inline ::dsp* createJitFaustDsp (const std::string&, std::string& err)
{
    err = "built with SOTADAW_ENABLE_JIT=OFF (AOT registry only)";
    return nullptr;
}
}
#else
#include <faust/dsp/interpreter-dsp.h>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <sys/stat.h>

namespace sotadaw
{

inline std::string jitDspPath (const std::string& name)
{
    // resolution order: env root -> cwd-relative -> binary-adjacent AppImage payload
    if (const char* r = std::getenv ("SOTADAW_ROOT"))
    {
        auto p = std::string (r) + "/instruments/" + name + ".dsp";
        if (std::ifstream (p).good()) return p;
    }
    auto p = "instruments/" + name + ".dsp";
    if (std::ifstream (p).good()) return p;
    if (const char* ap = std::getenv ("APPDIR"))     // inside an AppImage
    {
        p = std::string (ap) + "/usr/share/sotadaw-payload/instruments/" + name + ".dsp";
        if (std::ifstream (p).good()) return p;
    }
    return {};
}

inline ::dsp* createJitFaustDsp (const std::string& name, std::string& error)
{
    struct Entry { interpreter_dsp_factory* factory; time_t mtime; };
    static std::map<std::string, Entry> cache;
    static std::mutex lock;

    const auto path = jitDspPath (name);
    if (path.empty())
    {
        error = "no instruments/" + name + ".dsp found for JIT";
        return nullptr;
    }
    struct stat st {};
    stat (path.c_str(), &st);

    std::lock_guard<std::mutex> g (lock);
    auto it = cache.find (name);
    if (it != cache.end() && it->second.mtime != st.st_mtime)
    {
        deleteInterpreterDSPFactory (it->second.factory);   // .dsp edited: re-JIT
        cache.erase (it);
        it = cache.end();
    }
    if (it == cache.end())
    {
        std::ifstream f (path);
        std::stringstream src;
        src << f.rdbuf();
        // stdlib import path: env override first (packaged Win/mac builds ship
        // faustlibs/ and point this at it), else the Linux system path.
        static const std::string libPath = []
        {
            if (const char* e = std::getenv ("SOTADAW_FAUST_LIB_PATH")) return std::string (e);
            return std::string ("/usr/share/faust");
        }();
        const char* argv[] = { "-I", libPath.c_str() };
        auto* factory = createInterpreterDSPFactoryFromString (name, src.str(), 2, argv, error);
        if (factory == nullptr)
        {
            // PORT_SPEC round-4 truth: a silent null here cost a CI round —
            // the compiler message must always reach stderr.
            std::fprintf (stderr, "[fxdbg] JIT %s FAILED: %s\n", name.c_str(), error.c_str());
            return nullptr;
        }
        it = cache.emplace (name, Entry { factory, st.st_mtime }).first;
    }
    if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
        std::fprintf (stderr, "[fxdbg] JIT %s (interpreter, %s)\n", name.c_str(), path.c_str());
    return it->second.factory->createDSPInstance();
}

} // namespace sotadaw

#endif // SOTADAW_NO_JIT
