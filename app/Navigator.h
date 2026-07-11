// Navigator.h — THE NAVIGATOR (fable-uxwave, 2026-07-10): the whole song in one
// strip. A pro-DAW overview under the ruler: every track is a colour band whose
// per-bar brightness is its note density (audio clips draw as solid blocks),
// sections wash + name their span, the loop brace rides the top edge, the
// playhead is a beam, and the arrange viewport is a grabbable PANE.
//
//   drag         = pan the arrange view (grab the pane anywhere on the strip)
//   double-click = locate the transport to that beat
//   wheel        = zoom the arrange view around that beat (same handleWheel law)
//
// LAG LAW (docs/LAG_DOSSIER.md): the static picture renders ONCE into an image
// keyed by an owner-computed signature; the playhead repaints two 7px columns;
// view changes repaint one ~30px strip at user-action rate. NO timer of its own —
// the owner's single clock calls tickPlayhead(), and refresh() is signature-gated.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

namespace sotadaw
{

class Navigator : public juce::Component
{
public:
    struct Band
    {
        juce::Colour colour;
        bool muted = false;
        std::vector<float> note;   // per-bar density 0..1
        std::vector<char>  audio;  // per-bar audio-clip presence
    };
    struct Sec { juce::String name; double startBeat = 0; };
    struct Model
    {
        double totalBeats = 16, loopA = -1, loopB = -1;
        std::vector<Band> bands;
        std::vector<Sec>  secs;
        juce::int64 sig = 0;       // owner-computed change signature
    };

    std::function<void (double)>        onView;    // drag -> new viewStart (beats)
    std::function<void (double)>        onLocate;  // double-click -> transport beat
    std::function<void (double, float)> onZoom;    // wheel -> (anchorBeat, delta)

    Navigator() { setMouseCursor (juce::MouseCursor::PointingHandCursor); }

    void setModel (Model&& m)
    {
        if (haveModel && m.sig == model.sig) return;
        model = std::move (m);
        haveModel = true;
        cacheDirty = true;
        repaint();
    }
    void setView (double startBeats, double visBeats)
    {
        if (std::abs (startBeats - viewStart) < 1e-9
            && std::abs (visBeats - viewBeats) < 1e-9) return;
        viewStart = startBeats;
        viewBeats = visBeats;
        repaint();
    }
    void tickPlayhead (double beats)
    {
        if (beats == playhead) return;
        const int ox = (int) xOf (playhead), nx = (int) xOf (beats);
        playhead = beats;
        if (! isShowing()) return;                    // unmapped strips never tick paints
        repaint (ox - 3, 0, 7, getHeight());
        repaint (nx - 3, 0, 7, getHeight());
    }

    void resized() override { cacheDirty = true; }

    void paint (juce::Graphics& g) override
    {
        const auto b = getLocalBounds();
        if (b.isEmpty()) return;
        if (cacheDirty || cache.getWidth() != b.getWidth() || cache.getHeight() != b.getHeight())
            rebuildCache();
        g.drawImageAt (cache, 0, 0);

        // the viewport pane (only when the view is narrower than the song)
        if (viewBeats > 0.01 && viewBeats < model.totalBeats - 0.01)
        {
            const float x0 = xOf (viewStart), x1 = xOf (viewStart + viewBeats);
            g.setColour (juce::Colours::black.withAlpha (0.30f));      // dim the elsewhere
            g.fillRect (0.0f, 0.0f, x0, (float) b.getHeight());
            g.fillRect (x1, 0.0f, (float) b.getWidth() - x1, (float) b.getHeight());
            juce::Rectangle<float> pane (x0, 1.0f, juce::jmax (6.0f, x1 - x0), (float) b.getHeight() - 2.0f);
            g.setColour (theme::accent.withAlpha (0.10f));
            g.fillRoundedRectangle (pane, 3.0f);
            g.setColour (theme::accent.withAlpha (dragging ? 0.95f : 0.65f));
            g.drawRoundedRectangle (pane, 3.0f, 1.2f);
        }
        // loop brace on the top edge
        if (model.loopB > model.loopA && model.loopA >= 0)
        {
            g.setColour (juce::Colour (0xffE8B84B).withAlpha (0.85f));
            g.fillRect (xOf (model.loopA), 0.0f, juce::jmax (2.0f, xOf (model.loopB) - xOf (model.loopA)), 2.0f);
        }
        // hover column (a whisper, not a banner)
        if (hoverBeat >= 0 && ! dragging)
        {
            g.setColour (juce::Colours::white.withAlpha (0.10f));
            g.fillRect ((int) xOf (hoverBeat), 0, 1, b.getHeight());
        }
        // playhead beam
        if (playhead >= 0)
        {
            const float x = xOf (playhead);
            g.setColour (juce::Colours::white.withAlpha (0.16f));
            g.fillRect (x - 1.5f, 0.0f, 3.0f, (float) b.getHeight());
            g.setColour (juce::Colours::white.withAlpha (0.85f));
            g.fillRect (x - 0.5f, 0.0f, 1.0f, (float) b.getHeight());
        }
    }

