// JamStrip.h — THE BAND'S CONVERSATION AS MATERIAL (no-text-ui-state law).
// A GhostGlass strip under the Live view's pads: one BLOCK per phrase (width =
// its bars — you SEE the turn-taking shorten when you play), follow-tinted when
// the human drove that phrase's decide, amber-hatched when the REPEAT LAW saved
// a late render, a spark notch where a PUNCH entered mid-phrase, the played
// portion lit by the JamPlayer's real progress, a breathing edge while the set
// runs. Fed additively from pollJamFeed's existing parse; survives the set as
// history until the next JAM resets it.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

class JamStrip : public juce::Component
{
public:
    JamStrip() { setInterceptsMouseClicks (false, false); }

    void reset()
    {
        blocks.clear();
        followMarks.clear();
        punches.clear();
        playedBeats = 0.0;
        running = false;
        repaint();
    }

    void addBlock (int phrase, double startBeat, double bars, bool repeated)
    {
        while ((int) blocks.size() <= phrase)
            blocks.push_back ({});
        blocks[(size_t) phrase] = { startBeat, juce::jmax (0.25, bars), repeated,
                                    (size_t) phrase < followMarks.size()
                                        && followMarks[(size_t) phrase] };
        running = true;
        repaint();
    }

    void markFollow (int phrase)          // this phrase's decide HEARD the human
    {
        while ((int) followMarks.size() <= phrase)
            followMarks.push_back (false);
        followMarks[(size_t) phrase] = true;
        if (phrase >= 0 && phrase < (int) blocks.size() && blocks[(size_t) phrase].bars > 0)
        {
            blocks[(size_t) phrase].follow = true;
            repaint();
        }
    }

    void addPunch (double atBeat)
    {
        punches.push_back (atBeat);
        repaint();
    }

    // progress in PHRASE UNITS (JamPlayer::progress): cur + frac-within-phrase
    void setProgressPhrase (double units)
    {
        double b = 0.0;
        const int whole = (int) units;
        for (int i = 0; i < whole && i < (int) blocks.size(); ++i)
            b += blocks[(size_t) i].bars * 4.0;
        if (whole >= 0 && whole < (int) blocks.size())
            b += (units - whole) * blocks[(size_t) whole].bars * 4.0;
        if (std::abs (b - playedBeats) > 0.01)
        {
            playedBeats = b;
            repaint();
        }
    }

    // B6: the pane exists the MOMENT the band is called — the sound-check phase
    // reads as a warming shimmer, never dead air (no-text-ui-state law: material)
    void arm()       { running = true; repaint(); }
    void setDone()   { running = false; repaint(); }
    bool hasData() const { return ! blocks.empty() || running; }

    void tick()
    {
        if (! isVisible() || ! running) return;
        breath += 0.05f;
        if (breath > juce::MathConstants<float>::twoPi)
            breath -= juce::MathConstants<float>::twoPi;
        repaint();
    }

    // rig truth (tools/jam_strip_e2e.py)
    juce::String dump() const
    {
        int fol = 0, reps = 0;
        for (auto& b : blocks) { fol += b.follow ? 1 : 0; reps += b.repeated ? 1 : 0; }
        return "blocks=" + juce::String ((int) blocks.size())
             + " follow=" + juce::String (fol)
             + " repeats=" + juce::String (reps)
             + " punches=" + juce::String ((int) punches.size())
             + " playedBeats=" + juce::String (playedBeats, 1);
    }

