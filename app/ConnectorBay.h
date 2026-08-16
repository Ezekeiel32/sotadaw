// ConnectorBay.h — THE CONNECTOR BAY (Chezy 2026-07-16 ask #5: "the connectors
// aren't in the right place - they need to be nice buttons somewhere that fits
// intuitively and aesthetically"). The world-bridges leave the menu bar's shadow:
// one CONNECT button in the transport (beside Export, where in/out belongs) opens
// this machined vault sheet — IMPORT A WORLD on the left, EXPORT THIS SONG on the
// right, every format a real tile with a badge and a one-line truth. The tiles
// fire the SAME lambdas as the Connectors menu (one dispatch, two faces); the
// menu stays for the keyboard-minded.
//
// Vault-glass law: a machined window (seams, top light, engraved caps), never a
// frameless frost. ESC or a click on the dim floor closes it.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

class ConnectorBay : public juce::Component
{
public:
    std::function<void (const juce::String&)> onAction;   // tile id -> host dispatch
    std::function<void()> onClose;

    ConnectorBay()
    {
        setWantsKeyboardFocus (true);
        setInterceptsMouseClicks (true, true);
    }

    void setSongName (const juce::String& s) { songName = s; repaint(); }

    struct Tile { const char* id, *badge, *name, *sub; };
    static constexpr int nIn = 7, nOut = 5;
    const Tile* imports() const
    {
        static const Tile t[nIn] = {
            { "in_audio",     "WAV", "Song audio -> stems session", "any mp3/wav/flac: GPU demucs stems + editable MIDI sketches" },
            { "in_als",       "ALS", "Ableton Live set",            "tracks, clips, devices land as a session" },
            { "in_flp",       "FLP", "FL Studio project",           "patterns + playlist through the PyFLP bridge" },
            { "in_dawproject","DWP", "DAWproject",                  "Bitwig / Cubase / Nuendo / Studio One, round-trip exact" },
            { "in_rpp",       "RPP", "REAPER project",              "round-trip exact at MIDI resolution" },
            { "in_midi",      "MID", "Standard MIDI file",          "any DAW's notes -> lanes, byte-idempotent bridge" },
            { "in_rekordbox", "RBX", "Rekordbox collection",        "bpm / Camelot / first-beat truth + a ready DJ set plan" },
        };
        return t;
    }
    const Tile* exports() const
    {
        static const Tile t[nOut] = {
            { "out_master",    "WAV", "Master (C2PA-signed)", "bounce the release wall's truth with provenance" },
            { "out_als",       "ALS", "Ableton Live set",     "open this song in Live, lanes intact" },
            { "out_dawproject","DWP", "DAWproject",           "Bitwig / Cubase / Nuendo / Studio One" },
            { "out_rpp",       "RPP", "REAPER project",       "round-trip exact - come back any time" },
            { "out_midi",      "MID", "Standard MIDI file",   "the notes, for anything with a piano roll" },
        };
        return t;
    }

    bool keyPressed (const juce::KeyPress& k) override
    {
        if (k == juce::KeyPress (juce::KeyPress::escapeKey)) { if (onClose) onClose(); return true; }
        return false;
    }

    void mouseMove (const juce::MouseEvent& e) override
    {
        juce::String h;
        for (auto& hh : hits)
            if (hh.r.contains (e.position)) { h = hh.id; break; }
        if (h != hoverId)
        {
            hoverId = h;
            setMouseCursor (h.isNotEmpty() ? juce::MouseCursor::PointingHandCursor
                                           : juce::MouseCursor::NormalCursor);
            repaint();
        }
    }
    void mouseExit (const juce::MouseEvent&) override { hoverId.clear(); repaint(); }

    void mouseUp (const juce::MouseEvent& e) override
    {
        for (auto& h : hits)
            if (h.r.contains (e.position))
            {
                if (h.id == "close") { if (onClose) onClose(); }
                else if (onAction) onAction (h.id);
                return;
            }
        if (! sheet.contains (e.position) && onClose) onClose();   // the dim floor closes
    }

