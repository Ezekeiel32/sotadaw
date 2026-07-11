// AI SOTA DAW — engine CLI (m1)
//   m1                                    boot check
//   m1 instruments                        list Faust instruments
//   m1 scan-plugins                       scan VST3s -> app/plugins_cache.xml
//   m1 render <song.json> <out.wav>       render a song (v0/v1/v2) headless
//   m1 render-stems <song.json> <outdir>  render each track solo to <outdir>/NN_name.wav
//   m1 list-params <song.json>            JSON dump of every automatable parameter
//                                         (track/plugin/param/value/min/max) — the agent's map
//                                         of "every knob in the session"
#include <tracktion_engine/tracktion_engine.h>
#include <juce_cryptography/juce_cryptography.h>   // SHA256 for the render seal (E11)
#include <iostream>
#include <cstdlib>
#include <ctime>
#include <atomic>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <thread>
#include "SongLoader.h"
#include "EditDelta.h"     // hidden delta-null verb: THE ENGINE DELTA's proof organ
#include "PluginFaces.h"   // m1 faces: paint every plugin face offscreen (agent eyes)

const char* FaustInstrumentPlugin::xmlTypeName = "faustInstrument";
const char* SpectralVoicePlugin::xmlTypeName = "spectralVoice";
const char* FaustFxPlugin::xmlTypeName = "faustFx";
const char* RetunePlugin::xmlTypeName = "sotaRetune";

namespace te = tracktion;
using namespace tracktion::literals;

static int bootCheck()
{
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    std::cout << "[m1] Tracktion Engine booted OK.\n";
    return 0;
}

static int listInstruments()
{
    for (auto& n : faustDspNames())
        std::cout << n << "\n";
    return 0;
}

static int scanPlugins()
{
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    auto& pm = engine.getPluginManager();
    juce::VST3PluginFormat format;
    auto paths = format.getDefaultLocationsToSearch();

    // crash-proofing: a marker names the plugin being scanned; if a previous scan
    // died mid-file, that plugin is blacklisted and skipped forever after
    auto marker = sotadaw::sotadawRoot().getChildFile ("app/plugins_scan_current.txt");
    auto blacklistFile = sotadaw::sotadawRoot().getChildFile ("app/plugins_blacklist.txt");
    if (marker.existsAsFile())
    {
        const auto culprit = marker.loadFileAsString().trim();
        if (culprit.isNotEmpty())
        {
            blacklistFile.appendText (culprit + "\n");
            std::cout << "[m1] previous scan crashed on: " << culprit << " -> blacklisted\n";
        }
        marker.deleteFile();
    }
    juce::StringArray blacklist;
    blacklist.addLines (blacklistFile.loadFileAsString());
    blacklist.removeEmptyStrings();

    juce::PluginDirectoryScanner scanner (pm.knownPluginList, format, paths, true, {});
    juce::String name;
    for (;;)
    {
        const auto next = scanner.getNextPluginFileThatWillBeScanned();
        if (blacklist.contains (next))
        {
            std::cout << "[scan] SKIP (blacklisted): " << next << "\n";
            if (! scanner.skipNextFile()) break;
            continue;
        }
        marker.replaceWithText (next);
        const bool more = scanner.scanNextFile (true, name);
        marker.deleteFile();
        std::cout << "[scan] " << name << "\n";
        if (auto xml = pm.knownPluginList.createXml())     // incremental: survive a later crash
            xml->writeTo (sotadaw::pluginCacheFile());
        if (! more) break;
    }
    std::cout << "[m1] plugins found: " << pm.knownPluginList.getNumTypes()
              << " -> " << sotadaw::pluginCacheFile().getFullPathName() << "\n";
    for (const auto& d : pm.knownPluginList.getTypes())
        std::cout << "  " << d.name << " (" << d.pluginFormatName << ")\n";
    return 0;
}

