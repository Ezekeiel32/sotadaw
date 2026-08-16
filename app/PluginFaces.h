// PluginFaces.h — every tool gets a FACE (the FL Studio doctrine: each plugin opens
// its own distinctive window). Faust voices/fx get GENERATED editors — sectioned
// knobs skinned by instrument family — so the "vst3 tracks only" wall is gone:
// every sound in the DAW is now hand-editable. VST3 plugins keep their native
// editors, hosted inside the same chrome so the product feels like ONE instrument.
#pragma once
#include <tracktion_engine/tracktion_engine.h>
#include "UiTheme.h"
#include "FaustInstrumentPlugin.h"
#include "FaustFxPlugin.h"

namespace te = tracktion;

namespace faces
{

struct Skin
{
    juce::Colour hot, cool;     // gradient ends
    juce::String family;        // painted subtitle chip
    juce::Colour trackAccent;   // CC3-1 FL law: the CHANNEL's colour rides into the modal
                                // (transparent = unset; openFace stamps theme::trackColour)
};

inline Skin skinFor (const juce::String& dspName)
{
    const auto c = theme::familyColour (dspName);
    const auto n = dspName.toLowerCase();
    juce::String fam = "voice";
    // built-in engine tools first — before this they ALL fell to 'voice' and every
    // eq/comp/sampler face looked identical (the "generic and all the same" tell)
    if (n.contains ("equal") || n == "eq" || n.startsWith ("eq "))           fam = "eq";
    else if (n.contains ("compress") || n.contains ("limit"))                fam = "dynamics";
    else if (n.contains ("sampler"))                                         fam = "sampler";
    else if (n.contains ("volume") || n.contains ("trim") || n.contains ("gain")
          || n.contains ("pan") || n.contains ("level"))                     fam = "utility";
    else if (n.startsWith ("fx_"))                                           fam = "effect";
    else if (n.contains ("kick") || n.contains ("snare") || n.contains ("hat")
          || n.contains ("clap") || n.contains ("perc") || n.contains ("drum"))  fam = "drum";
    else if (n.contains ("bass") || n.contains ("sub") || n.contains ("reese"))  fam = "bass";
    else if (n.contains ("pad") || n.contains ("string") || n.contains ("vox"))  fam = "pad";
    else if (n.contains ("key") || n.contains ("organ") || n.contains ("clav")
          || n.contains ("rhodes") || n.contains ("piano"))                      fam = "keys";
    return { c.brighter (0.10f), c.withRotatedHue (0.09f).darker (0.15f), fam };
}

// the family's MONEY parameter — the one that gets the hero knob
inline int heroScore (const juce::String& family, const juce::String& paramName)
{
    const auto n = paramName.toLowerCase();
    auto pri = [&n] (std::initializer_list<const char*> keys)
    {
        int s = 100;
        for (auto* k : keys) { if (n.contains (k)) return s; s -= 10; }
        return 0;
    };
    if (family == "bass")     return pri ({ "cutoff", "freq", "drive", "decay" });
    if (family == "drum")     return pri ({ "punch", "decay", "tune", "snap" });
    if (family == "pad")      return pri ({ "attack", "motion", "rate", "width" });
    if (family == "effect")   return pri ({ "mix", "wet", "drive", "amount", "cutoff" });
    if (family == "keys")     return pri ({ "tone", "bright", "drawbar", "bell" });
    if (family == "eq")       return pri ({ "gain", "freq", "q" });
    if (family == "dynamics") return pri ({ "threshold", "ratio", "attack", "release" });
    if (family == "utility")  return pri ({ "level", "gain", "pan" });
    if (family == "sampler")  return 0;   // a sampler face is its zones, not one knob
    return pri ({ "cutoff", "tone", "decay", "bright" });
}

// FL doctrine, honoured: every family gets its own FACEPLATE ART — drawn, generative,
// keyed to the skin hue. Low alpha over the panel gradient: depth, not noise.
inline void paintBackdrop (juce::Graphics& g, juce::Rectangle<float> r, const Skin& skin,
                           int headerH)
{
    auto body = r.withTrimmedTop ((float) headerH);
    g.setGradientFill ({ theme::panel.brighter (0.03f), body.getTopLeft(),
                         theme::panel.darker (0.10f), body.getBottomLeft(), false });
    g.fillRect (body);
    juce::Random rng ((juce::int64) (skin.hot.getARGB()));   // stable per family colour
    if (skin.family == "drum")
    {   // impact rings + hit dots — punch energy
        const auto c = body.getBottomLeft().translated (body.getWidth() * 0.22f, -8.0f);
        for (int i = 1; i <= 5; ++i)
        {
            g.setColour (skin.hot.withAlpha (0.10f - 0.016f * (float) i));
            g.drawEllipse (c.x - 26.0f * i, c.y - 26.0f * i, 52.0f * i, 52.0f * i, 2.2f);
        }
        g.setColour (skin.hot.withAlpha (0.10f));
        for (int i = 0; i < 14; ++i)
            g.fillEllipse (body.getX() + rng.nextFloat() * body.getWidth(),
                           body.getY() + rng.nextFloat() * body.getHeight(),
                           2.5f, 2.5f);
    }
    else if (skin.family == "bass")
    {   // heavy sub ridges rolling across the lower body
        for (int k = 0; k < 3; ++k)
        {
            juce::Path w;
            const float yb = body.getBottom() - 18.0f - 26.0f * (float) k;
            w.startNewSubPath (body.getX(), yb);
            for (float px = body.getX(); px <= body.getRight(); px += 3.0f)
                w.lineTo (px, yb - std::sin (px * (0.016f - 0.003f * (float) k) + (float) k * 1.7f)
                                   * (10.0f - 2.5f * (float) k));
            g.setColour (skin.hot.withAlpha (0.10f - 0.025f * (float) k));
            g.strokePath (w, juce::PathStrokeType (3.4f - 0.8f * (float) k,
                                                   juce::PathStrokeType::curved));
        }
    }
    else if (skin.family == "pad")
    {   // aurora: layered slow translucent waves filling the body
        for (int k = 0; k < 4; ++k)
        {
            juce::Path w;
            const float base = body.getY() + body.getHeight() * (0.35f + 0.16f * (float) k);
            w.startNewSubPath (body.getX(), body.getBottom());
            for (float px = body.getX(); px <= body.getRight(); px += 4.0f)
                w.lineTo (px, base + std::sin (px * 0.012f + (float) k * 2.1f) * 14.0f);
            w.lineTo (body.getRight(), body.getBottom());
            w.closeSubPath();
            g.setColour ((k % 2 == 0 ? skin.hot : skin.cool).withAlpha (0.05f));
            g.fillPath (w);
        }
    }
    else if (skin.family == "keys")
    {   // a faint keybed band along the base
        auto kb = body.removeFromBottom (26.0f).reduced (10.0f, 4.0f);
        const float kw = kb.getWidth() / 21.0f;
        for (int i = 0; i < 21; ++i)
        {
            g.setColour (juce::Colours::white.withAlpha (0.05f));
            g.fillRoundedRectangle (kb.getX() + kw * (float) i + 0.8f, kb.getY(),
                                    kw - 1.6f, kb.getHeight(), 1.5f);
            const int m = i % 7;
            if (m == 0 || m == 1 || m == 3 || m == 4 || m == 5)
            {
                g.setColour (skin.hot.withAlpha (0.13f));
                g.fillRoundedRectangle (kb.getX() + kw * (float) i + kw * 0.62f, kb.getY(),
                                        kw * 0.7f, kb.getHeight() * 0.6f, 1.2f);
            }
        }
    }
    else if (skin.family == "effect")
    {   // signal path: in -> nodes -> out
        const float cy = body.getBottom() - 22.0f;
        g.setColour (skin.hot.withAlpha (0.14f));
        g.drawLine (body.getX() + 12.0f, cy, body.getRight() - 12.0f, cy, 1.6f);
        for (int i = 0; i < 4; ++i)
        {
            const float nx = body.getX() + body.getWidth() * (0.16f + 0.22f * (float) i);
            g.setColour (skin.hot.withAlpha (0.22f));
            g.fillEllipse (nx - 3.5f, cy - 3.5f, 7.0f, 7.0f);
            g.setColour (skin.cool.withAlpha (0.12f));
            g.drawEllipse (nx - 7.0f, cy - 7.0f, 14.0f, 14.0f, 1.0f);
        }
    }
    else if (skin.family == "eq")
    {   // the response curve: log-grid hints + a bell boost and a high shelf
        auto zone = body.reduced (14.0f, 18.0f);
        g.setColour (juce::Colours::white.withAlpha (0.035f));
        for (float fx : { 0.12f, 0.3f, 0.5f, 0.7f, 0.88f })
            g.drawVerticalLine ((int) (zone.getX() + zone.getWidth() * fx),
                                zone.getY(), zone.getBottom());
        const float mid = zone.getCentreY();
        g.setColour (juce::Colours::white.withAlpha (0.05f));
        g.drawHorizontalLine ((int) mid, zone.getX(), zone.getRight());
        juce::Path curve;
        curve.startNewSubPath (zone.getX(), mid + 6.0f);
        for (float px = zone.getX(); px <= zone.getRight(); px += 3.0f)
        {
            const float u = (px - zone.getX()) / zone.getWidth();
            const float bell = std::exp (-std::pow ((u - 0.42f) * 6.5f, 2.0f)) * -26.0f;
            const float shelf = 10.0f / (1.0f + std::exp (-(u - 0.78f) * 18.0f));
            curve.lineTo (px, mid + 6.0f + bell + shelf * -0.6f);
        }
        g.setColour (skin.hot.withAlpha (0.22f));
        g.strokePath (curve, juce::PathStrokeType (2.4f, juce::PathStrokeType::curved));
        g.setColour (skin.cool.withAlpha (0.30f));
        g.fillEllipse (zone.getX() + zone.getWidth() * 0.42f - 4.0f, mid - 20.0f - 4.0f, 8.0f, 8.0f);
        g.fillEllipse (zone.getX() + zone.getWidth() * 0.78f - 4.0f, mid + 0.4f, 8.0f, 8.0f);
    }
    else if (skin.family == "dynamics")
    {   // the transfer curve: unity line, knee bend at the threshold, GR ticks
        auto zone = body.reduced (18.0f, 16.0f);
        g.setColour (juce::Colours::white.withAlpha (0.04f));
        g.drawLine (zone.getX(), zone.getBottom(), zone.getRight(), zone.getY(), 1.0f);
        juce::Path knee;
        const float kx = zone.getX() + zone.getWidth() * 0.55f;
        const float ky = zone.getBottom() - zone.getHeight() * 0.55f;
        knee.startNewSubPath (zone.getX(), zone.getBottom());
        knee.lineTo (kx, ky);
        knee.lineTo (zone.getRight(), ky - zone.getHeight() * 0.13f);
        g.setColour (skin.hot.withAlpha (0.24f));
        g.strokePath (knee, juce::PathStrokeType (2.4f, juce::PathStrokeType::curved,
                                                  juce::PathStrokeType::rounded));
        g.setColour (skin.cool.withAlpha (0.35f));
        g.fillEllipse (kx - 4.0f, ky - 4.0f, 8.0f, 8.0f);
        for (int i = 0; i < 6; ++i)   // gain-reduction ticks falling from the top right
        {
            g.setColour (skin.hot.withAlpha (0.16f - 0.02f * (float) i));
            g.fillRect (zone.getRight() - 10.0f - 7.0f * (float) i, zone.getY(),
                        3.5f, 8.0f + 3.0f * (float) i);
        }
    }
    else if (skin.family == "sampler")
    {   // waveform slices with slice markers — the chopped-sample identity
        auto zone = body.reduced (14.0f, 20.0f);
        juce::Random wrng (0x5A17CE);
        const int bars = 46;
        const float bw = zone.getWidth() / (float) bars;
        for (int i = 0; i < bars; ++i)
        {
            const float env = 0.25f + 0.75f * std::abs (std::sin ((float) i * 0.33f));
            const float hgt = zone.getHeight() * env * (0.55f + 0.45f * wrng.nextFloat());
            g.setColour ((i / 12) % 2 == 0 ? skin.hot.withAlpha (0.14f)
                                           : skin.cool.withAlpha (0.16f));
            g.fillRoundedRectangle (zone.getX() + bw * (float) i + 0.8f,
                                    zone.getCentreY() - hgt * 0.5f, bw - 1.6f, hgt, 1.2f);
        }
        for (int s = 0; s <= 4; ++s)   // slice markers
        {
            const float sx = zone.getX() + zone.getWidth() * 0.25f * (float) s;
            g.setColour (skin.hot.withAlpha (0.30f));
            g.drawVerticalLine ((int) sx, zone.getY() - 6.0f, zone.getBottom() + 6.0f);
            g.fillEllipse (sx - 2.5f, zone.getY() - 9.0f, 5.0f, 5.0f);
        }
    }
    else if (skin.family == "utility")
    {   // a clean fader ladder — staging, honestly plain
        auto zone = body.reduced (24.0f, 18.0f);
        for (int i = 0; i < 4; ++i)
        {
            const float fx = zone.getX() + zone.getWidth() * (0.14f + 0.24f * (float) i);
            g.setColour (juce::Colours::white.withAlpha (0.05f));
            g.drawVerticalLine ((int) fx, zone.getY(), zone.getBottom());
            const float fy = zone.getY() + zone.getHeight() * (0.25f + 0.16f * (float) i);
            g.setColour (skin.hot.withAlpha (0.20f));
            g.fillRoundedRectangle (fx - 7.0f, fy - 3.0f, 14.0f, 6.0f, 2.0f);
        }
    }
    else
    {   // voice/lead: diagonal saw ridges
        g.setColour (skin.hot.withAlpha (0.055f));
        for (float px = body.getX() - body.getHeight(); px < body.getRight(); px += 26.0f)
            g.drawLine (px, body.getBottom(), px + body.getHeight() * 0.7f, body.getY() + 10.0f, 7.0f);
    }
}

// ---------------------------------------------------------------------------
// One knob, custom-drawn: inset well, value arc in the skin colour, glow thumb,
// name + live value readout underneath. Bound directly to an engine parameter.
class FaceKnob : public juce::Slider
{
public:
    FaceKnob (te::AutomatableParameter* p, const Skin& s) : param (p), skin (s)
    {
        setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
        setTextBoxStyle (juce::Slider::NoTextBox, true, 0, 0);
        setRotaryParameters (juce::MathConstants<float>::pi * 1.25f,
                             juce::MathConstants<float>::pi * 2.75f, true);
        const auto lo = param->valueRange.start, hi = param->valueRange.end;
        setRange (lo, hi, 0.0);
        setDoubleClickReturnValue (true, param->getCurrentValue());
        setValue (param->getCurrentValue(), juce::dontSendNotification);
        onValueChange = [this] { param->setParameter ((float) getValue(), juce::sendNotification); };
        setName (param->getParameterName());
    }

