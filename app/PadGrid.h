// PadGrid — MPC-style scene pads, visible (#38): big launchable pads over the
// Live view. Click = launch that scene column (exclusive); the active pad
// glows with the brand gradient; MIDI hands hit the same scenes.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

namespace sotadaw
{

class PadGrid : public juce::Component, private juce::Timer
{
public:
    std::function<int()> getNumScenes;                 // from the song
    std::function<juce::String (int)> getSceneName;
    std::function<int()> getActiveScene;               // liveGrid.lastScene
    std::function<void (int)> onPad;                   // -> liveGrid.launchScene

    PadGrid() { startTimerHz (8); }

    static constexpr int maxPads = 8;              // one hardware row = keys 1..8
    int page = 0;                                  // scenes past 8 live one wheel away
    int pages() const
    {
        const int n = getNumScenes ? juce::jmax (0, getNumScenes()) : 0;
        return juce::jmax (1, (n + maxPads - 1) / maxPads);
    }
    int curPage() const { return juce::jlimit (0, pages() - 1, page); }
    int padAt (juce::Point<int> pt) const          // ABSOLUTE scene under the hand
    {
        const int n = getNumScenes ? juce::jmax (1, getNumScenes()) : 1;
        const int onPage = juce::jlimit (1, maxPads, n - curPage() * maxPads);
        const int w = getWidth() / juce::jmax (1, onPage);
        const int i = w > 0 ? curPage() * maxPads + pt.x / w : -1;
        return (i >= curPage() * maxPads && i < juce::jmin (n, (curPage() + 1) * maxPads)) ? i : -1;
    }
    juce::Rectangle<int> pageRect() const { return { getWidth() - 40, 2, 36, 14 }; }
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails& w) override
    {
        if (pages() <= 1) return;
        const int np = juce::jlimit (0, pages() - 1, curPage() + (w.deltaY < 0 ? 1 : -1));
        if (np != curPage()) { page = np; repaint(); }
    }

    static juce::Colour padColour (int i)              // mirrors LiveGrid::sceneColour
    {
        return theme::trackColour (i + 3).withRotatedHue (0.02f);
    }