static std::unique_ptr<te::Edit> loadSongEdit (te::Engine& engine, const juce::File& songFile,
                                               sotadaw::Song& song, int& err)
{
    err = 0;
    if (! sotadaw::parseSong (songFile, song))
    {
        std::cerr << "[m1] ERROR: cannot parse " << songFile.getFullPathName() << "\n";
        err = 2;
        return nullptr;
    }
    juce::String buildErrors;
    auto edit = sotadaw::buildEdit (engine, song, te::Edit::EditRole::forRendering, &buildErrors);
    if (buildErrors.isNotEmpty())
        std::cerr << "[m1] BUILD WARNINGS:\n" << buildErrors;

    // flush pending async updates (SamplerPlugin rebuilds its sound list on the
    // message loop after addSound) — without this, headless renders play an EMPTY
    // sampler. The blind 250ms here was the render pipeline's largest fixed cost:
    // pump 10ms slices only until every sampler reports its sounds (rebuilds are
    // whole-list, so numSounds>0 == rebuilt; an empty kit rides the full cap =
    // old behavior). Sampler-free songs settle in one 25ms slice. THE SEAL is
    // the judge: the gold corpus carries 3 sampler songs + 3 without.
    juce::Array<te::SamplerPlugin*> samplers;
    for (auto* t : te::getAudioTracks (*edit))
        for (auto* p : t->pluginList.getPlugins())
            if (auto* sp = dynamic_cast<te::SamplerPlugin*> (p))
                samplers.add (sp);
    if (samplers.isEmpty())
        juce::MessageManager::getInstance()->runDispatchLoopUntil (25);
    else
    {
        for (int spent = 0; spent < 250; spent += 10)
        {
            juce::MessageManager::getInstance()->runDispatchLoopUntil (10);
            bool ready = true;
            for (auto* sp : samplers)
                ready = ready && sp->getNumSounds() > 0;
            if (ready)
            {   // one settle slice for any chained updates, then go
                juce::MessageManager::getInstance()->runDispatchLoopUntil (10);
                break;
            }
        }
    }
    int notes = 0;
    for (auto& t : song.tracks) notes += (int) t.notes.size();
    std::cout << "[m1] song: bpm=" << song.bpm << " bars=" << song.lengthBars
              << " tracks=" << song.tracks.size() << " notes=" << notes
              << " swing=" << song.swingAmount
              << " master_fx=" << song.master.size()
              << " len=" << edit->getLength().inSeconds() << "s\n";
    return edit;
}

static int renderCore (te::Engine& engine, const juce::File& songFile, const juce::File& outFile)
{
    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;

    outFile.deleteFile();
    // renderToFile(edit,file) ignores track mutes offline — render via explicit track bits
    // (muted song tracks excluded; bus tracks always included)
    juce::BigInteger bits;
    auto all = te::getAllTracks (*edit);
    auto audio = te::getAudioTracks (*edit);
    for (int j = 0; j < all.size(); ++j)
        for (int a = 0; a < audio.size(); ++a)
            if (all[j] == audio[a] && ! (a < (int) song.tracks.size() && song.tracks[(size_t) a].muted))
                bits.setBit (j);
    const auto range = te::TimeRange (0_tp, edit->getLength());
    const bool ok = te::Renderer::renderToFile ("render", outFile, *edit, range, bits, true, true, {}, false);
    std::cout << "[m1] renderToFile ok=" << (ok ? 1 : 0) << " bytes=" << outFile.getSize()
              << " -> " << outFile.getFullPathName() << "\n";
    if (ok && outFile.existsAsFile())
    {   // THE SEAL (E1/E11): the hash IS the render's name downstream (cache, C2PA, KG)
        juce::FileInputStream fis (outFile);
        std::cout << "[m1] render_sha256=" << juce::SHA256 (fis).toHexString()
                  << " file=" << outFile.getFileName() << "\n";
    }
    // the >1000 floor guards against corrupt renders of REAL songs — an empty
    // song (new project, 0 notes) legitimately writes a header-only wav and is
    // NOT an error (the Inspiron greeted a new user with "render failed")
    const bool emptySong = edit->getLength().inSeconds() <= 0.0;
    if (emptySong)
        std::cout << "[m1] empty song - nothing to render yet\n";
    return (ok && (outFile.getSize() > 1000 || emptySong)) ? 0 : 1;
}