    void syncFromParam()
    {
        setValue (param->getCurrentValue(), juce::dontSendNotification);
    }

    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat();
        auto well = r.withHeight (r.getWidth()).reduced (9.0f);
        const float cx = well.getCentreX(), cy = well.getCentreY(), rad = well.getWidth() * 0.5f;
        const float a0 = juce::MathConstants<float>::pi * 1.25f,
                    a1 = juce::MathConstants<float>::pi * 2.75f;
        const float t = (float) valueToProportionOfLength (getValue());
        const float at = a0 + (a1 - a0) * t;

        // anatomy scales with radius — a 116px hero and a 44px section knob both read
        const float aw = juce::jmax (3.5f, rad * 0.11f);
        // well + capped face (vertical sheen = machined, not a void)
        g.setColour (theme::inset);
        g.fillEllipse (well.expanded (3.0f));
        g.setGradientFill ({ theme::panelHi.brighter (0.12f), cx, well.getY(),
                             theme::panel.darker (0.25f), cx, well.getBottom(), false });
        g.fillEllipse (well.reduced (aw + 3.0f));
        g.setColour (juce::Colours::white.withAlpha (0.07f));
        g.drawEllipse (well.reduced (aw + 3.0f), 1.0f);
        g.setColour (theme::inset.brighter (0.35f));
        g.drawEllipse (well.reduced (rad * 0.45f), 1.0f);       // machined inner ring
        // track arc + value arc
        juce::Path track, val;
        track.addCentredArc (cx, cy, rad, rad, 0.0f, a0, a1, true);
        g.setColour (theme::grid);
        g.strokePath (track, { aw, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        if (t > 0.004f)
        {
            val.addCentredArc (cx, cy, rad, rad, 0.0f, a0, at, true);
            g.setGradientFill ({ skin.cool, well.getBottomLeft(), skin.hot, well.getTopRight(), false });
            g.strokePath (val, { aw, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        }
        // pointer line + glow tip (line appears once the knob is big enough to carry it)
        const float px = cx + std::sin (at) * (rad - aw * 1.8f), py = cy - std::cos (at) * (rad - aw * 1.8f);
        if (rad > 30.0f)
        {
            g.setColour (theme::text.withAlpha (0.85f));
            g.drawLine (cx + std::sin (at) * rad * 0.35f, cy - std::cos (at) * rad * 0.35f,
                        px, py, juce::jmax (2.2f, aw * 0.45f));
        }
        g.setColour (skin.hot.withAlpha (0.35f));
        g.fillEllipse (px - aw, py - aw, aw * 2.0f, aw * 2.0f);
        g.setColour (theme::text);
        g.fillEllipse (px - aw * 0.45f, py - aw * 0.45f, aw * 0.9f, aw * 0.9f);
        // label + value
        g.setColour (theme::textDim);
        g.setFont (theme::ui (9.5f, juce::Font::bold));
        g.drawText (getName(), r.withTrimmedTop (r.getWidth() - 4.0f).withHeight (12.0f).toNearestInt(),
                    juce::Justification::centred);
        g.setColour (skin.hot.brighter (0.15f));
        g.setFont (theme::mono (9.0f));
        g.drawText (juce::String (getValue(), std::abs (getMaximum() - getMinimum()) > 20.0 ? 0 : 2),
                    r.withTrimmedTop (r.getWidth() + 8.0f).withHeight (11.0f).toNearestInt(),
                    juce::Justification::centred);
    }

private:
    te::AutomatableParameter* param;
    Skin skin;
};

// ---------------------------------------------------------------------------
// The generated editor for a Faust voice or effect: header identity + sectioned
// knob grid. Diverse by construction — colours, family chip and knob count all
// derive from the instrument itself.
class FaustFace : public juce::Component, private juce::Timer
{
public:
    static constexpr int knobW = 74, knobH = 100, headerH = 54, pad = 12;

    FaustFace (te::Plugin& plug, const juce::String& dspName, const juce::String& trackName,
               const juce::String& kindLabel = "FAUST DSP")
        : skin (skinFor (dspName)), dsp (dspName), track (trackName), kind (kindLabel)
    {
        te::AutomatableParameter* heroParam = nullptr;
        int bestScore = 0;
        for (auto p : plug.getAutomatableParameters())
            if (p != nullptr)
            {
                const int sc = heroScore (skin.family, p->getParameterName());
                if (sc > bestScore) { bestScore = sc; heroParam = p; }
            }
        for (auto p : plug.getAutomatableParameters())
            if (p != nullptr)
            {
                auto* k = new FaceKnob (p, skin);
                knobs.add (k);
                addAndMakeVisible (k);
                if (p == heroParam && knobs.size() <= 24)
                    hero = k;                      // the money parameter, writ large
                else
                    sections[sectionFor (p->getParameterName())].add (k);
            }
        // preferred size mirrors resized(): hero strip + per section 18 + rows*knobH + 20
        int h = headerH + pad + pad + (hero != nullptr ? heroH : 0);
        for (auto& s : order())
            if (sections.count (s) && ! sections[s].isEmpty())
                h += 18 + ((sections[s].size() + 4) / 5) * knobH + 20;
        if (knobs.isEmpty()) h += 60;
        setSize (pad * 2 + 5 * knobW, h);   // TRUE height; Chrome caps + scrolls tall faces
        startTimerHz (8);        // follow automation/agent edits while open
    }

    static juce::StringArray order()
    {
        return { "ENVELOPE", "TONE", "MOTION", "SPACE / DRIVE", "CHARACTER" };
    }

    static juce::String sectionFor (const juce::String& raw)
    {
        const auto n = raw.toLowerCase();
        auto any = [&n] (std::initializer_list<const char*> keys)
        {
            for (auto* k : keys) if (n.contains (k)) return true;
            return false;
        };
        if (any ({ "attack", "decay", "sustain", "release", "env", "hold", "punch", "tail", "drop" })) return "ENVELOPE";
        if (any ({ "cutoff", "res", "bright", "tone", "filter", "formant", "color", "colour", "harm", "timbre", "damp", "sizzle", "snap",
                   "shelf", "freq", " q" })) return "TONE";   // eq anatomy is TONE (shelf/freq/Q)
        if (any ({ "lfo", "rate", "speed", "wow", "flutter", "vib", "trem", "motion", "detune", "spread", "wobble", "glide" })) return "MOTION";
        if (any ({ "mix", "wet", "room", "size", "feedback", "time", "delay", "drive", "level", "sat", "width", "depth", "ceiling", "amount" })) return "SPACE / DRIVE";
        return "CHARACTER";
    }

    size_t sectionsUsed() const
    {
        size_t n = 0;
        for (auto& [k, v] : sections) if (! v.isEmpty()) ++n;
        return n;
    }

    juce::String sectionCensus() const     // rig truth: where did the params land
    {
        juce::String s;
        for (auto& [k, v] : sections)
            if (! v.isEmpty())
                s << k.replace (" ", "_").replace ("/", "-") << "=" << v.size() << " ";
        if (hero != nullptr)
            s << "hero=" << hero->getName().replace (" ", "_");
        return s.trim();
    }

    void resized() override
    {
        auto r = getLocalBounds().reduced (pad, 0).withTrimmedTop (headerH + pad);
        if (hero != nullptr)
        {
            auto strip = r.removeFromTop (heroH);
            // knob well is width-sized with labels below: width = heroH - label zone
            hero->setBounds (strip.removeFromLeft (heroH).withWidth (heroH - 34).reduced (2));
        }
        for (auto& sec : order())
        {
            if (! sections.count (sec) || sections[sec].isEmpty()) continue;
            r.removeFromTop (18);
            auto row = r.removeFromTop (knobH);
            int i = 0;
            for (auto* k : sections[sec])
            {
                if (i == 5) { row = r.removeFromTop (knobH); i = 0; }
                k->setBounds (row.removeFromLeft (knobW).withHeight (knobH));
                ++i;
            }
            r.removeFromTop (20);
        }
    }

    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat();
        paintBackdrop (g, r, skin, headerH);       // the family's faceplate art
        // header: the instrument's identity
        auto head = r.withHeight ((float) headerH);
        g.setColour (theme::panel.darker (0.08f));   // OPAQUE base: the tint never washes out
        g.fillRect (head);
        g.setGradientFill ({ skin.cool.darker (0.25f).withAlpha (0.85f), head.getTopLeft(),
                             skin.hot.withAlpha (0.12f), head.getBottomRight(), false });
        g.fillRect (head);
        g.setColour (juce::Colours::white.withAlpha (0.05f));
        g.drawHorizontalLine (0, 0.0f, r.getWidth());
        g.setColour (theme::line);
        g.drawHorizontalLine (headerH, 0.0f, r.getWidth());
        // waveform motif — a drawn signature along the header base, unique per family hue
        {
            juce::Path wave;
            const float wy = (float) headerH - 5.0f;
            wave.startNewSubPath (14.0f, wy);
            for (float px = 14.0f; px < head.getRight() - 14.0f; px += 2.0f)
                wave.lineTo (px, wy - std::abs (std::sin (px * 0.055f)) * 3.5f
                                   * (0.4f + 0.6f * std::abs (std::sin (px * 0.011f + skin.hot.getHue() * 6.0f))));
            g.setColour (skin.hot.withAlpha (0.16f));
            g.strokePath (wave, juce::PathStrokeType (1.3f));
        }
        g.setColour (theme::text);
        g.setFont (theme::ui (19.0f, juce::Font::bold));
        g.drawText (dsp, 16, 6, getWidth() - 120, 26, juce::Justification::centredLeft);
        g.setColour (theme::textDim);
        g.setFont (theme::mono (9.5f));
        g.drawText (kind + " - " + juce::String (knobs.size()) + " live params - track: " + track,
                    16, 32, getWidth() - 120, 12, juce::Justification::centredLeft);
        // family chip
        {
            const auto f = theme::ui (9.0f, juce::Font::bold);
            const float cw = theme::measure (f, skin.family) + 16.0f;
            juce::Rectangle<float> chip (head.getRight() - cw - 14.0f, head.getCentreY() - 9.0f, cw, 18.0f);
            g.setColour (skin.hot.withAlpha (0.16f));
            g.fillRoundedRectangle (chip, 9.0f);
            g.setColour (skin.hot.withAlpha (0.33f));
            g.drawRoundedRectangle (chip.reduced (0.5f), 9.0f, 1.0f);
            g.setColour (skin.hot.brighter (0.2f));
            g.setFont (f);
            g.drawText (skin.family, chip.toNearestInt(), juce::Justification::centred);
        }
        // hero strip: the money parameter's name + guidance, next to the big knob
        auto rr = getLocalBounds().reduced (pad, 0).withTrimmedTop (headerH + pad);
        if (hero != nullptr)
        {
            auto strip = rr.removeFromTop (heroH);
            auto info = strip.withTrimmedLeft (heroH + 8).reduced (0, 26);
            g.setColour (skin.hot.withAlpha (0.85f));
            g.setFont (theme::ui (11.0f, juce::Font::bold));
            g.drawText ("THE " + hero->getName().toUpperCase(), info.removeFromTop (16),
                        juce::Justification::centredLeft);
            g.setColour (theme::textDim);
            g.setFont (theme::ui (10.0f));
            g.drawText ("this voice's money knob - grab it first", info.removeFromTop (14),
                        juce::Justification::centredLeft);
            g.setColour (theme::line);
            g.drawHorizontalLine (strip.getBottom() - 2, (float) strip.getX(), (float) strip.getRight());
        }
        for (auto& sec : order())
        {
            if (! sections.count (const_cast<juce::String&> (sec)) || sections.at (sec).isEmpty()) continue;
            auto lab = rr.removeFromTop (18);
            g.setColour (skin.hot.withAlpha (0.75f));
            g.setFont (theme::ui (9.0f, juce::Font::bold));
            g.drawText (sec, lab, juce::Justification::bottomLeft);
            const float tw = theme::measure (theme::ui (9.0f, juce::Font::bold), sec);
            g.setColour (theme::line);
            g.drawHorizontalLine (lab.getBottom() - 4, (float) lab.getX() + tw + 8.0f, (float) lab.getRight());
            int rows = (sections.at (sec).size() + 4) / 5;
            rr.removeFromTop (rows * knobH + 20);
        }
        if (knobs.isEmpty())
        {
            g.setColour (theme::textMute);
            g.setFont (theme::ui (12.0f));
            g.drawText ("this voice exposes no control zones", getLocalBounds(), juce::Justification::centred);
        }
    }

private:
    void timerCallback() override
    {
        for (auto* k : knobs)
            if (! k->isMouseButtonDown())
                k->syncFromParam();
    }

    static constexpr int heroH = 150;
    Skin skin;
    juce::String dsp, track, kind;
    juce::OwnedArray<FaceKnob> knobs;
    FaceKnob* hero = nullptr;
    std::map<juce::String, juce::Array<FaceKnob*>> sections;
};

// ---------------------------------------------------------------------------
// The chrome every face lives in: drawn title bar (family badge + names + close),
// draggable anywhere on the header. Content is either a FaustFace (owned) or a
// native AudioProcessorEditor (owned, deleted via the host contract).
class Chrome : public juce::Component
{
public:
    static constexpr int barH = 34;
    static constexpr int maxBodyH = 760;   // taller faces scroll; the desk stays a desk
    std::function<void()> onClose;

    Chrome (juce::Component* inner, bool ownInner, const Skin& s,
            const juce::String& title, const juce::String& sub)
        : skin (s), titleText (title), subText (sub), content (inner), owns (ownInner)
    {
        if (content->getHeight() > maxBodyH)
        {   // THE FACE SCROLLS: 260-param faces cap the window, knobs stay reachable
            vp.reset (new juce::Viewport());
            vp->setViewedComponent (content, false);
            vp->setScrollBarsShown (true, false);
            vp->setScrollBarThickness (10);
            addAndMakeVisible (*vp);
            setSize (juce::jmax (330, content->getWidth() + 10), maxBodyH + barH);
        }
        else
        {
            addAndMakeVisible (content);
            setSize (juce::jmax (330, content->getWidth()), content->getHeight() + barH);
        }
    }

    ~Chrome() override
    {
        if (vp != nullptr)
            vp->setViewedComponent (nullptr, false);   // release before any owns-delete
        if (owns)
            delete content;                     // AudioProcessorEditor: host must delete explicitly
    }

    juce::Component* inner() const { return content; }
    juce::Viewport* scrollView() const { return vp.get(); }   // rig truth: tall = wrapped

    void resized() override
    {
        if (vp != nullptr)
            vp->setBounds (getLocalBounds().withTrimmedTop (barH));
        else if (content != nullptr)
            content->setBounds (getLocalBounds().withTrimmedTop (barH));
    }

    void childBoundsChanged (juce::Component* c) override
    {
        if (vp == nullptr && c == content && content != nullptr)   // native editors resize themselves
            setSize (juce::jmax (330, content->getWidth()), content->getHeight() + barH);
    }

    void paint (juce::Graphics& g) override
    {
        auto bar = getLocalBounds().withHeight (barH).toFloat();
        g.setGradientFill ({ theme::panelHi, bar.getTopLeft(), theme::panel, bar.getBottomLeft(), false });
        g.fillRect (bar);
        const bool hasTrack = ! skin.trackAccent.isTransparent();
        if (hasTrack)   // the channel's identity ribbon: same hue as the arranger lane
        {
            g.setColour (skin.trackAccent.withAlpha (0.95f));
            g.fillRect (bar.withWidth (5.0f));
            g.setGradientFill ({ skin.trackAccent.withAlpha (0.16f), bar.getTopLeft(),
                                 skin.trackAccent.withAlpha (0.0f),
                                 { bar.getX() + bar.getWidth() * 0.45f, bar.getY() }, false });
            g.fillRect (bar.withTrimmedLeft (5.0f));
            g.setColour (skin.trackAccent.withAlpha (0.55f));   // the ring the window wears
            g.drawRect (getLocalBounds().toFloat().reduced (0.5f), 1.2f);
        }
        else
        {
            g.setColour (skin.hot.withAlpha (0.9f));
            g.fillRect (bar.withWidth (3.0f));
        }
        g.setColour (theme::line);
        g.drawHorizontalLine (barH - 1, 0.0f, bar.getWidth());
        g.setColour (skin.hot.withAlpha (0.18f));
        g.fillEllipse (12.0f, bar.getCentreY() - 8.0f, 16.0f, 16.0f);
        theme::spark (g, { 16.0f, bar.getCentreY() - 4.0f, 8.0f, 8.0f }, skin.hot);
        g.setColour (theme::text);
        g.setFont (theme::ui (12.5f, juce::Font::bold));
        g.drawText (titleText, 36, 0, getWidth() - 150, barH, juce::Justification::centredLeft);
        g.setColour (theme::textMute);
        g.setFont (theme::mono (9.5f));
        g.drawText (subText, 36 + (int) theme::measure (theme::ui (12.5f, juce::Font::bold), titleText) + 10,
                    0, 200, barH, juce::Justification::centredLeft);
        // close
        auto x = closeRect().toFloat();
        g.setColour (hoverClose ? theme::bad.withAlpha (0.85f) : theme::panel);
        g.fillRoundedRectangle (x, 5.0f);
        g.setColour (hoverClose ? theme::text : theme::textDim);
        const auto c = x.reduced (7.0f);
        g.drawLine (c.getX(), c.getY(), c.getRight(), c.getBottom(), 1.4f);
        g.drawLine (c.getX(), c.getBottom(), c.getRight(), c.getY(), 1.4f);
    }

    juce::Rectangle<int> closeRect() const { return { getWidth() - 30, 6, 22, 22 }; }

    void mouseMove (const juce::MouseEvent& e) override
    {
        const bool h = closeRect().contains (e.getPosition());
        if (h != hoverClose) { hoverClose = h; repaint (0, 0, getWidth(), barH); }
    }
    void mouseDown (const juce::MouseEvent& e) override
    {
        if (e.y < barH && ! closeRect().contains (e.getPosition()))
            dragger.startDraggingComponent (getTopLevelComponent(), e);
    }
    void mouseDrag (const juce::MouseEvent& e) override
    {
        if (e.getMouseDownY() < barH && ! closeRect().contains (e.getMouseDownPosition()))
            dragger.dragComponent (getTopLevelComponent(), e, nullptr);
    }
    void mouseUp (const juce::MouseEvent& e) override
    {
        if (closeRect().contains (e.getPosition()) && onClose)
            onClose();
    }

private:
    Skin skin;
    juce::String titleText, subText;
    juce::Component* content = nullptr;
    std::unique_ptr<juce::Viewport> vp;    // present only when the face outgrows maxBodyH
    bool owns = false, hoverClose = false;
    juce::ComponentDragger dragger;
};

// Frameless floating window (we draw our own chrome — FL style).
class FaceWindow : public juce::DocumentWindow
{
public:
    FaceWindow (const juce::String& name, juce::Colour bg)
        : juce::DocumentWindow (name, bg, 0, true)
    {
        setUsingNativeTitleBar (false);
        setTitleBarHeight (0);
        setDropShadowEnabled (true);
        setResizable (false, false);
    }
    void closeButtonPressed() override { setVisible (false); }
};

} // namespace faces
