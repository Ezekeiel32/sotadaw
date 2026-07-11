// THE ENGINE DELTA (docs/ENGINE_DELTA_CAMPAIGN.md) — kill the last freeze class.
//
// applyEditDelta (edit, oldS, newS): mutate a live te::Edit that was built from oldS
// so it becomes what buildEdit (newS) would build — WITHOUT tearing down the plugin
// world — but ONLY when every difference between the two songs is one this function
// can prove it applied. Anything else returns false with the edit UNTOUCHED (the plan
// phase collects ops without mutating; the residue check runs before the first op),
// and the caller falls back to today's full rebuild. Honesty first.
//
// Delta classes (cheapest first, per docs/ENGINE_DELTA_CAMPAIGN.md):
//   notes    — rewrite ONE track's timeline MidiClip sequence in place (the 80% accept)
//   mix      — track gainDb/pan/muted, bus gainDb, masterGainDb (live setters)
//   name     — track rename (engine-side label only)
//   srcparam — faust source zone values (same instrument; keys may be added, never removed)
//   fxparam  — plain faust fx zone values (same chain shape; tracks, buses, master)
//   send     — send gainDb (same send topology)
//   noop     — the songs differ only in fields buildEdit never reads (provenance,
//              _loop, sections, track color/locked/groove) — true with zero ops
//   trackadd    — class 6a: NEW tracks appended at the end (the agent's standard
//                 move), built exactly like buildEdit's loop, inserted before the
//                 bus tracks; composes with prefix deltas. Suffix-only; clip-free,
//                 slot-free, automation-free newcomers; no launcher scenes.
//   trackremove — class 6b: newS is an exact SUBSEQUENCE of oldS (kept tracks
//                 byte-identical after masks) — removal ops only, never combined
//                 with tweaks. Callers that run class-6 must follow with
//                 rebuildLanes/closePluginWindows (see allowTrackShape).
//   fxshape   — class 5a: ONE host's fx chain reshaped (add/remove/reorder/param
//               rewrites incl. removed keys + eq/comp) — the doomed slots are
//               TYPE-VERIFIED against the old list at positions 1..n before the
//               plan is legal, then the chain is rebuilt exactly like buildEdit
//               (tracks + buses; master chain refuses — the wall lives there).
//               Refuses when any fx entry is vst3: (can be null at build => the
//               positional law breaks) or when fx[i] automation exists.
//   srcswap   — class 5b: faust voice -> different faust voice (or removed source
//               param keys): slot-0 plugin replaced via buildTrackSource's exact
//               faust branch. Refuses non-faust kinds and source.* automation.
//   autocurve — class 7: automation[] deltas (track gainDb/pan/source./fx[ and
//               song masterGainDb/master[) — changed targets clear + re-add
//               points via addAutomationCurve's exact law; target REMOVAL is
//               allowed only where the static base is restorable (gainDb / pan /
//               masterGainDb); resolution mirrors resolveAutoTarget on the live
//               lists, and a mirror it cannot build faithfully refuses.
//
// Refused by design (full rebuild is CORRECT there): track reorders + mid-list
// inserts + remove-and-tweak combos, bus add/remove, master chain shape, vst3
// source/fx swaps and vst3 param changes (natural-unit conversion + quarantine
// state are buildEdit's job), sample-kit swaps, removed-key zone tweaks OUTSIDE
// a chain/source rebuild, automation removal of zone targets, audioClips,
// launcher slots, tempo/swing/key/lengthBars, sceneNames — and ANY song
// containing fx_retune (its chord grid is compiled from the WHOLE song at
// build time; a delta near it risks a stale grid).
//
// m1 renders NEVER use this (the sealed render path stays byte-identical by
// construction; engine_null_ci untouched). The proof organ is m1's hidden
// `delta-null` verb + tools/edit_delta_null.py: a delta-applied edit and a fresh
// buildEdit of the mutated song must render to a NULL pair; refused classes must
// exit 2, never wrong-but-silent.
//
// EQUALITY IS THE SERIALIZER'S: the residue check serializes both songs through
// songToVar, removes exactly the fields the collected ops account for (plus the
// audio-irrelevant set above), and requires the remaining JSON to match byte-for-
// byte. A Song field added tomorrow forces a fallback the moment it differs —
// unknown differences can never slip through silently.
#pragma once
#include "SongLoader.h"
#include <functional>

