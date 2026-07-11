// nam_bridge.cpp — the one TU that includes NeuralAmpModelerCore (see nam_bridge.h).
// NAM_SAMPLE is float (dsp.h default) — matches the engine's buffers directly.
#include "nam_bridge.h"

#include <cstdio>
#include <cstring>
#include <memory>
#include <string>
#include <vector>

#include "NAM/dsp.h"
#include "NAM/get_dsp.h"

struct NamHandle
{
    std::unique_ptr<nam::DSP> dsp;
    std::vector<float> inBuf, outBuf;   // NAM wants channel-pointer arrays
};

NamHandle* nam_load (const char* path, char* err, int errLen)
{
    try
    {
        auto h = std::make_unique<NamHandle>();
        h->dsp = nam::get_dsp (std::filesystem::path (path));
        if (h->dsp == nullptr)
        {
            if (err != nullptr) std::snprintf (err, (size_t) errLen, "get_dsp returned null for %s", path);
            return nullptr;
        }
        return h.release();
    }
    catch (const std::exception& e)
    {
        if (err != nullptr) std::snprintf (err, (size_t) errLen, "%s", e.what());
        return nullptr;
    }
}

void nam_reset (NamHandle* h, double sampleRate, int maxBlock)
{
    if (h != nullptr && h->dsp != nullptr)
        h->dsp->ResetAndPrewarm (sampleRate, maxBlock);
}

void nam_process (NamHandle* h, const float* in, float* out, int n)
{
    if (h == nullptr || h->dsp == nullptr || n <= 0)
        return;
    if ((int) h->inBuf.size() < n)
    {
        h->inBuf.resize ((size_t) n);
        h->outBuf.resize ((size_t) n);
    }
    std::memcpy (h->inBuf.data(), in, sizeof (float) * (size_t) n);
    float* inPtr  = h->inBuf.data();
    float* outPtr = h->outBuf.data();
    float** ins  = &inPtr;
    float** outs = &outPtr;
    h->dsp->process (ins, outs, n);
    std::memcpy (out, h->outBuf.data(), sizeof (float) * (size_t) n);
}

double nam_expected_rate (NamHandle* h)
{
    return (h != nullptr && h->dsp != nullptr) ? h->dsp->GetExpectedSampleRate() : -1.0;
}

void nam_free (NamHandle* h)
{
    delete h;
}
