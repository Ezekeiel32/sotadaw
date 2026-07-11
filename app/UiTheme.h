// SOTA DAW visual language v4 — the design system.
// Conventions borrowed deliberately: FL Studio (colored channels, stepped meters),
// Ableton (flat dark surfaces, minimal chrome, clip colors), Pro Tools (LCD transport),
// Cursor/Claude Code (chat cards, tool pills). Codified in docs/UI_SPEC.md.
// v3 added ATMOSPHERE: layered depth, brand glow, LED metering, machined controls.
// v4 is the 2026 FINISH: ghost controls (borderless until touched), glass surfaces,
// dot-lattice + film grain on the void, vignette — chrome recedes, the music leads.
#pragma once
#include <map>
#include <juce_gui_basics/juce_gui_basics.h>   // the theme is pure JUCE — no engine types
                                               // (uismoke paints it without linking tracktion)

namespace theme
{
    const juce::Colour bg        { 0xff07080d };   // window — deep space, blue-black
    const juce::Colour bgHi      { 0xff0c0e15 };   // window upper glow base
    const juce::Colour panel     { 0xff13151d };   // surfaces / cards
    const juce::Colour panelHi   { 0xff1a1d28 };   // raised surfaces (hover, chat agent card)
    const juce::Colour inset     { 0xff05060a };   // LCD / wells
    const juce::Colour lane      { 0xff11131b };
    const juce::Colour grid      { 0xff232735 };
    const juce::Colour gridBar   { 0xff333a4d };
    const juce::Colour line      { 0xff272c3d };   // hairline borders (blue-shifted)
    const juce::Colour text      { 0xffedeff7 };
    const juce::Colour textDim   { 0xff9ba3ba };
    const juce::Colour textMute  { 0xff5d6478 };
    const juce::Colour accent    { 0xff7c9bff };   // electric blue
    const juce::Colour accentB   { 0xffa78bfa };   // violet — the gradient partner
    const juce::Colour good      { 0xff3ddc97 };
    const juce::Colour warn      { 0xffffb86b };
    const juce::Colour bad       { 0xffff6b8a };
    const juce::Colour rec       { 0xffff5252 };
    const juce::Colour meterLo   { 0xff3ddc97 };
    const juce::Colour meterHi   { 0xffffd36b };

    // THE brand stroke: accent -> violet, left to right (buttons, active bars, focus)
    inline juce::ColourGradient brand (juce::Rectangle<float> r, float alpha = 1.0f)
    {
        return { accent.withMultipliedAlpha (alpha), r.getTopLeft(),
                 accentB.withMultipliedAlpha (alpha), r.getTopRight(), false };
    }
    // vertical panel depth: barely-lit top -> deep base; makes flat surfaces breathe
    inline void panelV (juce::Graphics& g, juce::Rectangle<float> r, juce::Colour base,
                        float corner = 8.0f)
    {
        g.setGradientFill ({ base.brighter (0.065f), r.getTopLeft(), base.darker (0.07f),
                             r.getBottomLeft(), false });
        g.fillRoundedRectangle (r, corner);
        g.setColour (juce::Colours::white.withAlpha (0.05f));
        g.drawHorizontalLine ((int) r.getY() + 1, r.getX() + corner, r.getRight() - corner);
    }
    inline void glowRing (juce::Graphics& g, juce::Rectangle<float> r, juce::Colour c,
                          float corner, float spread = 2.5f)
    {
        for (int i = 3; i >= 1; --i)
            g.setColour (c.withAlpha (0.055f * (float) i)),
            g.drawRoundedRectangle (r.expanded (spread * (float) (4 - i) * 0.5f), corner + 1.5f, 1.4f);
    }

    // dot lattice tile: the 2026 canvas texture (Figma/Linear ancestry) — visible
    // wherever surfaces part, invisible under them. One tiny cached image, tiled.
    inline const juce::Image& dotTile()
    {
        static const juce::Image img = []
        {
            juce::Image m (juce::Image::ARGB, 28, 28, true);
            juce::Graphics dg (m);
            dg.setColour (juce::Colours::white.withAlpha (0.055f));
            dg.fillEllipse (13.2f, 13.2f, 1.7f, 1.7f);
            return m;
        }();
        return img;
    }

    // film grain: sparse speckle that kills gradient banding and flat-black deadness.
    // Fixed seed — snapshots stay deterministic.
    inline const juce::Image& grain()
    {
        static const juce::Image img = []
        {
            juce::Image m (juce::Image::ARGB, 128, 128, true);
            juce::Random rnd (0x50DA0A11);
            juce::Image::BitmapData bd (m, juce::Image::BitmapData::writeOnly);
            for (int y = 0; y < 128; ++y)
                for (int x = 0; x < 128; ++x)
                {
                    const float v = rnd.nextFloat();
                    if (v > 0.962f)
                        bd.setPixelColour (x, y, juce::Colours::white.withAlpha ((juce::uint8) 14));
                    else if (v < 0.035f)
                        bd.setPixelColour (x, y, juce::Colours::black.withAlpha ((juce::uint8) 18));
                }
            return m;
        }();
        return img;
    }

    // THE ATMOSPHERE v4: wash + two brand blooms + dot lattice + grain + vignette.
    // Still cheap (two tiled fills + four gradients); timers repaint clipped regions.
    inline void renderBackdrop (juce::Graphics& g, juce::Rectangle<int> b)
    {
        auto r = b.toFloat();
        g.setGradientFill ({ bgHi, r.getTopLeft(), bg, { r.getX(), r.getHeight() * 0.55f }, false });
        g.fillRect (r);
        {   // accent bloom, upper right (under the agent dock)
            juce::ColourGradient gl (accent.withAlpha (0.06f), r.getRight() - r.getWidth() * 0.18f,
                                     r.getY() + 20.0f, accent.withAlpha (0.0f),
                                     r.getRight() - r.getWidth() * 0.18f, r.getY() + r.getHeight() * 0.7f, true);
            g.setGradientFill (gl);
            g.fillRect (r);
        }
        {   // violet bloom, lower left (under the rail / hear strip)
            juce::ColourGradient gl (accentB.withAlpha (0.05f), r.getX() + r.getWidth() * 0.12f,
                                     r.getBottom(), accentB.withAlpha (0.0f),
                                     r.getX() + r.getWidth() * 0.12f, r.getBottom() - r.getHeight() * 0.62f, true);
            g.setGradientFill (gl);
            g.fillRect (r);
        }
        g.setTiledImageFill (dotTile(), 0, 0, 1.0f);       // the lattice lives in the voids
        g.fillRect (r);
        g.setTiledImageFill (grain(), 0, 0, 1.0f);         // film over everything beneath panels
        g.fillRect (r);
        {   // vignette: the eye settles centre-stage
            juce::ColourGradient vg (juce::Colours::transparentBlack,
                                     r.getCentreX(), r.getCentreY() * 0.95f,
                                     juce::Colours::black.withAlpha (0.17f), r.getX(), r.getY(), true);
            vg.addColour (0.70, juce::Colours::transparentBlack);
            g.setGradientFill (vg);
            g.fillRect (r);
        }
    }