static int renderSong (const juce::File& songFile, const juce::File& outFile)
{
    // P6 THE THREAD LAW (docs/THE_PHYSICS.md E10): flush denormals to zero for the
    // whole render — FTZ/DAZ is thread-local CPU state, so this covers the Tracktion
    // graph AND every Faust voice running on this thread (they were LIVE before: no
    // ScopedNoDenormals anywhere + faust -ftz 0). Sub-audible tails (< -144 dBFS)
    // flush to 0; the change is inaudible, the denormal CPU spikes are gone.
    juce::ScopedNoDenormals _noDenormals;
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);
    return renderCore (engine, songFile, outFile);
}

// delta-null — THE ENGINE DELTA's proof organ (docs/ENGINE_DELTA_CAMPAIGN.md; the
// live UI's applyEditDelta must be audibly indistinguishable from a full rebuild):
//   m1 delta-null <base.json> <mutated.json> <out_delta.wav> <out_fresh.wav>
// builds the BASE song's edit, delta-applies base->mutated, renders it; then builds
// the MUTATED song fresh and renders that. tools/edit_delta_null.py nulls the pair.
// Exit codes: 0 = both rendered (null judged upstream), 2 = delta REFUSED (the
// falsifier legs assert this — a refused class must never wrong-but-silently apply),
// 3 = parse failure, 1 = render failure. The sealed render/serve paths are untouched.
static int deltaNull (const juce::File& baseFile, const juce::File& mutFile,
                      const juce::File& outDelta, const juce::File& outFresh)
{
    juce::ScopedNoDenormals _noDenormals;
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);

    sotadaw::Song base;
    int err = 0;
    auto edit = loadSongEdit (engine, baseFile, base, err);
    if (edit == nullptr) return 3;
    sotadaw::Song mut;
    if (! sotadaw::parseSong (mutFile, mut))
    {
        std::cerr << "[m1] ERROR: cannot parse " << mutFile.getFullPathName() << "\n";
        return 3;
    }

    juce::String cls;
    const auto t0 = juce::Time::getHighResolutionTicks();
    if (! sotadaw::applyEditDelta (*edit, base, mut, &cls))
    {
        std::cout << "[m1] DELTA REFUSED\n";
        return 2;
    }
    std::cout << "[m1] delta applied class=" << cls << " ms="
              << juce::String (juce::Time::highResolutionTicksToSeconds (
                     juce::Time::getHighResolutionTicks() - t0) * 1000.0, 2) << "\n";
    juce::MessageManager::getInstance()->runDispatchLoopUntil (25);   // clip edits settle

    // render the delta-applied edit — renderCore's exact bits law, mutes from MUTATED
    auto renderIt = [] (te::Edit& e, const sotadaw::Song& s, const juce::File& out)
    {
        out.deleteFile();
        juce::BigInteger bits;
        auto all = te::getAllTracks (e);
        auto audio = te::getAudioTracks (e);
        for (int j = 0; j < all.size(); ++j)
            for (int a = 0; a < audio.size(); ++a)
                if (all[j] == audio[a] && ! (a < (int) s.tracks.size() && s.tracks[(size_t) a].muted))
                    bits.setBit (j);
        const auto range = te::TimeRange (0_tp, e.getLength());
        const bool ok = te::Renderer::renderToFile ("render", out, e, range, bits, true, true, {}, false);
        std::cout << "[m1] renderToFile ok=" << (ok ? 1 : 0) << " bytes=" << out.getSize()
                  << " -> " << out.getFullPathName() << "\n";
        return ok && out.getSize() > 1000;
    };
    if (! renderIt (*edit, mut, outDelta)) return 1;

    sotadaw::Song mut2;
    auto fresh = loadSongEdit (engine, mutFile, mut2, err);
    if (fresh == nullptr) return 3;
    if (! renderIt (*fresh, mut2, outFresh)) return 1;
    return 0;
}