    void mouseDown (const juce::MouseEvent& e) override
    {
        if (e.mods.isPopupMenu()) return;
        const double beat = beatAt ((float) e.x);
        const bool inPane = viewBeats > 0.01 && beat >= viewStart && beat <= viewStart + viewBeats;
        grabOffset = inPane ? beat - viewStart : viewBeats * 0.5;
        dragging = true;
        if (! inPane && onView != nullptr) onView (beat - grabOffset);   // jump the pane to the hand
        repaint();
    }
    void mouseDrag (const juce::MouseEvent& e) override
    {
        if (dragging && onView != nullptr)
            onView (beatAt ((float) e.x) - grabOffset);
    }
    void mouseUp (const juce::MouseEvent&) override { dragging = false; repaint(); }
    void mouseDoubleClick (const juce::MouseEvent& e) override
    {
        if (onLocate != nullptr) onLocate (juce::jmax (0.0, beatAt ((float) e.x)));
    }
    void mouseWheelMove (const juce::MouseEvent& e, const juce::MouseWheelDetails& w) override
    {
        if (onZoom != nullptr) onZoom (beatAt ((float) e.x), (float) w.deltaY);
    }
    void mouseMove (const juce::MouseEvent& e) override
    {
        const double hb = beatAt ((float) e.x);
        if (std::abs (hb - hoverBeat) < 0.01) return;
        const int ox = (int) xOf (hoverBeat);
        hoverBeat = hb;
        repaint (ox - 1, 0, 3, getHeight());
        repaint ((int) xOf (hoverBeat) - 1, 0, 3, getHeight());
    }
    void mouseExit (const juce::MouseEvent&) override
    {
        const int ox = (int) xOf (hoverBeat);
        hoverBeat = -1;
        repaint (ox - 1, 0, 3, getHeight());
    }

private:
    static constexpr float padX = 2.0f;
    Model model;
    juce::Image cache;
    bool haveModel = false, cacheDirty = true, dragging = false;
    double viewStart = 0, viewBeats = 0, playhead = -1, hoverBeat = -1, grabOffset = 0;

    float span() const   { return juce::jmax (1.0f, (float) getWidth() - padX * 2.0f); }
    float xOf (double beat) const
    {
        return padX + (float) (juce::jlimit (0.0, model.totalBeats, beat)
                               / juce::jmax (1.0, model.totalBeats)) * span();
    }
    double beatAt (float px) const
    {
        return juce::jlimit (0.0, model.totalBeats,
                             (double) ((px - padX) / span()) * model.totalBeats);
    }