    void paint (juce::Graphics& g) override
    {
        hits.clear();
        g.fillAll (juce::Colour (0xff05060a).withAlpha (0.62f));   // the floor dims

        const float sw = juce::jmin (760.0f, (float) getWidth() - 60.0f);
        const float sh = juce::jmin (472.0f, (float) getHeight() - 60.0f);
        sheet = { ((float) getWidth() - sw) * 0.5f, ((float) getHeight() - sh) * 0.5f, sw, sh };

        // the machined vault window
        g.setColour (juce::Colours::black.withAlpha (0.45f));
        g.fillRoundedRectangle (sheet.translated (0.0f, 6.0f).expanded (2.0f), 16.0f);
        g.setColour (theme::panel.withAlpha (0.985f));
        g.fillRoundedRectangle (sheet, 14.0f);
        g.setGradientFill ({ juce::Colours::white.withAlpha (0.075f), sheet.getTopLeft(),
                             juce::Colours::white.withAlpha (0.0f),
                             { sheet.getX(), sheet.getY() + 90.0f }, false });
        g.fillRoundedRectangle (sheet, 14.0f);
        g.setColour (theme::accent.withAlpha (0.30f));
        g.drawRoundedRectangle (sheet.reduced (0.5f), 14.0f, 1.2f);
        g.setColour (juce::Colours::white.withAlpha (0.06f));
        g.drawRoundedRectangle (sheet.reduced (2.5f), 12.0f, 1.0f);   // inner seam

        auto in = sheet.reduced (22.0f, 16.0f);
        {   // header band: engraved title + song + close
            auto head = in.removeFromTop (34.0f);
            g.setColour (theme::text);
            g.setFont (theme::caps (13.0f));
            g.drawText ("CONNECTORS", head.toNearestInt(), juce::Justification::topLeft);
            g.setColour (theme::textMute);
            g.setFont (theme::ui (10.0f));
            g.drawText ("bridges between this song and every other world",
                        head.withTrimmedTop (17.0f).toNearestInt(), juce::Justification::topLeft);
            juce::Rectangle<float> x (head.getRight() - 24.0f, head.getY() - 2.0f, 24.0f, 24.0f);
            const bool hovX = hoverId == "close";
            g.setColour (theme::inset.withAlpha (hovX ? 1.0f : 0.75f));
            g.fillRoundedRectangle (x, 7.0f);
            g.setColour ((hovX ? theme::text : theme::textDim).withAlpha (0.9f));
            g.drawLine (x.getCentreX() - 4.0f, x.getCentreY() - 4.0f,
                        x.getCentreX() + 4.0f, x.getCentreY() + 4.0f, 1.4f);
            g.drawLine (x.getCentreX() - 4.0f, x.getCentreY() + 4.0f,
                        x.getCentreX() + 4.0f, x.getCentreY() - 4.0f, 1.4f);
            hits.push_back ({ x, "close" });
        }
        in.removeFromTop (6.0f);
        auto foot = in.removeFromBottom (18.0f);
        g.setColour (theme::textMute.withAlpha (0.75f));
        g.setFont (theme::ui (9.5f));
        g.drawText ("or just drop any .als / .flp / .rpp / .dawproject / .mid / audio file "
                    "straight onto the canvas",
                    foot.toNearestInt(), juce::Justification::centred);

        auto left = in.removeFromLeft (in.getWidth() * 0.5f - 9.0f);
        in.removeFromLeft (18.0f);
        drawColumn (g, left, "IMPORT A WORLD", imports(), nIn, false);
        drawColumn (g, in,   "EXPORT THIS SONG", exports(), nOut, true);
    }

private:
    void drawColumn (juce::Graphics& g, juce::Rectangle<float> col, const char* title,
                     const Tile* tiles, int n, bool isExport)
    {
        auto head = col.removeFromTop (20.0f);
        g.setColour ((isExport ? theme::good : theme::accent).withAlpha (0.9f));
        g.setFont (theme::caps (9.0f));
        g.drawText (title, head.toNearestInt(), juce::Justification::centredLeft);
        if (isExport && songName.isNotEmpty())
        {
            g.setColour (theme::textMute);
            g.setFont (theme::mono (9.0f));
            g.drawText (songName, head.toNearestInt(), juce::Justification::centredRight);
        }
        g.setColour (theme::line.withAlpha (0.7f));
        g.drawHorizontalLine ((int) col.getY(), col.getX(), col.getRight());
        col.removeFromTop (7.0f);

        const float rowH = juce::jmin (48.0f, (col.getHeight() - (float) (n - 1) * 7.0f) / (float) n);
        for (int i = 0; i < n; ++i)
        {
            auto r = col.removeFromTop (rowH);
            col.removeFromTop (7.0f);
            const auto& t = tiles[i];
            const bool hov = hoverId == t.id;
            const auto edge = isExport ? theme::good : theme::accent;
            if (hov) theme::glowRing (g, r, edge, 6.0f, 0.8f);
            g.setColour (theme::panelHi.withAlpha (hov ? 1.0f : 0.96f));   // machined, never frost
            g.fillRoundedRectangle (r, 9.0f);
            g.setGradientFill ({ juce::Colours::white.withAlpha (hov ? 0.09f : 0.05f),
                                 r.getTopLeft(), juce::Colours::white.withAlpha (0.0f),
                                 { r.getX(), r.getCentreY() }, false });
            g.fillRoundedRectangle (r, 9.0f);
            g.setColour (edge.withAlpha (hov ? 0.75f : 0.28f));
            g.drawRoundedRectangle (r.reduced (0.5f), 9.0f, 1.0f);
            auto inR = r.reduced (10.0f, 6.0f);
            {   // the format badge: engraved metal chip
                auto b = inR.removeFromLeft (40.0f).withSizeKeepingCentre (38.0f, 20.0f);
                g.setColour (theme::inset);
                g.fillRoundedRectangle (b, 5.0f);
                g.setColour (edge.withAlpha (hov ? 0.55f : 0.30f));
                g.drawRoundedRectangle (b.reduced (0.5f), 5.0f, 1.0f);
                g.setColour (hov ? theme::text : theme::textDim);
                g.setFont (theme::mono (9.5f, juce::Font::bold));
                g.drawText (t.badge, b.toNearestInt(), juce::Justification::centred);
                // in/out arrow: direction at a glance
                g.setColour (edge.withAlpha (0.8f));
                juce::Path a;
                const float ax = b.getRight() + 6.0f, ay = b.getCentreY();
                if (isExport) { a.addTriangle (ax, ay - 3.4f, ax, ay + 3.4f, ax + 5.4f, ay); }
                else          { a.addTriangle (ax + 5.4f, ay - 3.4f, ax + 5.4f, ay + 3.4f, ax, ay); }
                g.fillPath (a);
            }
            inR.removeFromLeft (14.0f);
            g.setColour (hov ? theme::text : theme::text.withAlpha (0.92f));
            g.setFont (theme::ui (12.0f, juce::Font::bold));
            g.drawText (t.name, inR.removeFromTop (inR.getHeight() * 0.52f).toNearestInt(),
                        juce::Justification::bottomLeft);
            g.setColour (theme::textMute.withAlpha (hov ? 1.0f : 0.85f));
            g.setFont (theme::ui (9.5f));
            g.drawText (t.sub, inR.toNearestInt(), juce::Justification::topLeft);
            hits.push_back ({ r, t.id });
        }
    }

    struct Hit { juce::Rectangle<float> r; juce::String id; };
    std::vector<Hit> hits;
    juce::Rectangle<float> sheet;
    juce::String songName;
    juce::String hoverId;
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ConnectorBay)
};