    // WAVE 4 (fable-lag, profiled): six full-surface passes — two RADIAL — made
    // one backdrop cost ~40-80ms at window size, and backdrop runs beneath EVERY
    // dirty rect of every page (radial rasterization alone = 25.1% of process
    // CPU during a pending-take playback storm; full-tree paints 141-210ms).
    // The scene is static per size: render ONCE, blit forever (~1ms).
    inline void backdrop (juce::Graphics& g, juce::Rectangle<int> b)
    {
        if (b.getWidth() < 2 || b.getHeight() < 2) return;
        static std::map<juce::int64, juce::Image> cache;
        const juce::int64 key = ((juce::int64) b.getWidth() << 24) ^ (juce::int64) b.getHeight();
        auto it = cache.find (key);
        if (it == cache.end())
        {
            if (cache.size() > 8) cache.clear();       // resize-churn bound
            juce::Image img (juce::Image::ARGB, b.getWidth(), b.getHeight(), true);
            juce::Graphics ig (img);
            renderBackdrop (ig, b.withZeroOrigin());
            it = cache.emplace (key, std::move (img)).first;
        }
        g.drawImageAt (it->second, b.getX(), b.getY());
    }

    // FL-style channel colors: stable per-track hue ring
    inline juce::Colour trackColour (int index)
    {
        static const juce::uint32 ring[] = { 0xff7aa2f7, 0xff81c995, 0xfff8b48a, 0xffe8837b,
                                             0xffc792ea, 0xff6cd9d3, 0xfff2d97f, 0xff8bd45f,
                                             0xffef8fb7, 0xff9aa7ff };
        return juce::Colour (ring[(size_t) (index % 10)]);
    }

    inline juce::Colour sourceColour (const juce::String& kind)
    {
        return kind == "faust" ? accent : kind == "sample" ? good
             : kind == "audio" ? meterHi : kind == "bus" ? warn : warn;
    }

    inline juce::Font mono (float h, int style = juce::Font::plain)
    {
        return juce::Font (juce::FontOptions (juce::Font::getDefaultMonospacedFontName(), h, style));
    }

    const juce::Colour agent { 0xffc792ea };   // the producer-agent's colour (violet)

    inline juce::Font ui (float h, int style = juce::Font::plain)
    {
        return juce::Font (juce::FontOptions (h, style));
    }

    // micro-caps: tracked-out bold labels (section headers, chips) — product typography
    inline juce::Font caps (float h)
    {
        return juce::Font (juce::FontOptions (h, juce::Font::bold)).withExtraKerningFactor (0.09f);
    }

    // text width without the deprecated Font::getStringWidth* (pills were truncating)
    inline float measure (const juce::Font& f, const juce::String& s)
    {
        juce::GlyphArrangement ga;
        ga.addLineOfText (f, s, 0.0f, 0.0f);
        return ga.getBoundingBox (0, -1, true).getWidth();
    }

    // instrument family colour — one visual language for rail, lanes, plugin faces
    inline juce::Colour familyColour (const juce::String& rawName)
    {
        const auto n = rawName.toLowerCase();
        auto any = [&n] (std::initializer_list<const char*> keys)
        {
            for (auto* k : keys) if (n.contains (k)) return true;
            return false;
        };
        if (any ({ "fx_", "reverb", "delay", "filter", "saturate", "widen", "pump", "trim", "brickwall", "compress" }))
            return juce::Colour (0xff9aa7ff);
        if (any ({ "kick", "snare", "hat", "clap", "perc", "808", "909", "drum", "shaker", "rim", "cymbal", "tom", "timpani" }))
            return juce::Colour (0xffe8837b);
        if (any ({ "bass", "sub", "reese", "wobble" }))            return juce::Colour (0xffc792ea);
        if (any ({ "key", "organ", "rhodes", "clav", "piano", "accordion" })) return juce::Colour (0xfff2d97f);
        if (any ({ "brass", "sax", "horn", "trumpet" }))           return juce::Colour (0xfff8b48a);
        if (any ({ "marimba", "kalimba", "steel", "vibra", "log_", "bell", "glock", "harp", "chime" }))
            return juce::Colour (0xff81c995);
        if (any ({ "lead", "saw", "pluck", "acid", "arp", "flute", "whistle" })) return juce::Colour (0xff6cd9d3);
        if (any ({ "pad", "string", "vox", "choir", "drone" }))    return juce::Colour (0xff7aa2f7);
        return juce::Colour (0xff8fa1b3);
    }

    // raised card: soft LARGE shadow + fill + top-light — 2026 elevation is generous
    inline void card (juce::Graphics& g, juce::Rectangle<float> r, juce::Colour fill,
                      float corner = 10.0f, float borderAlpha = 1.0f)
    {
        g.setColour (juce::Colours::black.withAlpha (0.13f));
        g.fillRoundedRectangle (r.translated (0.0f, 3.5f).expanded (2.0f), corner + 2.0f);
        g.setColour (juce::Colours::black.withAlpha (0.26f));
        g.fillRoundedRectangle (r.translated (0.0f, 1.4f).expanded (0.5f), corner + 0.5f);
        g.setGradientFill ({ fill.brighter (0.05f), r.getTopLeft(),
                             fill.darker (0.05f), r.getBottomLeft(), false });
        g.fillRoundedRectangle (r, corner);
        g.setColour (juce::Colours::white.withAlpha (0.045f * borderAlpha));
        g.drawRoundedRectangle (r.reduced (0.5f), corner, 1.0f);
        g.setColour (juce::Colours::white.withAlpha (0.06f * borderAlpha));
        g.drawHorizontalLine ((int) r.getY() + 1, r.getX() + corner * 0.8f, r.getRight() - corner * 0.8f);
    }

    // typed chip: tinted pill + identity dot + label. One drawing for tray chips,
    // lane chips, rail badges, prop items — the SAME object everywhere.
    inline void chip (juce::Graphics& g, juce::Rectangle<float> r, juce::Colour c,
                      const juce::String& label, const juce::Font& f,
                      float fillAlpha = 0.15f, float borderAlpha = 0.55f, bool dot = true)
    {
        const float cr = r.getHeight() * 0.5f;
        g.setColour (c.withAlpha (fillAlpha));
        g.fillRoundedRectangle (r, cr);
        g.setColour (c.withAlpha (borderAlpha));
        g.drawRoundedRectangle (r.reduced (0.5f), cr, 1.0f);
        float tx = r.getX() + 7.0f;
        if (dot)
        {
            g.setColour (c.brighter (0.25f));
            g.fillEllipse (r.getX() + 6.0f, r.getCentreY() - 2.0f, 4.0f, 4.0f);
            tx += 6.0f;
        }
        g.setColour (c.brighter (0.35f));
        g.setFont (f);
        g.drawText (label, juce::Rectangle<float> (tx, r.getY(), r.getRight() - tx - 6.0f,
                                                   r.getHeight()).toNearestInt(),
                    juce::Justification::centredLeft);
    }

