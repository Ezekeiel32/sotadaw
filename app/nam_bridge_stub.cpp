// nam_bridge_stub — links when the NAM vendor is absent (app/third_party/nam-core
// is gitignored like the tracktion clone; 37MB of Eigen doesn't belong in git).
// Every load fails with the restore recipe; renders pass through untouched.
#include "nam_bridge.h"
#include <cstdio>

NamHandle* nam_load (const char* path, char* err, int errLen)
{
    if (err != nullptr)
        std::snprintf (err, (size_t) errLen,
                       "NAM core not vendored on this box (wanted %s). Restore: "
                       "git clone --depth 1 https://github.com/sdatkinson/NeuralAmpModelerCore "
                       "app/third_party/nam-core && cd app/third_party/nam-core && "
                       "git submodule update --init --depth 1, then rebuild.", path);
    return nullptr;
}
void nam_reset (NamHandle*, double, int) {}
void nam_process (NamHandle*, const float* in, float* out, int n)
{
    if (in != out)
        for (int i = 0; i < n; ++i) out[i] = in[i];
}
double nam_expected_rate (NamHandle*) { return -1.0; }
void nam_free (NamHandle*) {}