// renderAbortable — the EXACT body of te::Renderer::renderToFile (the sealed
// path: same Parameters, same scoped wrappers, same public createAcidInfo) with
// ONE addition: the runJob loop polls a cancel flag and signals the task to
// exit. The DETERMINISM SEAL legs prove this replica byte-true against the
// classic overload; a cancelled partial is DELETED (a half-render is not a
// render). Returns 0 ok, 4 cancelled, else loadSongEdit's error codes.
static int renderAbortable (te::Engine& engine, const juce::File& songFile,
                            const juce::File& outFile, std::atomic<bool>& cancelFlag)
{
    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;
    outFile.deleteFile();
    juce::BigInteger bits;
    auto all = te::getAllTracks (*edit);
    auto audio = te::getAudioTracks (*edit);
    for (int j = 0; j < all.size(); ++j)
        for (int a = 0; a < audio.size(); ++a)
            if (all[j] == audio[a] && ! (a < (int) song.tracks.size() && song.tracks[(size_t) a].muted))
                bits.setBit (j);
    const auto range = te::TimeRange (0_tp, edit->getLength());
    bool ok = false;
    {
        const te::Edit::ScopedRenderStatus srs (*edit, true);
        te::Track::Array tracks;
        for (auto bit = bits.findNextSetBit (0); bit != -1; bit = bits.findNextSetBit (bit + 1))
            tracks.add (te::getAllTracks (*edit)[bit]);
        const te::FreezePointPlugin::ScopedTrackSoloIsolator isolator (*edit, tracks);
        const te::Renderer::ScopedClipSlotDisabler slotDisabler (*edit, tracks);
        te::TransportControl::stopAllTransports (engine, false, true);
        te::Renderer::turnOffAllPlugins (*edit);
        if (bits.countNumberOfSetBits() > 0)
        {
            te::Renderer::Parameters r (*edit);
            r.destFile = outFile;
            r.audioFormat = engine.getAudioFileFormatManager().getDefaultFormat();
            r.bitDepth = 24;
            r.sampleRateForAudio = engine.getDeviceManager().getSampleRate();
            r.blockSizeForAudio  = engine.getDeviceManager().getBlockSize();
            r.time = range;
            r.usePlugins = true;
            r.useMasterPlugins = true;
            r.tracksToDo = bits;
            r.createMidiFile = outFile.hasFileExtension (".mid");
            if (r.destFile.hasFileExtension (".wav") && r.endAllowance == te::TimeDuration())
                r.metadata.addArray (te::createAcidInfo (*edit, r.time));
            if (auto task = te::render_utils::createRenderTask (r, "serve", nullptr, nullptr))
            {
                while (task->runJob() == juce::ThreadPoolJob::jobNeedsRunningAgain)
                    if (cancelFlag.load() && ! task->shouldExit())
                        task->signalJobShouldExit();
            }
        }
        te::Renderer::turnOffAllPlugins (*edit);
        ok = outFile.existsAsFile();
    }
    if (cancelFlag.load())
    {
        outFile.deleteFile();
        std::cout << "[m1] render CANCELLED\n";
        return 4;
    }
    std::cout << "[m1] renderToFile ok=" << (ok ? 1 : 0) << " bytes=" << outFile.getSize()
              << " -> " << outFile.getFullPathName() << "\n";
    if (ok && outFile.existsAsFile())
    {
        juce::FileInputStream fis (outFile);
        std::cout << "[m1] render_sha256=" << juce::SHA256 (fis).toHexString()
                  << " file=" << outFile.getFileName() << "\n";
    }
    const bool emptySong = edit->getLength().inSeconds() <= 0.0;
    if (emptySong)
        std::cout << "[m1] empty song - nothing to render yet\n";
    return (ok && (outFile.getSize() > 1000 || emptySong)) ? 0 : 1;
}