    // drag ghost: a compact glass chip (dot + label) that rides the mouse.
    // NEVER let startDragging default to a source-component snapshot — dragging
    // a rail row used to carry a screenshot of the ENTIRE list (2026-07-11).
    inline juce::ScaledImage dragChip (const juce::String& label, juce::Colour c)
    {
        const float scale = 2.0f;                      // crisp on hidpi
        const auto f = ui (12.0f, juce::Font::bold);
        const int w = juce::jlimit (64, 240, (int) measure (f, label) + 34);
        const int h = 24;
        juce::Image img (juce::Image::ARGB, (int) (w * scale), (int) (h * scale), true);
        juce::Graphics g (img);
        g.addTransform (juce::AffineTransform::scale (scale));
        juce::Rectangle<float> r (0.5f, 0.5f, (float) w - 1.0f, (float) h - 1.0f);
        g.setColour (juce::Colour (0xf011131c));       // glass slab (mostly opaque)
        g.fillRoundedRectangle (r, 11.0f);
        g.setColour (c.withAlpha (0.20f));
        g.fillRoundedRectangle (r, 11.0f);
        g.setColour (c.withAlpha (0.9f));
        g.drawRoundedRectangle (r, 11.0f, 1.2f);
        g.setColour (c.brighter (0.25f));
        g.fillEllipse (9.0f, (float) h * 0.5f - 3.0f, 6.0f, 6.0f);
        g.setColour (juce::Colours::white.withAlpha (0.95f));
        g.setFont (f);
        g.drawText (label, 21, 0, w - 27, h, juce::Justification::centredLeft);
        return juce::ScaledImage (img, scale);
    }

    // LED meter: inset well + gradient column lit to `frac`, segmented like hardware.
    // vertical = true draws bottom-up. Peak tick drawn by the caller (it owns the state).
    inline void ledMeter (juce::Graphics& g, juce::Rectangle<float> r, float frac,
                          juce::Colour lo, juce::Colour hi, bool vertical = true)
    {
        g.setColour (inset);
        g.fillRoundedRectangle (r, 2.5f);
        frac = juce::jlimit (0.0f, 1.0f, frac);
        if (frac > 0.004f)
        {
            auto lit = vertical ? r.withTrimmedTop (r.getHeight() * (1.0f - frac))
                                : r.withTrimmedRight (r.getWidth() * (1.0f - frac));
            if (vertical)
                g.setGradientFill ({ lo, { r.getCentreX(), r.getBottom() },
                                     hi, { r.getCentreX(), r.getY() }, false });
            else
                g.setGradientFill ({ lo, { r.getX(), r.getCentreY() },
                                     hi, { r.getRight(), r.getCentreY() }, false });
            g.fillRoundedRectangle (lit, 2.0f);
            g.setColour (juce::Colours::white.withAlpha (0.18f));   // hot cap on the lit edge
            if (vertical) g.fillRect (lit.getX(), lit.getY(), lit.getWidth(), 1.5f);
            else          g.fillRect (lit.getRight() - 1.5f, lit.getY(), 1.5f, lit.getHeight());
        }
        g.setColour (inset.withAlpha (0.85f));                      // segmentation slits
        if (vertical)
            for (float y = r.getBottom() - 3.0f; y > r.getY(); y -= 3.0f)
                g.fillRect (r.getX(), y, r.getWidth(), 1.0f);
        else
            for (float x = r.getX() + 3.0f; x < r.getRight(); x += 3.0f)
                g.fillRect (x, r.getY(), 1.0f, r.getHeight());
    }

    // disabled controls dim EVERYTHING they draw (setOpacity dies at the next
    // setColour — a transparency layer survives; RAII keeps early returns safe)
    struct DimScope
    {
        juce::Graphics& g; bool on;
        DimScope (juce::Graphics& gg, bool dim, float alpha = 0.38f) : g (gg), on (dim)
        { if (on) g.beginTransparencyLayer (alpha); }
        ~DimScope() { if (on) g.endTransparencyLayer(); }
    };

    // the agent's spark — drawn, never a font glyph (no UTF-8 roulette)
    inline void spark (juce::Graphics& g, juce::Rectangle<float> r, juce::Colour c)
    {
        juce::Path p;
        const float cx = r.getCentreX(), cy = r.getCentreY(),
                    R = r.getWidth() * 0.5f, k = R * 0.32f;
        p.startNewSubPath (cx, cy - R);
        p.quadraticTo (cx + k * 0.4f, cy - k * 0.4f, cx + R, cy);
        p.quadraticTo (cx + k * 0.4f, cy + k * 0.4f, cx, cy + R);
        p.quadraticTo (cx - k * 0.4f, cy + k * 0.4f, cx - R, cy);
        p.quadraticTo (cx - k * 0.4f, cy - k * 0.4f, cx, cy - R);
        p.closeSubPath();
        g.setColour (c);
        g.fillPath (p);
    }
}

class SotaLookAndFeel : public juce::LookAndFeel_V4
{
public:
    SotaLookAndFeel()
    {
        setColour (juce::ResizableWindow::backgroundColourId, theme::bg);
        setColour (juce::TextButton::buttonColourId, theme::panel);
        setColour (juce::TextButton::buttonOnColourId, theme::accent.withAlpha (0.25f));
        setColour (juce::TextButton::textColourOffId, theme::text);
        setColour (juce::TextButton::textColourOnId, theme::text);
        setColour (juce::TextEditor::backgroundColourId, theme::panel);
        setColour (juce::TextEditor::textColourId, theme::text);
        setColour (juce::TextEditor::outlineColourId, theme::line);
        setColour (juce::TextEditor::focusedOutlineColourId, theme::accent.withAlpha (0.6f));
        setColour (juce::Label::textColourId, theme::textDim);
        setColour (juce::Slider::trackColourId, theme::accent.withAlpha (0.5f));
        setColour (juce::Slider::backgroundColourId, theme::grid);
        setColour (juce::Slider::thumbColourId, theme::text);
        setColour (juce::PopupMenu::backgroundColourId, theme::panelHi);
        setColour (juce::PopupMenu::textColourId, theme::text);
        setColour (juce::PopupMenu::highlightedBackgroundColourId, theme::accent.withAlpha (0.25f));
        setColour (juce::ComboBox::backgroundColourId, theme::panel);
        setColour (juce::ComboBox::textColourId, theme::text);
        setColour (juce::ComboBox::outlineColourId, theme::line);
        setColour (juce::ComboBox::arrowColourId, theme::textDim);
        setColour (juce::ScrollBar::thumbColourId, theme::gridBar);
        setColour (juce::ScrollBar::trackColourId, theme::inset);
        setColour (juce::TooltipWindow::backgroundColourId, theme::panelHi);
        setColour (juce::TooltipWindow::textColourId, theme::text);
        setColour (juce::TooltipWindow::outlineColourId, theme::line);
    }