    void paint (juce::Graphics& g) override
    {
        const int n = getNumScenes ? juce::jmax (0, getNumScenes()) : 0;
        if (n == 0)
        {
            g.setColour (juce::Colours::white.withAlpha (0.30f));
            g.setFont (juce::Font (juce::FontOptions (11.0f)));
            g.drawText ("no scenes yet — MAKE a track, import a song, or build a loop machine",
                        getLocalBounds(), juce::Justification::centred);
            return;
        }
        const int active = getActiveScene ? getActiveScene() : -1;
        const int iEnd = juce::jmin (n, (curPage() + 1) * maxPads);
        for (int i = curPage() * maxPads; i < iEnd; ++i)
        {
            auto r = padRect (i).toFloat().reduced (3.0f);
            const bool on = i == active;
            const bool hot = i == hover;
            const auto sc = padColour (i);
            if (on)
            {
                // the lit pad: brand gradient + breathing glow ring — THE performance surface
                const float pulse = 0.5f + 0.5f * std::sin ((float) juce::Time::getMillisecondCounter() * 0.005f);
                g.setColour (theme::accentB.withAlpha (0.18f + 0.12f * pulse));
                g.fillRoundedRectangle (r.expanded (3.0f), 11.0f);
                juce::ColourGradient grad (juce::Colour (0xff2437c8), r.getTopLeft(),
                                           juce::Colour (0xff8a4dff), r.getBottomRight(), false);
                g.setGradientFill (grad);
                g.fillRoundedRectangle (r, 9.0f);
                g.setColour (juce::Colours::white.withAlpha (0.25f));
                g.drawHorizontalLine ((int) r.getY() + 1, r.getX() + 8.0f, r.getRight() - 8.0f);
                g.setColour (juce::Colour (0xff8a4dff).withAlpha (0.55f + 0.3f * pulse));
                g.drawRoundedRectangle (r.expanded (1.5f), 10.0f, 2.0f);
            }
            else
            {
                g.setGradientFill ({ theme::panelHi.brighter (hot ? 0.10f : 0.02f), r.getTopLeft(),
                                     theme::panel.darker (hot ? 0.0f : 0.08f), r.getBottomLeft(), false });
                g.fillRoundedRectangle (r, 9.0f);
                g.setColour (sc.withAlpha (hot ? 0.95f : 0.65f));         // scene identity top edge
                g.fillRoundedRectangle (r.getX() + 7.0f, r.getY() + 2.0f, r.getWidth() - 14.0f, 2.5f, 1.25f);
                g.setColour (hot ? sc.withAlpha (0.55f) : juce::Colours::white.withAlpha (0.09f));
                g.drawRoundedRectangle (r, 9.0f, 1.2f);
            }
            g.setColour (on ? juce::Colours::white : juce::Colours::white.withAlpha (hot ? 0.9f : 0.72f));
            g.setFont (juce::Font (juce::FontOptions (12.5f, on || hot ? juce::Font::bold : juce::Font::plain)));
            auto name = getSceneName ? getSceneName (i) : juce::String (i + 1);
            g.drawFittedText (name, r.reduced (8.0f).toNearestInt(), juce::Justification::centred, 2);
            {   // number badge, top-left — pads answer keys 1..8
                juce::Rectangle<float> badge (r.getX() + 5.0f, r.getY() + 5.0f, 15.0f, 13.0f);
                g.setColour (on ? juce::Colours::black.withAlpha (0.25f) : sc.withAlpha (0.16f));
                g.fillRoundedRectangle (badge, 4.0f);
                g.setColour (on ? juce::Colours::white : sc.brighter (0.2f));
                g.setFont (theme::mono (8.5f, juce::Font::bold));
                g.drawText (juce::String (i + 1), badge.toNearestInt(), juce::Justification::centred);
            }
        }
        if (pages() > 1)
        {   // the page jewel: click cycles, wheel rides, MIDI hands auto-follow
            auto pr = pageRect();
            g.setColour (theme::panel.withAlpha (0.85f));
            g.fillRoundedRectangle (pr.toFloat(), 4.0f);
            g.setColour (juce::Colours::white.withAlpha (0.75f));
            g.setFont (theme::mono (8.5f, juce::Font::bold));
            g.drawText (juce::String (curPage() + 1) + "/" + juce::String (pages()),
                        pr, juce::Justification::centred);
        }
    }

    void mouseMove (const juce::MouseEvent& e) override
    {
        const int i = padAt (e.getPosition());
        if (i != hover) { hover = i; repaint(); }
    }
    void mouseExit (const juce::MouseEvent&) override { hover = -1; repaint(); }
    void mouseDown (const juce::MouseEvent& e) override
    {
        if (pages() > 1 && pageRect().contains (e.getPosition()))
        { page = (curPage() + 1) % pages(); repaint(); return; }
        const int i = padAt (e.getPosition());
        if (i >= 0 && onPad && getNumScenes && i < getNumScenes())
            onPad (i);
    }

private:
    int hover = -1;

    juce::Rectangle<int> padRect (int i) const     // i ABSOLUTE; laid out on its page
    {
        const int n = getNumScenes ? juce::jmax (1, getNumScenes()) : 1;
        const int onPage = juce::jlimit (1, maxPads, n - curPage() * maxPads);
        const int w = getWidth() / juce::jmax (1, onPage);
        return { (i - curPage() * maxPads) * w, 0, w, getHeight() };
    }
    void timerCallback() override                      // follow MIDI-hand launches
    {
        const int a = getActiveScene ? getActiveScene() : -1;
        const int n = getNumScenes ? getNumScenes() : 0;
        if (a != lastActive || n != lastCount)         // scene state moved: redraw the strip
        {
            if (a >= 0 && a != lastActive && pages() > 1)
                page = a / maxPads;                    // MIDI hands pull their page into view
            lastActive = a; lastCount = n;
            repaint();
            return;
        }
        if (a >= 0 && n > 0 && a / maxPads == curPage())   // only the lit pad breathes
            repaint (padRect (a).expanded (4));
    }
    int lastActive = -2, lastCount = -1;
};

} // namespace sotadaw