static int serveRenders()
{
    // THE WARM SERVER — the last latency lever: cold renders paid process spawn
    // + engine init (~1-2s) EVERY time; here ONE engine stays alive and answers
    // renders over a JSON-lines protocol. stdin: {"song":path,"out":path} per
    // line ("quit"/EOF ends). stdout: the usual [m1] chatter, then EXACTLY ONE
    // protocol line per request starting {"ok": — clients read to that marker.
    // Per-request edits are discarded; te caches + JIT'd Faust voices stay warm.
    // DETERMINISM LAW: a served render must byte-match a spawned one — the same
    // renderCore runs; tools/render_serve_battery.py seals it before adoption.
    juce::ScopedNoDenormals _noDenormals;
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);
    // PROTOCOL v2 (cancellable): a reader THREAD consumes stdin continuously so
    // {"cancel":id} reaches an IN-FLIGHT render; requests queue and render
    // serialized on this thread via renderAbortable. Replies keep the v1 shape
    // ({"ok":...} first — clients match that prefix) + additive id/cancelled.
    std::mutex mx, outMx;
    std::condition_variable cv;
    std::deque<juce::var> pending;
    bool done = false;
    std::atomic<bool> cancelFlag { false };
    std::atomic<long long> activeId { -1 };
    auto reply = [&outMx] (const juce::String& s)
    {
        const std::lock_guard<std::mutex> l (outMx);
        std::cout << s << "\n" << std::flush;
    };
    std::cout << "[m1] serve ready (cancellable)\n" << std::flush;
    std::thread reader ([&]
    {
        std::string line;
        while (std::getline (std::cin, line))
        {
            if (line == "quit") break;
            if (line.empty()) continue;
            const auto v = juce::JSON::parse (juce::String (line));
            if (! v.isObject())
            {
                reply ("{\"ok\":0,\"err\":\"bad json\"}");
                continue;
            }
            if (! v.getProperty ("cancel", juce::var()).isVoid())
            {
                const auto cid = (long long) (double) v.getProperty ("cancel", -1.0);
                if (cid == activeId.load())
                    cancelFlag.store (true);
                else   // late/unknown cancel: benign, the moment already passed
                    reply ("{\"ok\":0,\"id\":" + juce::String (cid)
                           + ",\"cancelled\":0,\"err\":\"not active\"}");
                continue;
            }
            {
                const std::lock_guard<std::mutex> l (mx);
                pending.push_back (v);
            }
            cv.notify_one();
        }
        {
            const std::lock_guard<std::mutex> l (mx);
            done = true;
        }
        cv.notify_one();
    });
    long long autoId = 0;
    while (true)
    {
        juce::var v;
        {
            std::unique_lock<std::mutex> l (mx);
            cv.wait (l, [&] { return done || ! pending.empty(); });
            if (pending.empty())
                break;
            v = pending.front();
            pending.pop_front();
        }
        const juce::File sf (v.getProperty ("song", "").toString());
        const juce::File of (v.getProperty ("out", "").toString());
        const auto idv = v.getProperty ("id", juce::var());
        const long long id = idv.isVoid() ? ++autoId : (long long) (double) idv;
        cancelFlag.store (false);
        activeId.store (id);
        int rc = 3;
        if (sf.existsAsFile())
            rc = renderAbortable (engine, sf, of, cancelFlag);
        activeId.store (-1);
        juce::String sha;
        if (rc == 0 && of.existsAsFile())
        {
            juce::FileInputStream fis (of);
            sha = juce::SHA256 (fis).toHexString();
        }
        reply ("{\"ok\":" + juce::String (rc == 0 ? 1 : 0)
               + ",\"id\":" + juce::String (id)
               + ",\"cancelled\":" + juce::String (rc == 4 ? 1 : 0)
               + ",\"sha\":\"" + sha + "\"}");
    }
    reader.join();
    return 0;
}