namespace sotadaw
{

inline bool edNotesEqual (const std::vector<SongNote>& x, const std::vector<SongNote>& y)
{
    if (x.size() != y.size()) return false;
    for (size_t i = 0; i < x.size(); ++i)
        if (x[i].start != y[i].start || x[i].len != y[i].len || x[i].pitch != y[i].pitch
            || x[i].vel != y[i].vel || x[i].chance != y[i].chance)
            return false;
    return true;
}

// zone-value delta: keys may be added (the zone sat at its .dsp default) or changed,
// never removed (the default is unknowable without recompiling the voice)
inline bool edParamsDelta (const std::map<juce::String, float>& oldP,
                           const std::map<juce::String, float>& newP,
                           std::vector<std::pair<juce::String, float>>& changed)
{
    for (auto& [k, v] : oldP)
        if (newP.find (k) == newP.end())
            return false;
    for (auto& [k, v] : newP)
    {
        auto it = oldP.find (k);
        if (it == oldP.end() || it->second != v)
            changed.push_back ({ k, v });
    }
    return true;
}

// an fx entry whose live engine twin is a FaustFxPlugin with settable zones
inline bool edIsPlainFaustFx (const SongFx& f)
{
    return f.type == "faustfx"
        && ! f.id.startsWith ("vst3:") && ! f.id.startsWith ("nam:")
        && ! f.id.startsWith ("clap:") && f.id != "fx_retune";
}

// allowTrackShape: class-6 add/remove ops leave lane meters / plugin windows /
// launcher cells to the CALLER's follow-up (rebuildLanes + closePluginWindows);
// call sites that don't run those must pass false so shape changes fall back.
inline bool applyEditDelta (te::Edit& edit, const Song& oldS, const Song& newS,
                            juce::String* classOut = nullptr, bool allowTrackShape = true)
{
    if (oldS.tracks.empty() || newS.tracks.empty()) return false;      // first build / teardown
    if (oldS.buses.size() != newS.buses.size()) return false;
    if (oldS.master.size() != newS.master.size()) return false;
    const size_t oldN = oldS.tracks.size(), newN = newS.tracks.size();
    if (oldN != newN && ! allowTrackShape) return false;

    // fx_retune compiles a chord grid from the WHOLE song (key + every other track's
    // notes) at build time — no delta may run near one
    auto hasRetune = [] (const Song& s)
    {
        for (auto& t : s.tracks) for (auto& f : t.fx) if (f.id == "fx_retune") return true;
        for (auto& b : s.buses)  for (auto& f : b.fx) if (f.id == "fx_retune") return true;
        for (auto& f : s.master) if (f.id == "fx_retune") return true;
        return false;
    };
    if (hasRetune (oldS) || hasRetune (newS)) return false;

    auto atracks = te::getAudioTracks (edit);
    if ((int) atracks.size() != (int) (oldS.tracks.size() + oldS.buses.size()))
        return false;                       // the edit is not the shape oldS promises

    std::vector<std::function<void()>> ops;
    juce::StringArray classes;
    auto addClass = [&classes] (const char* c) { if (! classes.contains (c)) classes.add (c); };

    // named locals — the JUCE var lifetime law
    auto va = songToVar (oldS);
    auto vb = songToVar (newS);
    auto* ra = va.getDynamicObject();
    auto* rb = vb.getDynamicObject();
    if (ra == nullptr || rb == nullptr) return false;

    // fields buildEdit never reads: masked unconditionally, so a provenance append
    // (every accept carries one) or a lane recolour can't force a full rebuild
    for (auto* r : { ra, rb })
        for (auto k : { "provenance", "_loop", "sections" })
            r->removeProperty (k);

    auto tracksVarA = ra->getProperty ("tracks");   // keep-alive copies: the REMOVE branch
    auto tracksVarB = rb->getProperty ("tracks");   // drops the root property under them
    auto* tarrA = tracksVarA.getArray();
    auto* tarrB = tracksVarB.getArray();
    if (tarrA == nullptr || tarrB == nullptr
        || tarrA->size() != (int) oldN || tarrB->size() != (int) newN)
        return false;

    auto trackObj = [] (juce::Array<juce::var>* arr, size_t i) -> juce::DynamicObject*
    { return arr->getReference ((int) i).getDynamicObject(); };
    auto maskT = [&] (size_t i, const char* prop)
    {
        for (auto* arr : { tarrA, tarrB })
            if (auto* o = trackObj (arr, i)) o->removeProperty (prop);
    };
    // mask "params" on the j-th entry of an fx array held under `prop` of object `o`
    auto maskFxParams = [] (juce::DynamicObject* o, const char* prop, size_t j)
    {
        if (o == nullptr) return;
        if (auto* fxa = o->getProperty (prop).getArray())
            if ((int) j < fxa->size())
                if (auto* fo = fxa->getReference ((int) j).getDynamicObject())
                    fo->removeProperty ("params");
    };

    // shared fx-params planner: same chain shape required; plain faust zones only.
    // `plugs` = the FaustFxPlugin subsequence of the host's plugin list, in order.
    auto planFxList = [&] (const std::vector<SongFx>& fa, const std::vector<SongFx>& fb,
                           const std::vector<FaustFxPlugin*>& plugs,
                           std::function<void (size_t)> maskParamsAt) -> bool
    {
        if (fa.size() != fb.size()) return false;
        int plainCount = 0;
        for (auto& f : fa) if (edIsPlainFaustFx (f)) ++plainCount;
        int jj = -1;
        for (size_t j = 0; j < fa.size(); ++j)
        {
            if (edIsPlainFaustFx (fa[j])) ++jj;
            if (fa[j].id != fb[j].id || fa[j].type != fb[j].type
                || fa[j].preset != fb[j].preset || fa[j].bypass != fb[j].bypass)
                return false;
            if (fa[j].params == fb[j].params) continue;
            if (! edIsPlainFaustFx (fa[j])) return false;       // vst3/nam/clap/eq/comp: rebuild's job
            if ((int) plugs.size() != plainCount) return false; // census: an insert failed at build
            std::vector<std::pair<juce::String, float>> changed;
            if (! edParamsDelta (fa[j].params, fb[j].params, changed)) return false;
            auto* plug = plugs[(size_t) jj];
            ops.push_back ([plug, changed] { for (auto& [k, v] : changed) plug->setZone (k, v); });
            addClass ("fxparam");
            maskParamsAt (j);
        }
        return true;
    };
    auto faustFxOf = [] (te::Track& tr)
    {
        std::vector<FaustFxPlugin*> out;
        for (auto p : tr.pluginList.getPlugins())
            if (auto* f = dynamic_cast<FaustFxPlugin*> (p)) out.push_back (f);
        return out;
    };

    // a live plugin at an fx slot must BE the old list's entry before it may be doomed
    auto liveFxMatches = [] (te::Plugin* p, const SongFx& f) -> bool
    {
        if (edIsPlainFaustFx (f))
        {
            auto* fp = dynamic_cast<FaustFxPlugin*> (p);
            return fp != nullptr && fp->dspName == f.id;
        }
        if (f.type == "eq")            return dynamic_cast<te::EqualiserPlugin*> (p) != nullptr;
        if (f.type == "comp")          return dynamic_cast<te::CompressorPlugin*> (p) != nullptr;
        if (f.id.startsWith ("nam:"))  return dynamic_cast<NamPlugin*> (p)  != nullptr;
        if (f.id.startsWith ("clap:")) return dynamic_cast<ClapPlugin*> (p) != nullptr;
        return false;
    };
    // kinds whose engine twin instantiates DETERMINISTICALLY (vst3 can be null at
    // build — quarantine / missing scan — which would shift the positional law)
    auto edFxDeltaSafe = [] (const SongFx& f)
    {
        return edIsPlainFaustFx (f) || f.type == "eq" || f.type == "comp"
            || f.id.startsWith ("nam:") || f.id.startsWith ("clap:");
    };

    // ---- class 5a planner: rebuild ONE host's fx chain in place. Layout law
    // (buildEdit): slot 0 = the host's anchor (source plugin / vol on audio lanes /
    // AuxReturn on buses), fx occupy 1..n, sends and vol ride AFTER — deleting the
    // doomed slots and re-inserting at 1.. lands the new chain exactly where a
    // fresh build would. anchorOk verifies slot 0 so a build-time source miss
    // (failed vst3 instrument) can never shift the knife one slot left.
    auto planFxShape = [&] (te::Track& tr,
                            const std::vector<SongFx>& fa, const std::vector<SongFx>& fb,
                            std::function<bool (te::Plugin*)> anchorOk,
                            const std::vector<SongAuto>* autoA, const std::vector<SongAuto>* autoB,
                            std::function<void()> maskWhole) -> bool
    {
        auto anyFxAuto = [] (const std::vector<SongAuto>* v)
        {
            if (v != nullptr)
                for (auto& a : *v)
                    if (a.target.startsWith ("fx[")) return true;
            return false;
        };
        if (anyFxAuto (autoA) || anyFxAuto (autoB)) return false;  // curves ride doomed plugins
        for (auto& f : fa) if (! edFxDeltaSafe (f)) return false;
        for (auto& f : fb) if (! edFxDeltaSafe (f)) return false;
        auto live = tr.pluginList.getPlugins();
        if (live.size() < (int) fa.size() + 1) return false;
        if (! anchorOk (live[0].get())) return false;
        std::vector<te::Plugin::Ptr> doomed;                       // Ptrs: alive until the op runs
        for (size_t j = 0; j < fa.size(); ++j)
        {
            if (! liveFxMatches (live[(int) j + 1].get(), fa[j])) return false;
            doomed.push_back (live[(int) j + 1]);
        }
        ops.push_back ([&edit, trp = &tr, doomed, newFx = fb]
        {
            for (auto& p : doomed) p->deleteFromParent();
            int idx = 1;                                           // buildEdit's fxIndex law
            for (auto& fx : newFx)
                trp->pluginList.insertPlugin (makeFaustFx (edit, fx), idx++, nullptr);
        });
        addClass ("fxshape");
        maskWhole();
        return true;
    };

    // ---- class 7 planner: automation[] deltas. Entries are grouped per target;
    // a target whose entry-set changed gets clear + re-add through the SAME
    // addAutomationCurve law buildEdit uses. resolve() mirrors resolveAutoTarget
    // on the live lists — it returns feasible=false when the mirror itself cannot
    // be trusted (vst3 in the fx list, anchor mismatch), which refuses the delta;
    // a param that resolves to null FEASIBLY is skipped exactly like buildEdit's
    // errors<< path skips it. planRemoval restores the static base where that is
    // derivable (gainDb / pan / masterGainDb) and refuses everything else.
    auto planAutos = [&] (const std::vector<SongAuto>& aa, const std::vector<SongAuto>& ab,
                          std::function<te::AutomatableParameter* (const juce::String&, bool&, bool&)> resolve,
                          std::function<bool (const juce::String&)> planRemoval,
                          std::function<void()> maskWhole) -> bool
    {
        auto serOf = [] (const std::vector<SongAuto>& v, const juce::String& target)
        {
            juce::String s;
            for (auto& a : v)
                if (a.target == target)
                {
                    std::vector<SongAuto> one { a };
                    s << juce::JSON::toString (automationToVar (one));
                }
            return s;
        };
        juce::StringArray targets;
        for (auto& a : aa) targets.addIfNotAlreadyThere (a.target);
        for (auto& a : ab) targets.addIfNotAlreadyThere (a.target);
        for (auto& tgt : targets)
        {
            if (serOf (aa, tgt) == serOf (ab, tgt)) continue;      // curve already right
            bool isVolDb = false, feasible = true;
            auto* param = resolve (tgt, isVolDb, feasible);
            if (! feasible) return false;
            if (param == nullptr) continue;      // buildEdit would error<< and skip too
            std::vector<SongAuto> entries;
            for (auto& a : ab) if (a.target == tgt) entries.push_back (a);
            if (entries.empty())
            {
                if (! planRemoval (tgt)) return false;
                ops.push_back ([param] { param->getCurve().clear (nullptr); });
            }
            else
                ops.push_back ([&edit, param, entries, isVolDb]
                {
                    param->getCurve().clear (nullptr);
                    for (auto& a : entries)
                        addAutomationCurve (edit, param, a, isVolDb);
                });
            addClass ("autocurve");
        }
        maskWhole();
        return true;
    };

    // ---- class 6b: track REMOVAL — the exact-subsequence law. Kept tracks must be
    // byte-identical (after the audio-irrelevant masks); anything else — reorders,
    // remove-and-tweak combos — is a rebuild's job. Ops capture track POINTERS, so
    // later deletions never shift under earlier ones.
    bool tracksHandled = false;
    if (newN < oldN)
    {
        for (auto* arr : { tarrA, tarrB })
            for (int i = 0; i < arr->size(); ++i)
                if (auto* o = trackObj (arr, (size_t) i))
                    for (auto k : { "color", "locked", "groove" })
                        o->removeProperty (k);
        std::vector<te::AudioTrack*> doomed;
        size_t j = 0;
        for (size_t i = 0; i < oldN; ++i)
        {
            if (j < newN && juce::JSON::toString (tarrA->getReference ((int) i))
                              == juce::JSON::toString (tarrB->getReference ((int) j)))
                ++j;
            else
                doomed.push_back (atracks[(int) i]);
        }
        if (j != newN) return false;
        for (auto* tr : doomed)
            ops.push_back ([&edit, tr] { edit.deleteTrack (tr); });
        addClass ("trackremove");
        ra->removeProperty ("tracks");   // every kept track proven equal by the match;
        rb->removeProperty ("tracks");   // the doomed ones are accounted by the ops
        tracksHandled = true;
    }

    for (size_t i = 0; ! tracksHandled && i < oldN; ++i)
    {
        const auto& ta = oldS.tracks[i];
        const auto& tb = newS.tracks[i];
        auto* tr = atracks[(int) i];

        // UI-only fields — buildEdit never reads them
        maskT (i, "color"); maskT (i, "locked"); maskT (i, "groove");

        if (ta.name != tb.name)
        {
            ops.push_back ([tr, nm = tb.name] { tr->setName (nm); });
            addClass ("name"); maskT (i, "name");
        }

        auto* vol = tr->getVolumePlugin();
        if (ta.gainDb != tb.gainDb)
        {
            if (vol == nullptr) return false;
            ops.push_back ([vol, v = (float) tb.gainDb] { vol->setVolumeDb (v); });
            addClass ("mix"); maskT (i, "gainDb");
        }
        if (ta.pan != tb.pan)
        {
            if (vol == nullptr) return false;
            ops.push_back ([vol, v = (float) tb.pan] { vol->setPan (v); });
            addClass ("mix"); maskT (i, "pan");
        }
        if (ta.muted != tb.muted)
        {
            ops.push_back ([tr, m = tb.muted] { tr->setMute (m); });
            addClass ("mix"); maskT (i, "muted");
        }

        if (! edNotesEqual (ta.notes, tb.notes))
        {
            // synth-backed lanes only; the clip census must match what buildEdit(oldS)
            // created: exactly one timeline MidiClip iff oldS had notes
            if (tb.source.kind != "faust" && tb.source.kind != "sample" && tb.source.kind != "vst3")
                return false;
            te::MidiClip* mc = nullptr;
            int found = 0;
            for (auto* c : tr->getClips())
                if (auto* m = dynamic_cast<te::MidiClip*> (c)) { mc = m; ++found; }
            if (found != (ta.notes.empty() ? 0 : 1)) return false;

            if (tb.notes.empty())
                ops.push_back ([mc] { mc->removeFromParent(); });
            else
                ops.push_back ([&edit, tr, mc, &newS, i]
                {
                    auto* clip = mc;
                    te::Clip::Ptr keepAlive;
                    if (clip == nullptr)     // oldS had no notes -> no clip yet
                    {
                        const auto end = edit.tempoSequence.toTime (
                            te::BeatPosition::fromBeats (newS.totalBeats() + 4.0));
                        auto made = tr->insertMIDIClip ({ te::TimePosition(), end }, nullptr);
                        keepAlive = made.get();
                        clip = made.get();
                    }
                    if (clip == nullptr) return;
                    auto& seq = clip->getSequence();
                    seq.clear (nullptr);
                    // EXACTLY buildEdit's insert law: chance dice index runs over ALL
                    // notes, swing shifts on-grid odd subdivisions, 1..127 velocity
                    int ni = 0;
                    for (auto& n : newS.tracks[i].notes)
                        if (noteIncluded (n, ni++))
                            seq.addNote (n.pitch,
                                         te::BeatPosition::fromBeats (applySwing (n.start, newS)),
                                         te::BeatDuration::fromBeats (n.len),
                                         juce::jlimit (1, 127, (int) std::lround (n.vel * 127.0)),
                                         0, nullptr);
                });
            addClass ("notes"); maskT (i, "notes");
        }

        if (ta.source.kind != tb.source.kind || ta.source.id != tb.source.id
            || ta.source.preset != tb.source.preset || ta.source.params != tb.source.params)
        {
            if (ta.source.kind != "faust" || tb.source.kind != "faust") return false;
            std::vector<std::pair<juce::String, float>> changed;
            FaustInstrumentPlugin* fip = nullptr;
            for (auto p : tr->pluginList.getPlugins())
                if ((fip = dynamic_cast<FaustInstrumentPlugin*> (p)) != nullptr) break;

            if (ta.source.id == tb.source.id && ta.source.preset == tb.source.preset
                && fip != nullptr && edParamsDelta (ta.source.params, tb.source.params, changed))
            {
                // cheapest: same voice, zones added/changed — set them live
                ops.push_back ([fip, changed] { for (auto& [k, v] : changed) fip->setZone (k, v); });
                addClass ("srcparam");
                for (auto* arr : { tarrA, tarrB })
                    if (auto* o = trackObj (arr, i))
                        if (auto* so = o->getProperty ("source").getDynamicObject())
                            so->removeProperty ("params");
            }
            else
            {
                // class 5b: replace the slot-0 voice via buildTrackSource's exact
                // faust branch. Covers id swaps AND removed param keys (the fresh
                // plugin starts at .dsp defaults). source.* curves would ride the
                // doomed plugin — automation targeting it refuses.
                for (auto* av : { &ta.automation, &tb.automation })
                    for (auto& a : *av)
                        if (a.target.startsWith ("source.")) return false;
                auto live = tr->pluginList.getPlugins();
                if (live.isEmpty() || dynamic_cast<FaustInstrumentPlugin*> (live[0].get()) == nullptr)
                    return false;                    // the edit is not the shape oldS promises
                te::Plugin::Ptr doomedSrc = live[0];
                ops.push_back ([&edit, tr, doomedSrc, src = tb.source]
                {
                    doomedSrc->deleteFromParent();
                    auto plugin = edit.getPluginCache().createNewPlugin (FaustInstrumentPlugin::xmlTypeName, {});
                    if (auto* fp = dynamic_cast<FaustInstrumentPlugin*> (plugin.get()))
                    {
                        fp->dspName = src.id;
                        fp->prepareZones();
                        for (auto& [k, v] : src.params) fp->setZone (k, v);
                    }
                    tr->pluginList.insertPlugin (plugin, 0, nullptr);
                });
                addClass ("srcswap");
                maskT (i, "source");
            }
        }

        {
            auto sameShape = [] (const std::vector<SongFx>& fa, const std::vector<SongFx>& fb)
            {
                if (fa.size() != fb.size()) return false;
                for (size_t j = 0; j < fa.size(); ++j)
                    if (fa[j].id != fb[j].id || fa[j].type != fb[j].type
                        || fa[j].preset != fb[j].preset || fa[j].bypass != fb[j].bypass)
                        return false;
                return true;
            };
            auto trackAnchorOk = [&ta] (te::Plugin* p) -> bool
            {
                if (ta.source.kind == "faust")    return dynamic_cast<FaustInstrumentPlugin*> (p) != nullptr;
                if (ta.source.kind == "sample")   return dynamic_cast<te::SamplerPlugin*> (p) != nullptr;
                if (ta.source.kind == "spectral") return dynamic_cast<SpectralVoicePlugin*> (p) != nullptr;
                if (ta.source.kind == "vst3")     return dynamic_cast<te::ExternalPlugin*> (p) != nullptr;
                if (ta.source.kind == "audio")    return dynamic_cast<te::VolumeAndPanPlugin*> (p) != nullptr;
                return false;
            };
            const bool paramPathOk = sameShape (ta.fx, tb.fx)
                && planFxList (ta.fx, tb.fx, faustFxOf (*tr),
                               [&, i] (size_t j)
                               {
                                   for (auto* arr : { tarrA, tarrB })
                                       maskFxParams (trackObj (arr, i), "fx", j);
                               });
            if (! paramPathOk
                && ! planFxShape (*tr, ta.fx, tb.fx, trackAnchorOk,
                                  &ta.automation, &tb.automation,
                                  [&, i] { maskT (i, "fx"); }))
                return false;
        }

        // sends: gain-only tweaks; topology (count, bus targets) must be identical
        if (ta.sends.size() != tb.sends.size()) return false;
        {
            std::vector<te::AuxSendPlugin*> sps;
            for (auto p : tr->pluginList.getPlugins())
                if (auto* sp = dynamic_cast<te::AuxSendPlugin*> (p)) sps.push_back (sp);
            for (size_t k = 0; k < ta.sends.size(); ++k)
            {
                if (ta.sends[k].bus != tb.sends[k].bus) return false;
                if (ta.sends[k].gainDb == tb.sends[k].gainDb) continue;
                if (sps.size() != ta.sends.size()) return false;
                ops.push_back ([sp = sps[k], v = (float) tb.sends[k].gainDb] { sp->setGainDb (v); });
                addClass ("send");
                for (auto* arr : { tarrA, tarrB })
                    if (auto* o = trackObj (arr, i))
                        if (auto* sa = o->getProperty ("sends").getArray())
                            if ((int) k < sa->size())
                                if (auto* so = sa->getReference ((int) k).getDynamicObject())
                                    so->removeProperty ("gainDb");
            }
        }

        // class 7: this track's automation[] changed — mirror resolveAutoTarget on
        // the live lists (sourcePlug = slot 0 exactly like buildEdit's getFirst()
        // law; fxPlugs positional 1..n, trusted only when every old fx entry
        // type-verifies) and clear + re-add the differing targets' curves.
        if (juce::JSON::toString (automationToVar (ta.automation))
            != juce::JSON::toString (automationToVar (tb.automation)))
        {
            auto live = tr->pluginList.getPlugins();
            te::Plugin* sourcePlug = live.isEmpty() ? nullptr : live[0].get();
            bool fxMirrorOk = live.size() >= (int) ta.fx.size() + 1;
            std::vector<te::Plugin*> fxPlugs;
            for (auto& f : ta.fx) if (! edFxDeltaSafe (f)) fxMirrorOk = false;
            if (fxMirrorOk)
                for (size_t j = 0; j < ta.fx.size(); ++j)
                {
                    if (! liveFxMatches (live[(int) j + 1].get(), ta.fx[j])) { fxMirrorOk = false; break; }
                    fxPlugs.push_back (live[(int) j + 1].get());
                }
            auto resolve = [&, sourcePlug] (const juce::String& tgt, bool& isVolDb, bool& feasible)
                -> te::AutomatableParameter*
            {
                feasible = true;
                if (tgt.startsWith ("fx[") && ! fxMirrorOk) { feasible = false; return nullptr; }
                juce::String err;
                return resolveAutoTarget (tgt, vol, sourcePlug, fxPlugs, isVolDb, err);
            };
            auto planRemoval = [&] (const juce::String& tgt) -> bool
            {
                if (tgt == "gainDb" && vol != nullptr)
                { ops.push_back ([vol, v = (float) tb.gainDb] { vol->setVolumeDb (v); }); return true; }
                if (tgt == "pan" && vol != nullptr)
                { ops.push_back ([vol, v = (float) tb.pan] { vol->setPan (v); }); return true; }
                return false;   // zone targets: the un-automated base is not derivable live
            };
            if (! planAutos (ta.automation, tb.automation, resolve, planRemoval,
                             [&, i] { maskT (i, "automation"); }))
                return false;
        }
    }

    // ---- class 6a: track APPEND — suffix-only (the agent's standard move: "add a
    // lead" = new tracks at the end). Built EXACTLY like buildEdit's track loop,
    // inserted after the last song track so the [songs..., buses...] order a fresh
    // build would produce is preserved. Mid-list inserts pair-mismatch above and
    // refuse; launcher scenes refuse (a delta-added track would lack its cells).
    if (newN > oldN)
    {
        if (! newS.sceneNames.isEmpty()) return false;
        for (auto& t : oldS.tracks)
            if (! t.slots.empty()) return false;
        for (size_t i = oldN; i < newN; ++i)
        {
            const auto& t = newS.tracks[i];
            if (t.source.kind != "faust" && t.source.kind != "sample" && t.source.kind != "vst3")
                return false;
            if (! t.audioClips.empty() || ! t.slots.empty() || ! t.automation.empty())
                return false;
            for (auto& sd : t.sends)
            {
                bool known = false;
                for (auto& b : newS.buses) known = known || b.id == sd.bus;
                if (! known) return false;
            }
        }
        auto* lastSong = atracks[(int) oldN - 1];
        ops.push_back ([&edit, &newS, oldN, lastSong]
        {
            std::map<juce::String, int> busNum;
            for (size_t b = 0; b < newS.buses.size(); ++b)
                busNum[newS.buses[b].id] = (int) b + 1;
            const auto songEnd = edit.tempoSequence.toTime (
                te::BeatPosition::fromBeats (newS.totalBeats() + 4.0));
            te::Track* prev = lastSong;
            for (size_t i = oldN; i < newS.tracks.size(); ++i)
            {
                const auto& t = newS.tracks[i];
                auto track = edit.insertNewAudioTrack (te::TrackInsertPoint (nullptr, prev), nullptr);
                if (track == nullptr) return;
                prev = track.get();
                track->setName (t.name);
                buildTrackSource (edit.engine, edit, *track, t);
                int fxIndex = 1;
                for (auto& fx : t.fx)
                    track->pluginList.insertPlugin (makeFaustFx (edit, fx), fxIndex++, nullptr);
                for (auto& sd : t.sends)
                {
                    auto it = busNum.find (sd.bus);
                    if (it == busNum.end()) continue;
                    auto send = edit.getPluginCache().createNewPlugin (te::AuxSendPlugin::xmlTypeName, {});
                    if (auto* sp = dynamic_cast<te::AuxSendPlugin*> (send.get()))
                    {
                        sp->busNumber = it->second;
                        sp->setGainDb ((float) sd.gainDb);
                    }
                    track->pluginList.insertPlugin (send, fxIndex++, nullptr);
                }
                if (auto* vol = track->getVolumePlugin())
                {
                    vol->setVolumeDb ((float) t.gainDb);
                    vol->setPan ((float) t.pan);
                }
                if (! t.notes.empty())
                    if (auto clip = track->insertMIDIClip ({ te::TimePosition(), songEnd }, nullptr))
                    {
                        int ni = 0;
                        for (auto& n : t.notes)
                            if (noteIncluded (n, ni++))
                                clip->getSequence().addNote (n.pitch,
                                    te::BeatPosition::fromBeats (applySwing (n.start, newS)),
                                    te::BeatDuration::fromBeats (n.len),
                                    juce::jlimit (1, 127, (int) std::lround (n.vel * 127.0)),
                                    0, nullptr);
                    }
                if (t.muted) track->setMute (true);
            }
        });
        addClass ("trackadd");
        while (tarrB->size() > (int) oldN)   // appended entries fully accounted above
            tarrB->remove (tarrB->size() - 1);
    }

    if (oldS.masterGainDb != newS.masterGainDb)
    {
        auto mv = edit.getMasterVolumePlugin();
        if (mv == nullptr) return false;
        ops.push_back ([mv, v = (float) newS.masterGainDb] { mv->setVolumeDb (v); });
        addClass ("mix");
        ra->removeProperty ("masterGainDb");
        rb->removeProperty ("masterGainDb");
    }

    // master fx params (the meter + ears tap ride the same list but are not FaustFxPlugins)
    {
        std::vector<FaustFxPlugin*> mfx;
        for (auto p : edit.getMasterPluginList().getPlugins())
            if (auto* f = dynamic_cast<FaustFxPlugin*> (p)) mfx.push_back (f);
        if (! planFxList (oldS.master, newS.master, mfx,
                          [&] (size_t j)
                          {
                              maskFxParams (ra, "master", j);
                              maskFxParams (rb, "master", j);
                          }))
            return false;

        // class 7 at song level: masterGainDb / master[i].<param> automation.
        // buildEdit's masterFxPlugs = the successfully-created subsequence, which
        // equals the live FaustFxPlugin subsequence ONLY when every master entry
        // is plain faust (vst3 can be null at build; eq/comp are not FaustFxPlugins)
        // — anything else makes the positional mirror untrustworthy and refuses.
        if (juce::JSON::toString (automationToVar (oldS.automation))
            != juce::JSON::toString (automationToVar (newS.automation)))
        {
            auto mv = edit.getMasterVolumePlugin();
            bool masterMirrorOk = mfx.size() == oldS.master.size();
            for (auto& f : oldS.master) if (! edIsPlainFaustFx (f)) masterMirrorOk = false;
            auto resolve = [&] (const juce::String& tgt, bool& isVolDb, bool& feasible)
                -> te::AutomatableParameter*
            {
                feasible = true; isVolDb = false;
                if (tgt == "masterGainDb")
                {
                    isVolDb = true;
                    if (mv == nullptr) { feasible = false; return nullptr; }
                    return mv->volParam.get();
                }
                if (tgt.startsWith ("master[") && tgt.contains ("]."))
                {
                    if (! masterMirrorOk) { feasible = false; return nullptr; }
                    const int idx = tgt.fromFirstOccurrenceOf ("master[", false, false).getIntValue();
                    const auto id = tgt.fromFirstOccurrenceOf ("].", false, false);
                    if (idx < 0 || idx >= (int) mfx.size()) return nullptr;  // build errors<< and skips
                    if (auto p = mfx[(size_t) idx]->getAutomatableParameterByID (id))
                        return p.get();
                    return nullptr;                    // exact-ID law at master level (no fuzzy)
                }
                return nullptr;                        // unknown target: build errors<< and skips
            };
            auto planRemoval = [&] (const juce::String& tgt) -> bool
            {
                if (tgt == "masterGainDb" && mv != nullptr)
                { ops.push_back ([mv, v = (float) newS.masterGainDb] { mv->setVolumeDb (v); }); return true; }
                return false;
            };
            if (! planAutos (oldS.automation, newS.automation, resolve, planRemoval,
                             [&] { ra->removeProperty ("automation"); rb->removeProperty ("automation"); }))
                return false;
        }
    }

    for (size_t b = 0; b < oldS.buses.size(); ++b)
    {
        const auto& ba = oldS.buses[b];
        const auto& bb = newS.buses[b];
        if (ba.id != bb.id) return false;
        auto* btr = atracks[(int) (oldS.tracks.size() + b)];
        auto maskBus = [&] (const char* prop)
        {
            for (auto* r : { ra, rb })
                if (auto* barr = r->getProperty ("buses").getArray())
                    if ((int) b < barr->size())
                        if (auto* bo = barr->getReference ((int) b).getDynamicObject())
                            bo->removeProperty (prop);
        };
        if (ba.gainDb != bb.gainDb)
        {
            auto* vol = btr->getVolumePlugin();
            if (vol == nullptr) return false;
            ops.push_back ([vol, v = (float) bb.gainDb] { vol->setVolumeDb (v); });
            addClass ("mix");
            maskBus ("gainDb");
        }
        {
            auto sameShape = [] (const std::vector<SongFx>& fa, const std::vector<SongFx>& fb)
            {
                if (fa.size() != fb.size()) return false;
                for (size_t j = 0; j < fa.size(); ++j)
                    if (fa[j].id != fb[j].id || fa[j].type != fb[j].type
                        || fa[j].preset != fb[j].preset || fa[j].bypass != fb[j].bypass)
                        return false;
                return true;
            };
            const bool paramPathOk = sameShape (ba.fx, bb.fx)
                && planFxList (ba.fx, bb.fx, faustFxOf (*btr),
                               [&, b] (size_t j)
                               {
                                   for (auto* r : { ra, rb })
                                       if (auto* barr = r->getProperty ("buses").getArray())
                                           if ((int) b < barr->size())
                                               maskFxParams (barr->getReference ((int) b).getDynamicObject(),
                                                             "fx", j);
                               });
            if (! paramPathOk
                && ! planFxShape (*btr, ba.fx, bb.fx,
                                  [] (te::Plugin* p) { return dynamic_cast<te::AuxReturnPlugin*> (p) != nullptr; },
                                  nullptr, nullptr,
                                  [&] { maskBus ("fx"); }))
                return false;
        }
    }

    // THE RESIDUE LAW: everything the ops did not account for must be identical
    if (juce::JSON::toString (va) != juce::JSON::toString (vb))
        return false;

    for (auto& op : ops) op();
    if (classOut != nullptr)
        *classOut = ops.empty() ? juce::String ("noop") : classes.joinIntoString ("+");
    return true;
}

} // namespace sotadaw