    void paint (juce::Graphics& g) override
    {
        if (blocks.empty() && ! running) return;
        auto r = getLocalBounds().toFloat().reduced (1.0f);
        const float br = 0.5f + 0.5f * std::sin (breath);
        if (blocks.empty())
        {   // SOUND CHECK: the band is warming — a breathing pane + a traveling
            // ember says "coming" in material, before the first phrase exists
            g.setColour (juce::Colours::white.withAlpha (0.030f + 0.012f * br));
            g.fillRoundedRectangle (r, 7.0f);
            g.setColour (theme::accentB.withAlpha (0.20f + 0.22f * br));
            g.drawRoundedRectangle (r, 7.0f, 1.3f);
            const float sweep = std::fmod (breath * 0.35f, 1.0f);
            auto lane0 = r.reduced (6.0f, 4.0f);
            const float ex = lane0.getX() + sweep * lane0.getWidth();
            g.setGradientFill ({ theme::accentB.withAlpha (0.0f), { ex - 60.0f, lane0.getCentreY() },
                                 theme::accentB.withAlpha (0.35f), { ex, lane0.getCentreY() }, false });
            g.fillRect (juce::Rectangle<float> (ex - 60.0f, lane0.getCentreY() - 1.2f, 60.0f, 2.4f));
            return;
        }
        double total = 0.0;
        for (auto& b : blocks) total += b.bars * 4.0;
        if (total <= 0.0) return;

        // frosted pane (GhostGlass numbers)
        g.setColour (juce::Colours::white.withAlpha (running ? 0.030f + 0.012f * br : 0.026f));
        g.fillRoundedRectangle (r, 7.0f);
        g.setColour ((running ? theme::accentB : theme::textMute).withAlpha (running ? 0.22f + 0.2f * br : 0.12f));
        g.drawRoundedRectangle (r, 7.0f, running ? 1.3f : 1.0f);

        auto lane = r.reduced (5.0f, 4.0f);
        auto xOf = [&lane, total] (double beats)
        { return lane.getX() + (float) (beats / total) * lane.getWidth(); };

        for (auto& b : blocks)
        {
            if (b.bars <= 0) continue;
            const float x0 = xOf (b.startBeat), x1 = xOf (b.startBeat + b.bars * 4.0);
            juce::Rectangle<float> cell (x0 + 0.5f, lane.getY(), juce::jmax (2.0f, x1 - x0 - 1.5f),
                                         lane.getHeight());
            const auto base = b.follow ? theme::good : theme::accent;
            g.setColour (base.withAlpha (0.10f));
            g.fillRoundedRectangle (cell, 3.0f);
            // the PLAYED portion lights up (real player progress)
            const double playedIn = juce::jlimit (0.0, b.bars * 4.0, playedBeats - b.startBeat);
            if (playedIn > 0)
            {
                auto lit = cell.withWidth (juce::jmax (2.0f, (float) (playedIn / (b.bars * 4.0)) * cell.getWidth()));
                g.setColour (base.withAlpha (0.42f));
                g.fillRoundedRectangle (lit, 3.0f);
            }
            g.setColour (base.withAlpha (b.follow ? 0.6f : 0.35f));
            g.drawRoundedRectangle (cell, 3.0f, 1.0f);
            if (b.repeated)   // the REPEAT LAW saved this slot: amber hatch
            {
                g.setColour (theme::warn.withAlpha (0.65f));
                g.drawLine (cell.getX() + 2, cell.getBottom() - 2, cell.getRight() - 2, cell.getY() + 2, 1.2f);
                g.drawLine (cell.getX() + 2, cell.getY() + 2, cell.getRight() - 2, cell.getBottom() - 2, 1.2f);
            }
        }
        for (double pb : punches)   // a punch ENTERED here: the agent's spark
        {
            const float px = xOf (pb);
            theme::spark (g, { px - 4.0f, lane.getY() - 1.0f, 8.0f, 8.0f },
                          theme::accentB.withAlpha (0.9f));
        }
        if (playedBeats > 0 && playedBeats < total)   // the set's cursor
        {
            const float px = xOf (playedBeats);
            g.setColour (theme::text.withAlpha (0.7f));
            g.drawVerticalLine ((int) px, lane.getY(), lane.getBottom());
        }
    }

private:
    struct Block { double startBeat = 0, bars = 0; bool repeated = false, follow = false; };
    std::vector<Block> blocks;
    std::vector<bool> followMarks;
    std::vector<double> punches;
    double playedBeats = 0.0;
    bool running = false;
    float breath = 0.0f;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (JamStrip)
};