// paint every Faust plugin face in a song to PNGs — the agent SEES the faces
// it designed (uismoke can't: FaustFace needs a live engine plugin; m1 has one).
static int renderFaces (const juce::File& songFile, const juce::File& outDir)
{
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);
    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;
    outDir.createDirectory();
    auto audio = te::getAudioTracks (*edit);
    int made = 0;
    for (int i = 0; i < audio.size() && i < (int) song.tracks.size(); ++i)
        for (auto* p : audio[i]->pluginList.getPlugins())
        {
            juce::String dsp;
            std::unique_ptr<juce::Component> face;
            if (auto* fi = dynamic_cast<FaustInstrumentPlugin*> (p))
            {
                fi->prepareZones();
                dsp = fi->dspName.get();
                face.reset (new faces::FaustFace (*fi, dsp, song.tracks[(size_t) i].name));
            }
            else if (auto* fx = dynamic_cast<FaustFxPlugin*> (p))
            {
                fx->prepareZones();
                dsp = fx->dspName.get();
                face.reset (new faces::FaustFace (*fx, dsp, song.tracks[(size_t) i].name));
            }
            if (face == nullptr) continue;
            juce::Image img (juce::Image::ARGB, face->getWidth(), face->getHeight(), true);
            {
                juce::Graphics g (img);
                face->paintEntireComponent (g, false);
            }
            juce::PNGImageFormat png;
            auto out = outDir.getChildFile (song.tracks[(size_t) i].name + "_" + dsp + ".png");
            out.deleteFile();
            juce::FileOutputStream os (out);
            if (os.openedOk() && png.writeImageToStream (img, os))
            {
                std::cout << "[faces] " << out.getFileName() << " "
                          << face->getWidth() << "x" << face->getHeight() << "\n";
                ++made;
            }
        }
    std::cout << "[faces] wrote " << made << "\n";
    return made > 0 ? 0 : 1;
}

static int renderStems (const juce::File& songFile, const juce::File& outDir)
{
    juce::ScopedNoDenormals _noDenormals;      // P6 (E10): denormal flush, see renderSong
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);

    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;

    outDir.createDirectory();
    const auto range = te::TimeRange (0_tp, edit->getLength() );
    auto all = te::getAllTracks (*edit);
    auto audio = te::getAudioTracks (*edit);

    int i = 0;
    for (auto* at : audio)
    {
        juce::BigInteger bits;
        for (int j = 0; j < all.size(); ++j)
            if (all[j] == at) bits.setBit (j);
        auto f = outDir.getChildFile (juce::String::formatted ("%02d_", i) + at->getName() + ".wav");
        f.deleteFile();
        const bool ok = te::Renderer::renderToFile ("stem", f, *edit, range, bits, true, true, {}, false);
        std::cout << "[m1] stem " << f.getFileName() << " ok=" << (ok ? 1 : 0)
                  << " bytes=" << f.getSize() << "\n";
        if (ok && f.existsAsFile())
        {
            juce::FileInputStream fis (f);
            std::cout << "[m1] render_sha256=" << juce::SHA256 (fis).toHexString()
                      << " file=" << f.getFileName() << "\n";
        }
        ++i;
    }
    return 0;
}

static int listParams (const juce::File& songFile)
{
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);

    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;

    juce::Array<juce::var> out;
    auto dumpPlugins = [&out] (const juce::String& trackName, const te::Plugin::Array& plugins)
    {
        for (auto plugin : plugins)
        {
            if (std::getenv ("SOTADAW_FX_DEBUG") != nullptr)
                std::fprintf (stderr, "[fxdbg] dump %s/%s @%p: %d params\n",
                              trackName.toRawUTF8(), plugin->getName().toRawUTF8(),
                              (void*) plugin, plugin->getAutomatableParameters().size());
            for (auto ap : plugin->getAutomatableParameters())
            {
                auto* o = new juce::DynamicObject();
                o->setProperty ("track", trackName);
                o->setProperty ("plugin", plugin->getName());
                o->setProperty ("param", ap->paramID);
                o->setProperty ("name", ap->getParameterName());
                o->setProperty ("value", ap->getCurrentValue());
                const auto r = ap->getValueRange();
                o->setProperty ("min", r.getStart());
                o->setProperty ("max", r.getEnd());
                out.add (juce::var (o));
            }
        }
    };
    for (auto* at : te::getAudioTracks (*edit))
        dumpPlugins (at->getName(), at->pluginList.getPlugins());
    dumpPlugins ("master", edit->getMasterPluginList().getPlugins());

    std::cout << "PARAMS_JSON " << juce::JSON::toString (juce::var (out), true) << "\n";
    return 0;
}

// Tracktion logs its whole device-enumeration to stdout by default — silence it
// (the CLI's contract is [m1]-prefixed lines + machine-readable payloads only).
struct QuietLogger : juce::Logger { void logMessage (const juce::String&) override {} };