    void drawButtonBackground (juce::Graphics& g, juce::Button& b, const juce::Colour&,
                               bool highlighted, bool down) override
    {
        theme::DimScope dim (g, ! b.isEnabled());          // a dead control must LOOK dead
        auto r = b.getLocalBounds().toFloat().reduced (1.0f);
        const auto id = b.getComponentID();
        if (id == "mute" || id == "solo")                             // channel DOTS (2026: circular, ghost off)
        {
            const auto base = id == "mute" ? juce::Colour (0xfff0a35c) : theme::good;
            auto c = r.withSizeKeepingCentre (juce::jmin (r.getWidth(), r.getHeight()),
                                              juce::jmin (r.getWidth(), r.getHeight()));
            if (b.getToggleState())
            {
                g.setColour (base.withAlpha (0.28f));                 // lit halo
                g.fillEllipse (c.expanded (2.0f));
                g.setGradientFill ({ (highlighted ? base.brighter (0.15f) : base.brighter (0.05f)),
                                     c.getTopLeft(), base.darker (0.14f), c.getBottomLeft(), false });
                g.fillEllipse (c);
            }
            else
            {
                g.setColour (juce::Colours::white.withAlpha (highlighted ? 0.10f : 0.045f));
                g.fillEllipse (c);
                g.setColour (juce::Colours::white.withAlpha (highlighted ? 0.22f : 0.10f));
                g.drawEllipse (c.reduced (0.5f), 1.0f);
            }
            return;
        }
        if (id == "primary" || id == "danger" || id == "confirm")     // filled action buttons
        {
            auto base = id == "danger" ? theme::bad : id == "confirm" ? theme::good : theme::accent;
            if (down) r = r.reduced (0.0f, 0.5f).translated (0.0f, 0.5f);
            theme::glowRing (g, r, id == "primary" ? theme::accentB : base, 7.0f);   // living glow
            if (id == "primary")
                g.setGradientFill (theme::brand (r, highlighted ? 1.0f : 0.92f));
            else
                g.setColour (highlighted ? base.brighter (0.12f) : base);
            g.fillRoundedRectangle (r, 7.0f);
            g.setGradientFill ({ juce::Colours::white.withAlpha (0.22f), r.getTopLeft(),
                                 juce::Colours::white.withAlpha (0.0f),
                                 { r.getX(), r.getY() + r.getHeight() * 0.55f }, false });
            g.fillRoundedRectangle (r, 7.0f);                          // glass sheen
            return;
        }
        // default: GHOST control (2026 law — borderless until touched, lit when true)
        if (b.getToggleState())
        {
            const auto c = theme::panelHi.interpolatedWith (theme::accent, highlighted ? 0.22f : 0.16f);
            g.setGradientFill ({ c.brighter (0.10f), r.getTopLeft(), c.darker (0.08f),
                                 r.getBottomLeft(), false });
            g.fillRoundedRectangle (r, 7.0f);
            g.setGradientFill (theme::brand (r.withHeight (2.0f), 0.9f));   // lit top edge
            g.fillRoundedRectangle (r.getX() + 3.0f, r.getY() + 0.5f, r.getWidth() - 6.0f, 2.0f, 1.0f);
            g.setColour (theme::accent.withAlpha (0.50f));
            g.drawRoundedRectangle (r.reduced (0.5f), 7.0f, 1.0f);
            return;
        }
        const float lift = down ? 0.13f : highlighted ? 0.085f : 0.035f;
        g.setGradientFill ({ juce::Colours::white.withAlpha (lift), r.getTopLeft(),
                             juce::Colours::white.withAlpha (lift * 0.45f), r.getBottomLeft(), false });
        g.fillRoundedRectangle (r, 7.0f);
        if (highlighted || down)
        {
            g.setColour (juce::Colours::white.withAlpha (down ? 0.16f : 0.09f));
            g.drawRoundedRectangle (r.reduced (0.5f), 7.0f, 1.0f);
        }
    }

    void drawButtonText (juce::Graphics& g, juce::TextButton& b, bool, bool) override
    {
        theme::DimScope dim (g, ! b.isEnabled());
        const auto id = b.getComponentID();
        const bool filled = id == "primary" || id == "danger" || id == "confirm";
        const bool pill = id == "mute" || id == "solo";
        g.setColour ((filled || (pill && b.getToggleState()))
                       ? theme::inset
                       : pill ? theme::textMute.brighter (0.15f)
                              : b.findColour (b.getToggleState() ? juce::TextButton::textColourOnId
                                                                 : juce::TextButton::textColourOffId));
        g.setFont (theme::ui (pill ? 9.5f : filled ? 13.0f : 12.5f,
                              (filled || pill) ? juce::Font::bold : juce::Font::plain));
        g.drawText (b.getButtonText(), b.getLocalBounds().reduced (pill ? 0 : 4, 0), juce::Justification::centred);
    }

    // linear sliders: hairline track + glow thumb; bipolar (pan) fills from centre
    void drawLinearSlider (juce::Graphics& g, int x, int y, int w, int h, float sliderPos,
                           float, float, juce::Slider::SliderStyle style, juce::Slider& s) override
    {
        if (style != juce::Slider::LinearHorizontal)
        {
            juce::LookAndFeel_V4::drawLinearSlider (g, x, y, w, h, sliderPos, 0, 0, style, s);
            return;
        }
        const float cy = (float) y + (float) h * 0.5f;
        auto track = juce::Rectangle<float> ((float) x, cy - 1.75f, (float) w, 3.5f);
        g.setColour (theme::inset);
        g.fillRoundedRectangle (track.expanded (0.0f, 0.75f), 2.4f);
        g.setColour (theme::grid.brighter (0.06f));
        g.fillRoundedRectangle (track, 2.0f);
        const bool bipolar = s.getMinimum() < 0.0 && s.getMaximum() > 0.0;
        const auto fillCol = s.findColour (juce::Slider::trackColourId);
        const float zeroX = bipolar
            ? (float) x + (float) w * (float) ((0.0 - s.getMinimum()) / (s.getMaximum() - s.getMinimum()))
            : (float) x;
        auto fill = juce::Rectangle<float> (juce::jmin (zeroX, sliderPos), cy - 1.75f,
                                            std::abs (sliderPos - zeroX), 3.5f);
        g.setColour (fillCol);
        g.fillRoundedRectangle (fill, 2.0f);
        g.setColour (fillCol.withAlpha (0.35f));                    // thumb halo
        g.fillEllipse (sliderPos - 7.0f, cy - 7.0f, 14.0f, 14.0f);
        g.setColour (theme::text);
        g.fillEllipse (sliderPos - 4.5f, cy - 4.5f, 9.0f, 9.0f);
        g.setColour (theme::inset);
        g.drawEllipse (sliderPos - 4.5f, cy - 4.5f, 9.0f, 9.0f, 1.0f);
    }