    void rebuildCache()
    {
        const int w = juce::jmax (1, getWidth()), h = juce::jmax (1, getHeight());
        if (cache.getWidth() != w || cache.getHeight() != h)
            cache = juce::Image (juce::Image::ARGB, w, h, true);
        else
            cache.clear (cache.getBounds());
        cacheDirty = false;
        juce::Graphics g (cache);

        // the floor: a shade below the panel so the strip reads as a well
        g.setColour (theme::bg.brighter (0.06f));
        g.fillRoundedRectangle (juce::Rectangle<float> (0, 0, (float) w, (float) h), 3.0f);

        const int labelH = model.secs.empty() ? 0 : 9;
        const auto rows = juce::Rectangle<int> (0, labelH, w, h - labelH).reduced (0, 1);

        // section washes + names (position palette, matches the ruler's chip spirit)
        for (size_t i = 0; i < model.secs.size(); ++i)
        {
            const auto& sc = model.secs[i];
            const double endB = i + 1 < model.secs.size() ? model.secs[i + 1].startBeat
                                                          : model.totalBeats;
            const float x0 = xOf (sc.startBeat), x1 = xOf (endB);
            const auto tint = juce::Colour::fromHSV (std::fmod (0.58f + (float) i * 0.13f, 1.0f),
                                                     0.45f, 0.95f, 1.0f);
            g.setColour (tint.withAlpha (0.07f));
            g.fillRect (x0, 0.0f, x1 - x0, (float) h);
            g.setColour (tint.withAlpha (0.30f));
            g.fillRect (x0, 0.0f, 1.0f, (float) h);
            if (x1 - x0 > 26.0f && labelH > 0)
            {
                g.setColour (tint.withAlpha (0.60f));
                g.setFont (juce::Font (juce::FontOptions (8.0f, juce::Font::bold)));
                g.drawText (sc.name.toUpperCase(),
                            juce::Rectangle<int> ((int) x0 + 3, 0, (int) (x1 - x0) - 6, labelH),
                            juce::Justification::centredLeft, true);
            }
        }
        // 4-bar orientation ticks
        g.setColour (juce::Colours::white.withAlpha (0.05f));
        for (double bt = 16.0; bt < model.totalBeats; bt += 16.0)
            g.fillRect (xOf (bt), (float) labelH, 1.0f, (float) (h - labelH));

        // the bands: every track a strip of its own colour
        if (! model.bands.empty())
        {
            const int n = (int) model.bands.size();
            const float bh = juce::jmax (1.0f, (float) rows.getHeight() / (float) n);
            const double barB = 4.0;
            const int bars = (int) std::ceil (model.totalBeats / barB);
            const float barW = (xOf (barB) - xOf (0.0));
            for (int t = 0; t < n; ++t)
            {
                const auto& bd = model.bands[(size_t) t];
                const float y = (float) rows.getY() + bh * (float) t;
                const float rh = juce::jmax (1.0f, bh - (bh > 2.5f ? 1.0f : 0.0f));
                const float dim = bd.muted ? 0.35f : 1.0f;
                for (int bi = 0; bi < bars && bi < (int) bd.note.size(); ++bi)
                {
                    const float x = xOf (bi * barB);
                    if (bd.audio[(size_t) bi] != 0)
                    {
                        g.setColour (bd.colour.withAlpha (0.85f * dim));
                        g.fillRect (x, y, juce::jmax (1.0f, barW - (barW > 3.0f ? 1.0f : 0.0f)), rh);
                    }
                    else if (bd.note[(size_t) bi] > 0.001f)
                    {
                        g.setColour (bd.colour.withAlpha ((0.20f + 0.65f * bd.note[(size_t) bi]) * dim));
                        g.fillRect (x, y, juce::jmax (1.0f, barW - (barW > 3.0f ? 1.0f : 0.0f)), rh);
                    }
                }
            }
        }
        // breathing edge law: a 1px rim so the strip reads as material, not paint
        g.setColour (juce::Colours::white.withAlpha (0.06f));
        g.drawRoundedRectangle (juce::Rectangle<float> (0.5f, 0.5f, (float) w - 1.0f, (float) h - 1.0f), 3.0f, 1.0f);
    }

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (Navigator)
};

} // namespace sotadaw