// list a hosted vst3's PROGRAMS (factory preset bank, if the plugin exposes one):
// the rail for use_preset-by-name across the whole VST universe — probe before schema.
static int listPrograms (const juce::File& songFile, const juce::String& trackName)
{
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);
    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;
    for (auto* at : te::getAudioTracks (*edit))
    {
        if (at->getName() != trackName) continue;
        for (auto plugin : at->pluginList)
            if (auto* ep = dynamic_cast<te::ExternalPlugin*> (plugin))
                if (auto* inst = ep->getAudioPluginInstance())
                {
                    juce::Array<juce::var> names;
                    for (int i = 0; i < inst->getNumPrograms(); ++i)
                        names.add (inst->getProgramName (i).trim());
                    std::cout << "[m1] '" << ep->getName() << "' programs: "
                              << inst->getNumPrograms() << "\n"
                              << "PROGRAMS_JSON " << juce::JSON::toString (juce::var (names), true) << "\n";
                    return 0;
                }
        std::cerr << "[m1] no external plugin on track '" << trackName << "'\n";
        return 1;
    }
    std::cerr << "[m1] no track '" << trackName << "'\n";
    return 1;
}

// capture a vst3 track's live plugin state -> reusable .preset blob (OUR patch format):
// the agent tweaks params, captures, and the design persists in song.json via source.preset
static int captureState (const juce::File& songFile, const juce::String& trackName,
                         const juce::File& outFile)
{
    te::Engine engine { "sotadaw", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);
    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;
    for (auto* at : te::getAudioTracks (*edit))
    {
        if (at->getName() != trackName) continue;
        for (auto plugin : at->pluginList)
            if (auto* ep = dynamic_cast<te::ExternalPlugin*> (plugin))
                if (auto* inst = ep->getAudioPluginInstance())
                {
                    juce::MemoryBlock blob;
                    inst->getStateInformation (blob);
                    outFile.getParentDirectory().createDirectory();
                    outFile.replaceWithData (blob.getData(), blob.getSize());
                    std::cout << "[m1] captured " << (int) blob.getSize() << " bytes of '"
                              << ep->getName() << "' state -> " << outFile.getFullPathName() << "\n";
                    return 0;
                }
        std::cerr << "[m1] no external plugin on track '" << trackName << "'\n";
        return 1;
    }
    std::cerr << "[m1] no track '" << trackName << "'\n";
    return 1;
}

static int listLauncher (const juce::File& songFile)
{
    te::Engine engine { "m1", nullptr, std::make_unique<sotadaw::SotadawEngineBehaviour>() };
    sotadaw::registerSotadawPlugins (engine);
    sotadaw::loadKnownPlugins (engine);
    sotadaw::Song song;
    int err = 0;
    auto edit = loadSongEdit (engine, songFile, song, err);
    if (edit == nullptr) return err;
    int scene = 0;
    for (auto* tr : te::getAudioTracks (*edit))
        for (auto* slot : tr->getClipSlotList().getClipSlots())
            if (auto* c = slot->getClip())
            {
                juce::String fol;
                if (auto* acts = c->getFollowActions())
                    for (auto* a : acts->getActions())
                        fol << (fol.isEmpty() ? "" : " | ")
                            << te::toString (a->action.get()) << " w" << juce::String ((double) a->weight.get());
                if (fol.isEmpty()) fol = "-";
                std::cout << "[launcher] track='" << tr->getName() << "' clip='" << c->getName()
                          << "' follow=" << fol << "\n";
                ++scene;
            }
    std::cout << "[launcher] total clips " << scene << "\n";
    return 0;
}