    // FL-grade knob: dark cap w/ radial sheen, brand value arc, glow dot at the tip
    void drawRotarySlider (juce::Graphics& g, int x, int y, int w, int h, float pos,
                           float startAngle, float endAngle, juce::Slider& s) override
    {
        auto r = juce::Rectangle<float> ((float) x, (float) y, (float) w, (float) h)
                     .reduced (4.0f).withSizeKeepingCentre (juce::jmin (w, h) - 8.0f,
                                                            juce::jmin (w, h) - 8.0f);
        const float angle = startAngle + pos * (endAngle - startAngle);
        const float rad = r.getWidth() * 0.5f;
        const auto centre = r.getCentre();
        // track arc
        juce::Path track;
        track.addCentredArc (centre.x, centre.y, rad, rad, 0.0f, startAngle, endAngle, true);
        g.setColour (theme::inset);
        g.strokePath (track, { 4.5f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        // value arc = the brand
        juce::Path val;
        val.addCentredArc (centre.x, centre.y, rad, rad, 0.0f, startAngle, angle, true);
        g.setGradientFill (theme::brand (r));
        g.strokePath (val, { 3.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        // cap with radial light
        auto cap = r.reduced (rad * 0.28f);
        g.setGradientFill ({ theme::panelHi.brighter (0.18f), cap.getCentreX(), cap.getY(),
                             theme::panel.darker (0.2f), cap.getCentreX(), cap.getBottom(), false });
        g.fillEllipse (cap);
        g.setColour (theme::line.brighter (0.15f));
        g.drawEllipse (cap.reduced (0.5f), 1.0f);
        // pointer + tip glow
        const auto tip = centre.getPointOnCircumference (rad - 1.0f, angle);
        const auto inner = centre.getPointOnCircumference (cap.getWidth() * 0.32f, angle);
        g.setColour (theme::text);
        g.drawLine ({ inner, centre.getPointOnCircumference (cap.getWidth() * 0.5f - 2.0f, angle) }, 2.2f);
        g.setColour (theme::accentB.withAlpha (0.55f));
        g.fillEllipse (tip.x - 3.5f, tip.y - 3.5f, 7.0f, 7.0f);
        g.setColour (juce::Colours::white);
        g.fillEllipse (tip.x - 1.5f, tip.y - 1.5f, 3.0f, 3.0f);
        juce::ignoreUnused (s);
    }

    // combo: quiet recessed well, borderless until focus (ghost law)
    void drawComboBox (juce::Graphics& g, int width, int height, bool, int, int, int, int,
                       juce::ComboBox& box) override
    {
        auto r = juce::Rectangle<float> (0, 0, (float) width, (float) height).reduced (1.0f);
        g.setColour (theme::inset.withAlpha (0.55f));
        g.fillRoundedRectangle (r, 7.0f);
        g.setColour (juce::Colours::white.withAlpha (box.hasKeyboardFocus (true) ? 0.0f : 0.055f));
        g.drawRoundedRectangle (r.reduced (0.5f), 7.0f, 1.0f);
        if (box.hasKeyboardFocus (true))
        {
            g.setColour (theme::accent.withAlpha (0.55f));
            g.drawRoundedRectangle (r.reduced (0.5f), 7.0f, 1.0f);
        }
        juce::Path ch;
        const float cx = (float) width - 14.0f, cy = (float) height * 0.5f;
        ch.startNewSubPath (cx - 4.0f, cy - 2.0f);
        ch.lineTo (cx, cy + 2.5f);
        ch.lineTo (cx + 4.0f, cy - 2.0f);
        g.setColour (theme::accent);
        g.strokePath (ch, { 1.8f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
    }
    juce::Font getComboBoxFont (juce::ComboBox&) override { return theme::ui (12.5f); }

    // menus float: MACHINED GLASS (vault law) — deep shadow, sheen lip, brushed body
    void drawPopupMenuBackground (juce::Graphics& g, int width, int height) override
    {
        juce::Rectangle<float> r (0, 0, (float) width, (float) height);
        g.fillAll (juce::Colours::transparentBlack);
        g.setColour (juce::Colours::black.withAlpha (0.50f));            // sits proud
        g.fillRoundedRectangle (r.reduced (1.0f).translated (0.0f, 2.5f), 10.0f);
        theme::panelV (g, r.reduced (1.0f), theme::panelHi, 10.0f);
        {   // brushed body + top sheen: machined hardware, never a flat slab
            juce::Graphics::ScopedSaveState ss (g);
            juce::Path clip;
            clip.addRoundedRectangle (r.reduced (1.0f), 10.0f);
            g.reduceClipRegion (clip);
            g.setColour (juce::Colours::white.withAlpha (0.012f));
            for (float y = r.getY() + 4.0f; y < r.getBottom(); y += 3.0f)
                g.drawHorizontalLine ((int) y, r.getX() + 3.0f, r.getRight() - 3.0f);
            g.setGradientFill ({ juce::Colours::white.withAlpha (0.06f), r.getTopLeft(),
                                 juce::Colours::white.withAlpha (0.0f),
                                 { r.getX(), r.getY() + 14.0f }, false });
            g.fillRect (r.withHeight (14.0f));
        }
        g.setColour (juce::Colours::white.withAlpha (0.085f));
        g.drawRoundedRectangle (r.reduced (1.5f), 10.0f, 1.0f);
        g.setColour (theme::accent.withAlpha (0.10f));                   // the quiet rim
        g.drawRoundedRectangle (r.reduced (0.5f), 10.5f, 1.0f);
    }
    void drawPopupMenuItem (juce::Graphics& g, const juce::Rectangle<int>& area, bool isSeparator,
                            bool isActive, bool isHighlighted, bool isTicked, bool hasSubMenu,
                            const juce::String& text, const juce::String& shortcutKeyText,
                            const juce::Drawable*, const juce::Colour* textColour) override
    {
        auto r = area.toFloat().reduced (4.0f, 1.0f);
        if (isSeparator)
        {
            g.setColour (theme::line);
            g.drawHorizontalLine ((int) r.getCentreY(), r.getX() + 6.0f, r.getRight() - 6.0f);
            return;
        }
        // THE SWATCH CONTRACT: an item carrying a colour and no words IS that colour
        // — a real paint chip. (The channel-colour picker painted BLANK rows before:
        // this hook dropped the Colour* on the floor — Chezy's void-submenu shot.)
        if (textColour != nullptr && text.trim().isEmpty())
        {
            auto chip = r.reduced (8.0f, 3.0f);
            g.setColour (juce::Colours::black.withAlpha (0.35f));        // the seat
            g.fillRoundedRectangle (chip.expanded (1.0f), 6.0f);
            g.setGradientFill ({ textColour->brighter (0.15f), chip.getTopLeft(),
                                 textColour->darker (0.10f), chip.getBottomLeft(), false });
            g.fillRoundedRectangle (chip, 5.0f);
            g.setColour (juce::Colours::white.withAlpha (0.28f));        // gloss lip
            g.fillRoundedRectangle (chip.withHeight (juce::jmax (2.0f, chip.getHeight() * 0.34f)), 5.0f);
            g.setColour (juce::Colours::black.withAlpha (0.45f));
            g.drawRoundedRectangle (chip, 5.0f, 1.0f);
            if (isHighlighted || isTicked)                               // the hand / the state
            {
                g.setColour (juce::Colours::white.withAlpha (isTicked ? 0.95f : 0.75f));
                g.drawRoundedRectangle (chip.expanded (1.5f), 6.5f, isTicked ? 1.6f : 1.2f);
            }
            return;
        }
        if (isHighlighted && isActive)
        {
            g.setGradientFill (theme::brand (r, 0.26f));
            g.fillRoundedRectangle (r, 6.0f);
            g.setColour (juce::Colours::white.withAlpha (0.07f));        // glass top-light
            g.drawHorizontalLine ((int) r.getY() + 1, r.getX() + 6.0f, r.getRight() - 6.0f);
            g.setColour (theme::accent.withAlpha (0.85f));               // the lit spine
            g.fillRoundedRectangle (r.getX() + 1.0f, r.getY() + 3.5f, 2.5f, r.getHeight() - 7.0f, 1.2f);
        }
        const auto ink = ! isActive             ? theme::textMute
                       : textColour != nullptr  ? *textColour
                       : isHighlighted          ? theme::text : theme::textDim;
        g.setFont (theme::ui (12.5f, isHighlighted && isActive ? juce::Font::bold
                                                               : juce::Font::plain));
        auto tr = r.reduced (12.0f, 0.0f);
        if (isTicked)
        {   // a crisp check, not an ambiguous dot — state reads at a glance
            juce::Path ck;
            const float cx = tr.getX() - 3.0f, cy = r.getCentreY();
            ck.startNewSubPath (cx - 3.5f, cy + 0.2f);
            ck.lineTo (cx - 1.0f, cy + 2.8f);
            ck.lineTo (cx + 3.6f, cy - 2.8f);
            g.setColour (theme::accentB);
            g.strokePath (ck, { 1.7f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded });
        }
        g.setColour (ink);
        g.drawText (text, tr.withTrimmedLeft (isTicked ? 9.0f : 0.0f).toNearestInt(),
                    juce::Justification::centredLeft);
        if (shortcutKeyText.isNotEmpty())
        {   // key hints wear KEYCAPS — the '?' map's language, on every menu
            const auto kf = theme::mono (9.5f, juce::Font::bold);
            const float kw = theme::measure (kf, shortcutKeyText) + 10.0f;
            juce::Rectangle<float> cap (tr.getRight() - kw, r.getCentreY() - 8.0f, kw, 16.0f);
            g.setColour (theme::inset.withAlpha (0.85f));
            g.fillRoundedRectangle (cap, 4.0f);
            g.setColour (juce::Colours::white.withAlpha (0.08f));
            g.drawRoundedRectangle (cap.reduced (0.5f), 4.0f, 1.0f);
            g.setColour (theme::textDim);
            g.setFont (kf);
            g.drawText (shortcutKeyText, cap.toNearestInt(), juce::Justification::centred);
        }
        if (hasSubMenu)
        {
            juce::Path p;
            p.addTriangle (tr.getRight() - 6.0f, r.getCentreY() - 3.5f,
                           tr.getRight() - 6.0f, r.getCentreY() + 3.5f,
                           tr.getRight() - 1.0f, r.getCentreY());
            g.setColour (isHighlighted ? theme::text : theme::textDim);
            g.fillPath (p);
        }
    }
    void drawPopupMenuSectionHeader (juce::Graphics& g, const juce::Rectangle<int>& area,
                                     const juce::String& name) override
    {   // headers are ENGRAVED: accent tick + caps + hairline — a labelled rack rail
        auto r = area.toFloat().reduced (10.0f, 0.0f);
        g.setColour (theme::accent.withAlpha (0.85f));
        g.fillRoundedRectangle (r.getX() - 2.0f, r.getCentreY() - 4.0f, 3.0f, 8.0f, 1.5f);
        g.setColour (theme::textMute.brighter (0.15f));
        g.setFont (theme::caps (9.0f));
        g.drawText (name.toUpperCase(), r.withTrimmedLeft (8.0f).toNearestInt(),
                    juce::Justification::centredLeft);
        g.setColour (juce::Colours::white.withAlpha (0.05f));
        g.drawHorizontalLine ((int) r.getBottom() - 1, r.getX(), r.getRight());
    }
    void getIdealPopupMenuItemSize (const juce::String& text, bool isSeparator,
                                    int standardMenuItemHeight, int& idealWidth,
                                    int& idealHeight) override
    {   // air: items breathe; swatch rows stay compact paint chips
        LookAndFeel_V4::getIdealPopupMenuItemSize (text, isSeparator, standardMenuItemHeight,
                                                   idealWidth, idealHeight);
        if (isSeparator) return;
        if (text.trim().isEmpty()) { idealHeight = 20; idealWidth = juce::jmax (idealWidth, 150); }
        else                       { idealHeight = juce::jmax (idealHeight, 24); idealWidth += 14; }
    }
    int getPopupMenuBorderSize() override { return 7; }

    // menu bar: the app's command surface — flat, tracked-out, brand-lit when open
    void drawMenuBarBackground (juce::Graphics& g, int width, int height, bool,
                                juce::MenuBarComponent&) override
    {
        juce::Rectangle<float> r (0, 0, (float) width, (float) height);
        g.setGradientFill ({ theme::bgHi.brighter (0.035f), r.getTopLeft(),
                             theme::bgHi, r.getBottomLeft(), false });
        g.fillRect (r);
        g.setColour (theme::line.withAlpha (0.7f));
        g.drawHorizontalLine (height - 1, 0.0f, (float) width);
    }
    juce::Font getMenuBarFont (juce::MenuBarComponent&, int, const juce::String&) override
    {
        return theme::ui (12.5f);
    }
    void drawMenuBarItem (juce::Graphics& g, int width, int height, int, const juce::String& itemText,
                          bool isMouseOver, bool isMenuOpen, bool, juce::MenuBarComponent&) override
    {
        auto r = juce::Rectangle<float> (0, 0, (float) width, (float) height).reduced (2.0f, 3.0f);
        if (isMenuOpen)
        {
            g.setGradientFill (theme::brand (r, 0.24f));
            g.fillRoundedRectangle (r, 5.0f);
            g.setColour (theme::accent.withAlpha (0.45f));
            g.drawRoundedRectangle (r.reduced (0.5f), 5.0f, 1.0f);
        }
        else if (isMouseOver)
        {
            g.setColour (juce::Colours::white.withAlpha (0.06f));
            g.fillRoundedRectangle (r, 5.0f);
        }
        g.setColour (isMenuOpen ? theme::text : isMouseOver ? theme::text.withAlpha (0.9f) : theme::textDim);
        g.setFont (theme::ui (12.5f));
        g.drawText (itemText, 0, 0, width, height, juce::Justification::centred);
    }

    // scrollbars: 6px pill, brand-tinted on hover
    void drawScrollbar (juce::Graphics& g, juce::ScrollBar& bar, int x, int y, int w, int h,
                        bool vertical, int thumbStart, int thumbSize, bool mouseOver, bool down) override
    {
        juce::ignoreUnused (bar);
        auto thumb = vertical
            ? juce::Rectangle<float> ((float) x + (float) w * 0.5f - 3.0f, (float) thumbStart, 6.0f, (float) thumbSize)
            : juce::Rectangle<float> ((float) thumbStart, (float) y + (float) h * 0.5f - 3.0f, (float) thumbSize, 6.0f);
        g.setColour ((mouseOver || down) ? theme::accent.withAlpha (0.55f) : theme::gridBar);
        g.fillRoundedRectangle (thumb, 3.0f);
    }

    // text fields: inset rounded well + focus glow
    void fillTextEditorBackground (juce::Graphics& g, int width, int height, juce::TextEditor& te) override
    {
        juce::ignoreUnused (te);
        auto r = juce::Rectangle<float> (0, 0, (float) width, (float) height).reduced (1.0f);
        g.setColour (theme::inset);
        g.fillRoundedRectangle (r, 9.0f);
        g.setGradientFill ({ juce::Colours::black.withAlpha (0.35f), r.getTopLeft(),
                             juce::Colours::black.withAlpha (0.0f),
                             { r.getX(), r.getY() + 7.0f }, false });
        g.fillRoundedRectangle (r, 9.0f);                            // inner top shadow: a real well
    }
    void drawTextEditorOutline (juce::Graphics& g, int width, int height, juce::TextEditor& te) override
    {
        auto r = juce::Rectangle<float> (0, 0, (float) width, (float) height).reduced (1.0f);
        if (te.hasKeyboardFocus (true))
        {
            theme::glowRing (g, r, theme::accent, 9.0f);
            g.setColour (theme::accent.withAlpha (0.7f));
        }
        else
            g.setColour (juce::Colours::white.withAlpha (0.06f));
        g.drawRoundedRectangle (r.reduced (0.5f), 9.0f, 1.2f);
    }

    // tooltips: a small glass card with a brand crown — the app explains itself
    juce::Rectangle<int> getTooltipBounds (const juce::String& tipText, juce::Point<int> screenPos,
                                           juce::Rectangle<int> parentArea) override
    {
        const auto tl = layoutTooltipText (tipText);
        const int w = (int) std::ceil (tl.getWidth()) + 24;
        const int h = (int) std::ceil (tl.getHeight()) + 15;
        return juce::Rectangle<int> (screenPos.x > parentArea.getCentreX() ? screenPos.x - (w + 12)
                                                                           : screenPos.x + 18,
                                     screenPos.y > parentArea.getCentreY() ? screenPos.y - (h + 8)
                                                                           : screenPos.y + 22,
                                     w, h).constrainedWithin (parentArea);
    }
    void drawTooltip (juce::Graphics& g, const juce::String& text, int width, int height) override
    {
        auto r = juce::Rectangle<float> (0, 0, (float) width, (float) height).reduced (1.0f);
        g.setColour (juce::Colours::black.withAlpha (0.32f));                  // lift off the page
        g.fillRoundedRectangle (r.translated (0.0f, 1.5f).expanded (1.0f), 9.0f);
        g.setGradientFill ({ theme::panelHi.brighter (0.07f), r.getTopLeft(),
                             theme::panelHi.darker (0.05f), r.getBottomLeft(), false });
        g.fillRoundedRectangle (r, 8.0f);
        g.setGradientFill (theme::brand (r.withHeight (1.6f), 0.6f));          // brand crown
        g.fillRoundedRectangle (r.getX() + 4.0f, r.getY() + 0.5f, r.getWidth() - 8.0f, 1.6f, 0.8f);
        g.setColour (juce::Colours::white.withAlpha (0.07f));
        g.drawRoundedRectangle (r.reduced (0.5f), 8.0f, 1.0f);
        layoutTooltipText (text).draw (g, r.reduced (11.0f, 6.5f));
    }

private:
    static juce::TextLayout layoutTooltipText (const juce::String& text)
    {
        juce::AttributedString as;
        as.append (text, theme::ui (11.5f), theme::text.withAlpha (0.95f));
        juce::TextLayout tl;
        tl.createLayout (as, 300.0f);
        return tl;
    }
};

//==============================================================================
// Transport icon button: Play/Stop, Rec, Loop, Undo/Redo — drawn, not labelled.
class IconButton : public juce::Button
{
public:
    enum class Glyph { play, rec, loop, undo, redo };
    explicit IconButton (Glyph gl, const juce::String& name) : juce::Button (name), glyph (gl) {}

    void paintButton (juce::Graphics& g, bool over, bool down) override
    {
        theme::DimScope dim (g, ! isEnabled());            // ghost of a ghost
        auto r = getLocalBounds().toFloat().reduced (1.0f);
        const bool on = getToggleState() || (glyph == Glyph::play && getButtonText() == "Stop");
        const auto hot = glyph == Glyph::rec ? theme::rec : theme::accent;
        if (on)   // lit: brand-tinted tile + glow (state deserves the light)
        {
            auto c = theme::panelHi.interpolatedWith (hot, over ? 0.26f : 0.20f);
            theme::glowRing (g, r, hot, 7.0f, 2.0f);
            g.setGradientFill ({ c.brighter (0.10f), r.getTopLeft(), c.darker (0.10f),
                                 r.getBottomLeft(), false });
            g.fillRoundedRectangle (r, 7.0f);
            g.setColour (hot.withAlpha (0.75f));
            g.drawRoundedRectangle (r.reduced (0.5f), 7.0f, 1.0f);
        }
        else      // ghost: whisper tile, border only under the hand
        {
            const float lift = down ? 0.13f : over ? 0.085f : 0.035f;
            g.setGradientFill ({ juce::Colours::white.withAlpha (lift), r.getTopLeft(),
                                 juce::Colours::white.withAlpha (lift * 0.45f), r.getBottomLeft(), false });
            g.fillRoundedRectangle (r, 7.0f);
            if (over || down)
            {
                g.setColour (juce::Colours::white.withAlpha (down ? 0.16f : 0.09f));
                g.drawRoundedRectangle (r.reduced (0.5f), 7.0f, 1.0f);
            }
        }

        auto ic = r.reduced (r.getWidth() * 0.30f, r.getHeight() * 0.30f);
        if (glyph == Glyph::play)
        {
            if (getButtonText() == "Stop")
            {
                g.setColour (theme::accent);
                g.fillRoundedRectangle (ic, 2.0f);
                g.setColour (theme::accent.withAlpha (0.35f));
                g.drawRoundedRectangle (ic.expanded (2.5f), 3.5f, 1.2f);
            }
            else
            {
                juce::Path p;
                p.addTriangle (ic.getX() + 1.0f, ic.getY(), ic.getX() + 1.0f, ic.getBottom(),
                               ic.getRight() + 1.0f, ic.getCentreY());
                g.setColour (over ? theme::text : theme::text.withAlpha (0.92f));
                g.fillPath (p);
            }
        }
        else if (glyph == Glyph::rec)
        {
            if (getToggleState())
            {   // armed: pulsing hot core + halo
                const float pulse = 0.5f + 0.5f * std::sin ((float) juce::Time::getMillisecondCounter() * 0.008f);
                g.setColour (theme::rec.withAlpha (0.25f + 0.25f * pulse));
                g.fillEllipse (ic.expanded (3.0f));
                g.setColour (theme::rec);
                g.fillEllipse (ic);
                g.setColour (juce::Colours::white.withAlpha (0.85f));
                g.fillEllipse (ic.reduced (ic.getWidth() * 0.36f));
            }
            else
            {
                g.setColour (theme::textDim);
                g.fillEllipse (ic);
            }
        }
        else if (glyph == Glyph::loop)
        {
            g.setColour (getToggleState() ? theme::accent : theme::textDim);
            juce::Path p;
            p.addCentredArc (ic.getCentreX(), ic.getCentreY(),
                             ic.getWidth() * 0.5f, ic.getHeight() * 0.5f,
                             0.0f, 0.6f, juce::MathConstants<float>::twoPi - 0.6f, true);
            g.strokePath (p, juce::PathStrokeType (1.8f));
            juce::Path arrow;
            const float ax = ic.getCentreX() + ic.getWidth() * 0.42f;
            const float ay = ic.getY() + 1.0f;
            arrow.addTriangle (ax - 3.5f, ay - 2.5f, ax - 3.5f, ay + 3.5f, ax + 2.5f, ay + 0.5f);
            g.fillPath (arrow);
        }
        else   // undo / redo: curved arrow, mirrored for redo
        {
            const bool redo = glyph == Glyph::redo;
            auto a = r.reduced (r.getWidth() * 0.26f, r.getHeight() * 0.30f);
            juce::Path p;
            const float cx = a.getCentreX(), cy = a.getCentreY() + 1.0f, rr = a.getWidth() * 0.42f;
            p.addCentredArc (cx, cy, rr, rr * 0.9f, 0.0f,
                             redo ? 0.35f : -0.35f,
                             redo ? juce::MathConstants<float>::pi * 1.05f
                                  : -juce::MathConstants<float>::pi * 1.05f, true);
            g.setColour (over ? theme::text : theme::textDim);
            g.strokePath (p, juce::PathStrokeType (1.8f, juce::PathStrokeType::curved,
                                                   juce::PathStrokeType::rounded));
            juce::Path tip;   // arrowhead at the arc's start (top)
            const float tx = cx + (redo ? rr * 0.35f : -rr * 0.35f), ty = a.getY() + 0.5f;
            tip.addTriangle (tx, ty - 3.0f, tx, ty + 3.5f, redo ? tx + 4.5f : tx - 4.5f, ty + 0.5f);
            g.fillPath (tip);
        }
    }
private:
    Glyph glyph;
};

//==============================================================================
// Segmented view switch: AGENT | ARRANGE | MIX | LIVE — one control, one mental
// model. AGENT-FIRST (F4, Chezy 2026-07-10): the chat-first page IS a mode and
// leads the row; its lit state wears the agent colour, the canvas modes keep
// brand. Pure view: reads state via getView(), reports clicks via onSelect(i).
class ViewSwitch : public juce::Component, private juce::Timer
{
public:
    std::function<int()> getView;            // 0=agent 1=arrange 2=mix 3=live
    std::function<void (int)> onSelect;
    ViewSwitch() { startTimerHz (6); }       // follow external state flips (roll open, env boot)

    static constexpr int numSegs = 4;
    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat().reduced (1.0f);
        g.setColour (theme::inset.withAlpha (0.9f));
        g.fillRoundedRectangle (r, 8.0f);
        g.setColour (juce::Colours::white.withAlpha (0.055f));
        g.drawRoundedRectangle (r.reduced (0.5f), 8.0f, 1.0f);
        const int cur = getView ? getView() : 1;
        const float segW = r.getWidth() / (float) numSegs;
        static const char* names[] = { "AGENT", "ARRANGE", "MIX", "LIVE" };
        for (int i = 0; i < numSegs; ++i)
        {
            auto seg = juce::Rectangle<float> (r.getX() + segW * (float) i, r.getY(), segW, r.getHeight());
            if (i == cur)
            {
                auto lit = seg.reduced (2.0f);
                if (i == 0)                              // the agent page wears its own colour
                {
                    g.setColour (theme::agent.withAlpha (0.28f));
                    g.fillRoundedRectangle (lit, 5.5f);
                    g.setColour (theme::agent.withAlpha (0.75f));
                    g.drawRoundedRectangle (lit.reduced (0.5f), 5.5f, 1.0f);
                    g.setColour (theme::agent.withAlpha (0.95f));
                    g.fillRoundedRectangle (lit.getX() + 4.0f, lit.getY() + 1.0f, lit.getWidth() - 8.0f, 1.8f, 0.9f);
                }
                else
                {
                    g.setGradientFill (theme::brand (lit, 0.26f));
                    g.fillRoundedRectangle (lit, 5.5f);
                    g.setColour (theme::accent.withAlpha (0.55f));
                    g.drawRoundedRectangle (lit.reduced (0.5f), 5.5f, 1.0f);
                    g.setGradientFill (theme::brand (lit.withHeight (2.0f), 0.95f));
                    g.fillRoundedRectangle (lit.getX() + 4.0f, lit.getY() + 1.0f, lit.getWidth() - 8.0f, 1.8f, 0.9f);
                }
            }
            else if (i == hover)
            {
                g.setColour ((i == 0 ? theme::agent : juce::Colours::white).withAlpha (0.07f));
                g.fillRoundedRectangle (seg.reduced (2.0f), 5.5f);
            }
            g.setColour (i == cur ? theme::text : theme::textMute.brighter (i == hover ? 0.25f : 0.0f));
            g.setFont (theme::caps (9.5f));
            g.drawText (names[i], seg.toNearestInt(), juce::Justification::centred);
        }
    }
    void mouseMove (const juce::MouseEvent& e) override
    {
        const int i = juce::jlimit (0, numSegs - 1, (int) (e.x / (getWidth() / (float) numSegs)));
        if (i != hover) { hover = i; repaint(); }
    }
    void mouseExit (const juce::MouseEvent&) override { hover = -1; repaint(); }
    void mouseDown (const juce::MouseEvent& e) override
    {
        if (onSelect) onSelect (juce::jlimit (0, numSegs - 1, (int) (e.x / (getWidth() / (float) numSegs))));
    }
private:
    void timerCallback() override                     // follow external flips — repaint on CHANGE only
    {
        const int v = getView ? getView() : 0;
        if (v != lastPainted) { lastPainted = v; repaint(); }
    }
    int hover = -1, lastPainted = -1;
};

//==============================================================================
// The LCD: bars.beats.16ths | m:ss.t — the Pro-Tools-style transport readout.
// Click it and TYPE where to go ("17", "17.3", "1:23") — the readout is a door.
class TransportLCD : public juce::Component
{
public:
    std::function<juce::String()> positionText;   // set by the host
    std::function<void (const juce::String&)> onTyped;   // host parses + seeks
    TransportLCD() { setMouseCursor (juce::MouseCursor::IBeamCursor); }   // it IS typable

    void mouseDown (const juce::MouseEvent&) override
    {
        if (onTyped == nullptr || editor != nullptr) return;
        editor = std::make_unique<juce::TextEditor>();
        editor->setFont (theme::mono (14.0f, juce::Font::bold));
        editor->setJustification (juce::Justification::centredLeft);
        editor->setTextToShowWhenEmpty ("bar.beat  or  m:ss",
                                        theme::textMute.withAlpha (0.8f));
        editor->setBounds (getLocalBounds().reduced (4, 3));
        addAndMakeVisible (*editor);
        editor->grabKeyboardFocus();
        auto commit = [this] (bool keep)
        {
            if (editor == nullptr) return;
            const auto t = editor->getText().trim();
            editor.reset();
            if (keep && t.isNotEmpty() && onTyped) onTyped (t);
            repaint();
        };
        editor->onReturnKey = [commit] { commit (true); };
        editor->onEscapeKey = [commit] { commit (false); };
        editor->onFocusLost = [commit] { commit (true); };
    }
    void paint (juce::Graphics& g) override
    {
        auto r = getLocalBounds().toFloat().reduced (1.0f);
        g.setColour (theme::inset);
        g.fillRoundedRectangle (r, 6.0f);
        g.setGradientFill ({ juce::Colours::black.withAlpha (0.4f), r.getTopLeft(),
                             juce::Colours::black.withAlpha (0.0f),
                             { r.getX(), r.getY() + 8.0f }, false });
        g.fillRoundedRectangle (r, 6.0f);                              // recessed glass
        g.setColour (theme::accent.withAlpha (0.10f));                 // phosphor wash
        g.fillRoundedRectangle (r.reduced (2.0f), 4.5f);
        g.setColour (theme::line);
        g.drawRoundedRectangle (r, 6.0f, 1.0f);
        const auto s = positionText ? positionText() : juce::String ("1.1.1 | 0:00.0");
        g.setColour (theme::accent.withAlpha (0.28f));                 // glow pass
        g.setFont (theme::mono (15.5f, juce::Font::bold));
        g.drawText (s, getLocalBounds().reduced (11, 0).translated (0, 1), juce::Justification::centredLeft);
        g.setColour (theme::accent.brighter (0.18f));
        g.drawText (s, getLocalBounds().reduced (10, 0), juce::Justification::centredLeft);
    }
private:
    std::unique_ptr<juce::TextEditor> editor;
};