// R4 hotplug rig: a VIRTUAL ALSA midi source (new seq client) appearing out of
// nowhere — exactly what plugging a cable does to the announce port. The driver
// (tools/hotplug_e2e.py) races the app's watcher against MIDISRC_UP.
static int midiSrc (const juce::String& name, int seconds, int everyMs)
{
    auto out = juce::MidiOutput::createNewDevice (name);
    if (out == nullptr)
    {
        std::cout << "midi-src: createNewDevice failed\n";
        return 1;
    }
    std::cout << "MIDISRC_UP t_ms=" << juce::Time::currentTimeMillis()
              << " name=\"" << name << "\"\n" << std::flush;
    const auto tEnd = juce::Time::currentTimeMillis() + (juce::int64) seconds * 1000;
    int n = 0;
    while (juce::Time::currentTimeMillis() < tEnd)
    {   // keep firing: the watcher must enable+subscribe before notes flow, so
        // the first RECEIVED note (not the first sent) stamps plug->playing
        out->sendMessageNow (juce::MidiMessage::noteOn (1, 60 + (n % 12), (juce::uint8) 100));
        out->sendMessageNow (juce::MidiMessage::noteOff (1, 60 + (n % 12)));
        ++n;
        juce::Thread::sleep (everyMs);
    }
    std::cout << "MIDISRC_SENT n=" << n << "\n";
    return 0;
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI juceInit;
    QuietLogger quiet;
    juce::Logger::setCurrentLogger (&quiet);

    // EB1 THE SEAL (docs/THE_PHYSICS.md E1): m1 renders are content-addressed — pin the
    // BWAV origination stamp (engine patch 0002) and TZ so bytes hold across runs AND
    // machines. Callers may export their own epoch; the UI never sets it, so human
    // exports keep human timestamps.
    if (std::getenv ("SOTADAW_RENDER_EPOCH") == nullptr)
    {
        ::setenv ("SOTADAW_RENDER_EPOCH", "0", 1);
        ::setenv ("TZ", "UTC", 1);
        ::tzset();
    }

    // V49: a stale flight file means the last session died inside a plugin op
    if (const auto q = sotadaw::PluginGuard::promoteStaleFlight(); q.isNotEmpty())
        std::cerr << "[guard] last session died inside plugin '" << q
                  << "' — quarantined (retry: delete "
                  << sotadaw::PluginGuard::quarantineFile().getFullPathName() << ")\n";

    const juce::String cmd = argc >= 2 ? argv[1] : "";

    const int rc = cmd == "instruments" ? listInstruments()
                 : cmd == "scan-plugins" ? scanPlugins()
                 : cmd == "resave" && argc >= 4 ? ([] (const juce::File& in, const juce::File& out)
                   {   // schema round-trip surface: load -> serialize -> write (battery food)
                       sotadaw::Song song;
                       if (! sotadaw::parseSong (in, song)) return 1;
                       out.replaceWithText (juce::JSON::toString (sotadaw::songToVar (song)));
                       std::cout << "[m1] resave ok -> " << out.getFullPathName() << "\n";
                       return 0;
                   }) (juce::File (argv[2]), juce::File (argv[3]))
                 : cmd == "render" && argc >= 4 ? renderSong (juce::File (argv[2]), juce::File (argv[3]))
                 : cmd == "delta-null" && argc >= 6 ? deltaNull (juce::File (argv[2]), juce::File (argv[3]),
                                                                juce::File (argv[4]), juce::File (argv[5]))
                 : cmd == "serve" ? serveRenders()
                 : cmd == "render-stems" && argc >= 4 ? renderStems (juce::File (argv[2]), juce::File (argv[3]))
                 : cmd == "faces" && argc >= 4 ? renderFaces (juce::File (argv[2]), juce::File (argv[3]))
                 : cmd == "list-params" && argc >= 3 ? listParams (juce::File (argv[2]))
                 : cmd == "list-launcher" && argc >= 3 ? listLauncher (juce::File (argv[2]))
                 : cmd == "capture-state" && argc >= 5 ? captureState (juce::File (argv[2]), argv[3], juce::File (argv[4]))
                 : cmd == "list-programs" && argc >= 4 ? listPrograms (juce::File (argv[2]), argv[3])
                 : cmd == "midi-src" && argc >= 3 ? midiSrc (argv[2],
                                                             argc >= 4 ? atoi (argv[3]) : 4,
                                                             argc >= 5 ? atoi (argv[4]) : 40)
                 : bootCheck();
    juce::Logger::setCurrentLogger (nullptr);
    return rc;
}
