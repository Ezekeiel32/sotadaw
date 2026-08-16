// THE SCORE TAB (2026-08-02) — the DAW's notation face. Every MIDI track in the
// song engraved as real sheet music (drums auto-detected onto a Weinberg kit
// staff, melodic tracks auto-cleffed), EDITABLE (drag = diatonic transpose,
// alt = chromatic, dbl-click = insert, right-click = delete, marquee + keys),
// and wired into the agent rails: score selection mirrors the lane-selection
// context, COMPOSE ships a prompt through the normal ask door, proposals paint
// as violet ghost notation with red strikes for removals (read-only while a
// take is on the stand — the deck stays the verdict door).
//
// Engraving truth lives in ScoreEngrave.h; this file is geometry + Bravura
// paint + hands. SMuFL glyphs via the embedded Bravura face (fallback shapes
// keep the page alive if the font is ever absent).
#pragma once
#include "UiTheme.h"
#include "ScoreEngrave.h"
#include "ScorePdf.h"
#include <functional>

namespace sotadaw
{

//============================================================== SMuFL glyphs
namespace smufl
{
    enum : juce::juce_wchar
    {
        gClef = 0xE050, fClef = 0xE062, percClef = 0xE069,
        timeSig0 = 0xE080,                       // ..+9 digits
        headWhole = 0xE0A2, headHalf = 0xE0A3, headBlack = 0xE0A4,
        headXBlack = 0xE0A9, headCircleX = 0xE0B3,
        flag8Up = 0xE240, flag8Down = 0xE241, flag16Up = 0xE242, flag16Down = 0xE243,
        flag32Up = 0xE244, flag32Down = 0xE245,
        accFlat = 0xE260, accNatural = 0xE261, accSharp = 0xE262,
        accDblSharp = 0xE263, accDblFlat = 0xE264,
        restWhole = 0xE4E3, restHalf = 0xE4E4, restQuarter = 0xE4E5,
        rest8 = 0xE4E6, rest16 = 0xE4E7, rest32 = 0xE4E8,
        augDot = 0xE1E7, tuplet3 = 0xE883, metQuarterUp = 0xECA5,
        commonTime = 0xE08A,
        dynP = 0xE520, dynF = 0xE522, dynPP = 0xE52B, dynMP = 0xE52C,
        dynMF = 0xE52D, dynFF = 0xE52F,
        accentAbove = 0xE4A0, accentBelow = 0xE4A1,
        metWhole = 0xECA2, metHalf = 0xECA3, met8 = 0xECA7, met16 = 0xECA9, met32 = 0xECAB
    };
}

class ScorePage : public juce::Component,
                  private juce::Timer,
                  private juce::ScrollBar::Listener
{
public:
    //-------------------------------------------------- host hooks (MainComponent)
    std::function<void()> onSnapshot;                       // BEFORE a gesture's first mutation
    std::function<void()> onChanged;                        // after mutation (save + engineDirty)
    std::function<void (int, int, float)> onAudition;       // trackIdx, midi pitch, vel
    std::function<void()> onAuditionOff;
    std::function<void (const std::map<int, std::set<size_t>>&)> onSelectionMirror;
    std::function<void (const juce::String&)> onCompose;    // ships the ask through the prompt rail
    std::function<void (const juce::String&)> onExport;     // "midi" | "xml"
    std::function<juce::Colour (int)> trackColourOf;
    std::function<double()> getPlayheadBeats;
    std::function<bool()> getIsPlaying;
    std::function<juce::String()> getSongName;
    std::function<void (double)> onSeek;                    // click-to-seek (beats)
    std::function<std::pair<double, double>()> getLoop;     // arrange loop region (a, b)
    std::function<void (int, bool)> onSetMute;              // staff M dot -> track mute
    std::function<void (int, bool)> onSetSolo;              // staff S dot -> track solo
    std::function<bool (int)> isMuted, isSoloed;

    Song* song = nullptr;                                   // the base (edited in place)

    ScorePage()
    {
        setWantsKeyboardFocus (true);
        setOpaque (true);
        addAndMakeVisible (vScroll);
        vScroll.setAutoHide (false);
        vScroll.addListener (this);
        auto initBox = [this] (juce::TextEditor& e, const char* hint)
        {
            e.setFont (theme::ui (12.0f));
            e.setTextToShowWhenEmpty (hint, theme::textMute);
            e.setSelectAllWhenFocused (true);
            addAndMakeVisible (e);
        };
        initBox (vibeBox, "vibe: cinematic bloom...");
        initBox (instBox, "instruments: banjo lead...");
        composeButton.setButtonText ("COMPOSE");
        composeButton.setComponentID ("primary");
        composeButton.setTooltip ("produce the song FROM these notes: the agent keeps them as written and builds around them");
        composeButton.onClick = [this] { compose(); };
        addAndMakeVisible (composeButton);
        midiButton.setButtonText ("MIDI");
        midiButton.setTooltip ("download the score as a Standard MIDI File");
        midiButton.onClick = [this] { if (onExport) onExport ("midi"); };
        addAndMakeVisible (midiButton);
        xmlButton.setButtonText ("XML");
        xmlButton.setTooltip ("download the score as MusicXML (opens in any notation app)");
        xmlButton.onClick = [this] { if (onExport) onExport ("xml"); };
        addAndMakeVisible (xmlButton);
        pdfButton.setButtonText ("PDF");
        pdfButton.setTooltip ("print the engraved score to a PDF (A4 pages)");
        pdfButton.onClick = [this] { if (onExport) onExport ("pdf"); };
        addAndMakeVisible (pdfButton);
        loadPrefs();
        startTimerHz (20);
    }

    //-------------------------------------------------- lifecycle from the host
    void songChanged()                                      // model went stale (load/edit/accept)
    {
        if (! ghosting) { selection.clear(); mirrorSelection(); }
        dirty = true;
        repaint();
    }
    // proposal ghosts: adds keyed per track, removals as raw notes; prop = the take
    void setGhosts (const Song* prop,
                    std::map<int, std::set<juce::String>> addedKeys,
                    std::map<int, std::vector<SongNote>> removedNotes)
    {
        ghostProp = prop;
        ghostAdds = std::move (addedKeys);
        ghostRemoves = std::move (removedNotes);
        const bool g = ghostProp != nullptr;
        if (g != ghosting)
        { ghosting = g; if (g) { selection.clear(); mirrorSelection(); stepMode = false; } }
        dirty = true;
        repaint();
    }
    bool isGhosting() const { return ghosting; }

    //-------------------------------------------------- component
    void resized() override
    {
        auto r = getLocalBounds();
        auto bar = r.removeFromTop (34);
        bar.removeFromLeft (8);
        // right cluster: vibe | inst | compose | midi xml pdf — the CHIP ROW gets
        // first claim on width (the theme door must never fall off the bar)
        auto right = bar.removeFromRight (juce::jmin (600, juce::jmax (210, getWidth() - 660)));
        pdfButton.setBounds (right.removeFromRight (42).reduced (2, 5));
        xmlButton.setBounds (right.removeFromRight (44).reduced (2, 5));
        midiButton.setBounds (right.removeFromRight (48).reduced (2, 5));
        composeButton.setBounds (right.removeFromRight (92).reduced (2, 4));
        instBox.setBounds (right.removeFromRight (juce::jmax (90, right.getWidth() / 2)).reduced (3, 6));
        vibeBox.setBounds (right.reduced (3, 6));
        toolbarArea = bar;                                   // custom chips paint here
        vScroll.setBounds (getLocalBounds().removeFromRight (10)
                               .withTrimmedTop (34).withTrimmedBottom (22));
        dirty = true;
    }

    void parentSizeChanged() override { dirty = true; }
    void visibilityChanged() override { if (isVisible()) { dirty = true; grabKeyboardFocus(); } }

    void paint (juce::Graphics& g) override
    {
        rebuildIfNeeded();
        paintPh = getPlayheadBeats ? getPlayheadBeats() : -1.0;
        paintPlaying = getIsPlaying && getIsPlaying();
        auto r = getLocalBounds();
        g.setGradientFill ({ theme::bgHi, r.toFloat().getTopLeft(), theme::bg,
                             { (float) r.getX(), (float) r.getBottom() * 0.7f }, false });
        g.fillAll();
        paintToolbar (g);
        g.saveState();
        g.reduceClipRegion (r.withTrimmedTop (34).withTrimmedBottom (22));
        g.addTransform (juce::AffineTransform::translation (0.0f, (float) -viewY));
        if (song == nullptr || model.staves.empty())
            paintEmpty (g);
        else
        {
            paintPaper (g);
            paintTitle (g, 64.0f);
            for (int sy = 0; sy < (int) systems.size(); ++sy)
            {
                auto& sys = systems[(size_t) sy];
                const float top = (float) (sys.y0 - viewY);
                if (top > (float) getHeight() + 60.0f || top + sys.h < -60.0f) continue;
                paintSystemBlock (g, sy);
            }
            paintHoverPreview (g);
            paintStepCaret (g);
        }
        g.restoreState();
        paintReadout (g);
        if (gesture.marquee)
        {
            auto mr = juce::Rectangle<float> (gesture.origin, gesture.current);
            g.setColour (theme::accent.withAlpha (0.10f)); g.fillRect (mr);
            g.setColour (theme::accent.withAlpha (0.6f));  g.drawRect (mr, 1.0f);
        }
        paintPill (g);
        paintHoverBubble (g);
        paintHelp (g);
    }

    //-------------------------------------------------- interaction
    void mouseDown (const juce::MouseEvent& e) override
    {
        grabKeyboardFocus();
        if (showHelp) { showHelp = false; repaint(); return; }
        if (e.y < 34) { toolbarClick (e); return; }
        if (e.y >= getHeight() - 22) return;                 // the readout strip
        for (auto& pc : pillChips)                           // AI verbs live ON the selection
            if (pc.r.contains (e.position))
            { if (onCompose) onCompose (pc.prompt); return; }
        const auto scPos = e.position.translated (0, (float) viewY);
        for (auto& lh : labelHits)                           // staff identity rail
        {
            if (lh.mDot.expanded (2.0f).contains (scPos)) { toggleStaffFlag (lh.staff, true);  return; }
            if (lh.sDot.expanded (2.0f).contains (scPos)) { toggleStaffFlag (lh.staff, false); return; }
            if (lh.r.contains (scPos))
            {
                if (e.getNumberOfClicks() >= 2) toggleFocus (lh.staff);
                else if (! ghosting)            selectStaffNotes (lh.staff);
                return;
            }
        }
        if (ghosting)                                        // read-only stand - but a click SEEKS
        {
            gesture = Gesture();
            gesture.marquee = true;
            gesture.origin = e.position;
            gesture.current = e.position;
            return;
        }
        const auto* hit = hitAt (scPos);
        if (e.mods.isPopupMenu())
        {
            if (hit != nullptr) deleteNote (hit->src);
            return;
        }
        gesture = Gesture();
        if (hit != nullptr)
        {
            if (auto* n = noteFor (hit->src))                // a touched note SOUNDS
                auditionBlip (hit->src.track, n->pitch, (float) n->vel);
            if (! trackIsDrum (hit->src.track)) stepTrackIdx = hit->src.track;
            if (e.mods.isCommandDown())
            {
                if (! selection.erase (key (hit->src))) selection[key (hit->src)] = hit->src;
                mirrorSelection(); repaint();
                return;
            }
            if (! selection.count (key (hit->src)))
            {
                selection.clear();
                selection[key (hit->src)] = hit->src;
                mirrorSelection();
            }
            gesture.active = true;
            gesture.src = hit->src;
            gesture.lastStepDelta = 0; gesture.lastSemiDelta = 0; gesture.lastBeatDelta = 0;
            gesture.origin = e.position;
            gesture.onRightEdge = ! trackIsDrum (hit->src.track)
                                  && e.position.x > hit->r.getRight() - hit->r.getWidth() * 0.35f;
            for (auto& [k2, sr] : selection)
            {
                juce::ignoreUnused (k2);
                if (auto* n = noteFor (sr))
                    gesture.orig.push_back ({ sr, n->start, n->len, n->pitch });
            }
            repaint();
            return;
        }
        if (e.mods.isAltDown() || e.getNumberOfClicks() >= 2) { insertAt (scPos); return; }
        gesture.marquee = true;
        gesture.origin = e.position;
        gesture.current = e.position;
        if (! e.mods.isCommandDown()) { selection.clear(); mirrorSelection(); }
        repaint();
    }

    void mouseDrag (const juce::MouseEvent& e) override
    {
        if (ghosting) return;
        if (gesture.marquee) { gesture.current = e.position; updateMarquee(); repaint(); return; }
        if (! gesture.active) return;
        if (! gesture.begun && e.getDistanceFromDragStart() > 3)
        { gesture.begun = true; if (onSnapshot) onSnapshot(); }
        if (! gesture.begun) return;
        const float dy = e.position.y - gesture.origin.y;
        const float dx = e.position.x - gesture.origin.x;
        if (gesture.onRightEdge)
        {   // length: horizontal only, by display grid
            const double grid = insertGrid();
            const double db = std::round ((double) dx / pxPerBeatAt (gesture.src) / grid) * grid;
            if (std::abs (db - gesture.lastBeatDelta) < 1e-9) return;
            gesture.lastBeatDelta = db;
            for (auto& o : gesture.orig)
                if (auto* n = noteFor (o.src))
                    n->len = juce::jmax (grid, o.len + db);
            noteEdited (false);
            return;
        }
        const int stepDelta = -(int) std::round (dy / (staffSpace * 0.5f));
        const double grid = insertGrid();
        const double beatDelta = std::round ((double) dx / pxPerBeatAt (gesture.src) / grid) * grid;
        const bool chromatic = e.mods.isAltDown();
        bool moved = false;
        if (chromatic ? stepDelta != gesture.lastSemiDelta : stepDelta != gesture.lastStepDelta)
        {
            for (auto& o : gesture.orig)
                if (auto* n = noteFor (o.src))
                {
                    if (trackIsDrum (o.src.track)) continue;      // kit rows are role-fixed
                    n->pitch = chromatic ? juce::jlimit (0, 127, o.pitch + stepDelta)
                                         : pitchAtStepDelta (o.pitch, stepDelta);
                }
            (chromatic ? gesture.lastSemiDelta : gesture.lastStepDelta) = stepDelta;
            moved = true;
            if (auto* n = noteFor (gesture.src))
                { auditionBlip (gesture.src.track, n->pitch, (float) n->vel); }
        }
        if (std::abs (beatDelta - gesture.lastBeatDelta) > 1e-9)
        {
            for (auto& o : gesture.orig)
                if (auto* n = noteFor (o.src))
                    n->start = juce::jmax (0.0, o.start + beatDelta);
            gesture.lastBeatDelta = beatDelta;
            moved = true;
        }
        if (moved) noteEdited (false);
    }

    void mouseUp (const juce::MouseEvent& e) override
    {
        if (audOn) { audOn = false; if (onAuditionOff) onAuditionOff(); }
        if (gesture.marquee)
        {
            const bool wasClick = e.getDistanceFromDragStart() < 4;
            gesture = Gesture();
            if (wasClick)                                    // a click on open paper = SEEK
            {
                const auto ip = resolveInsert (e.position.translated (0, (float) viewY));
                if (ip.valid && onSeek)
                    onSeek (juce::jmax (0.0, std::round (ip.rawBeat * 4.0) / 4.0));
            }
            repaint();
            return;
        }
        if (gesture.active && gesture.begun) noteEdited (true);
        gesture = Gesture();
    }

    void mouseMove (const juce::MouseEvent& e) override
    {
        hoverScreen = e.position;
        const bool inScore = e.y >= 34 && e.y < getHeight() - 22;
        const auto* h = inScore ? hitAt (e.position.translated (0, (float) viewY)) : nullptr;
        const auto nh = h != nullptr ? key (h->src) : juce::String();
        InsPoint ip;
        if (inScore && h == nullptr && ! ghosting && ! stepMode && ! showHelp)
            ip = resolveInsert (e.position.translated (0, (float) viewY));
        const bool changed = nh != hoverKey || ip.valid != hoverIns.valid
            || (ip.valid && (ip.step != hoverIns.step
                             || std::abs (ip.beat - hoverIns.beat) > 1e-9
                             || ip.staff != hoverIns.staff));
        hoverSrc = h != nullptr ? h->src : score::SrcRef();
        hoverKey = nh;
        hoverIns = ip;
        if (changed || ip.valid) repaint();
    }
    void mouseExit (const juce::MouseEvent&) override
    {
        if (hoverKey.isNotEmpty() || hoverIns.valid)
        { hoverKey.clear(); hoverIns = InsPoint(); repaint(); }
    }

    void mouseWheelMove (const juce::MouseEvent& e, const juce::MouseWheelDetails& w) override
    {
        if (e.mods.isCommandDown())
        {   // THE WHEEL LAW: ctrl = zoom (engraving scale), anchored at the cursor
            setScaleAnchored (staffSpace * (w.deltaY > 0 ? 1.12f : 0.89f), (float) e.y);
            return;
        }
        followPauseUntil = juce::Time::getMillisecondCounter() + 1800;
        viewY = juce::jlimit (0.0, juce::jmax (0.0, totalH - 34.0 - (double) viewH()),
                              viewY - w.deltaY * 120.0);
        vScroll.setCurrentRange (viewY, viewH(), juce::dontSendNotification);
        repaint();
    }

    bool keyPressed (const juce::KeyPress& k) override
    {
        const auto ch = k.getTextCharacter();
        if (ch == '?') { showHelp = ! showHelp; repaint(); return true; }
        if (showHelp) { showHelp = false; repaint(); return true; }
        if (k == juce::KeyPress::escapeKey)
        {
            if (stepMode) { stepMode = false; repaint(); return true; }
            if (! selection.empty()) { selection.clear(); mirrorSelection(); repaint(); return true; }
            if (focusStaff != -2) { focusStaff = -2; scopeTrack = -1; dirty = true; repaint(); return true; }
            return false;
        }
        if (ghosting) return false;
        const auto mods = k.getModifiers();

        // ---- step entry (N toggles; letters land notes at the caret)
        if ((ch == 'n' || ch == 'N') && ! mods.isCommandDown()) { toggleStepMode(); return true; }
        if (stepMode)
        {
            if (ch >= 'a' && ch <= 'g') { stepInsertLetter ((int) (ch - 'a')); return true; }
            if (ch >= 'A' && ch <= 'G') { stepInsertLetter ((int) (ch - 'A')); return true; }
            if (ch == 'r' || ch == 'R')
            { stepCaret += insertGrid(); scrollToBeat (stepCaret); repaint(); return true; }
            if (k == juce::KeyPress::backspaceKey)
            {
                stepCaret = juce::jmax (0.0, stepCaret - insertGrid());
                scrollToBeat (stepCaret); repaint(); return true;
            }
        }
        // ---- palette from the keyboard: 1..6 = whole..32nd, . dot, t triplet
        if (! mods.isCommandDown() && ch >= '1' && ch <= '6')
        {
            static const int dens[6] = { 1, 2, 4, 8, 16, 32 };
            insertDenom = dens[ch - '1'];
            repaint(); return true;
        }
        if (ch == '.') { insertDot = ! insertDot; repaint(); return true; }
        if (ch == 't' || ch == 'T') { insertTrip = ! insertTrip; repaint(); return true; }

        // ---- clipboard verbs
        if (mods.isCommandDown())
        {
            if (k.isKeyCode ('A')) { selectAll(); return true; }
            if (k.isKeyCode ('C')) { copySelection(); return true; }
            if (k.isKeyCode ('X')) { copySelection(); deleteSelection(); return true; }
            if (k.isKeyCode ('V')) { pasteClipboard(); return true; }
            if (k.isKeyCode ('D')) { duplicateSelection(); return true; }
        }
        if ((k == juce::KeyPress::deleteKey || k == juce::KeyPress::backspaceKey) && ! selection.empty())
        { deleteSelection(); return true; }

        // ---- the arrow matrix: step / Alt semitone / Ctrl octave / Shift velocity;
        //      Left-Right nudge by grid, Alt = length
        const bool up = k.getKeyCode() == juce::KeyPress::upKey,
                   dn = k.getKeyCode() == juce::KeyPress::downKey,
                   lf = k.getKeyCode() == juce::KeyPress::leftKey,
                   rt = k.getKeyCode() == juce::KeyPress::rightKey;
        if ((up || dn || lf || rt) && ! selection.empty())
        {
            if (onSnapshot) onSnapshot();
            const double grid = insertGrid();
            int blipPitch = -1, blipTrack = -1; float blipVel = 0.8f;
            for (auto& [k2, sr] : selection)
            {
                juce::ignoreUnused (k2);
                auto* n = noteFor (sr);
                if (n == nullptr) continue;
                if (up || dn)
                {
                    const int d = up ? 1 : -1;
                    if (mods.isShiftDown())
                        n->vel = juce::jlimit (0.05, 1.0, n->vel + 0.06 * d);
                    else if (trackIsDrum (sr.track))
                        continue;
                    else if (mods.isCommandDown())
                        n->pitch = juce::jlimit (0, 127, n->pitch + 12 * d);
                    else if (mods.isAltDown())
                        n->pitch = juce::jlimit (0, 127, n->pitch + d);
                    else
                        n->pitch = pitchAtStepDelta (n->pitch, d);
                    blipPitch = n->pitch; blipTrack = sr.track; blipVel = (float) n->vel;
                }
                else if (mods.isAltDown())
                    n->len = juce::jmax (grid, n->len + (rt ? grid : -grid));
                else
                    n->start = juce::jmax (0.0, n->start + (rt ? grid : -grid));
            }
            if (blipPitch >= 0 && blipTrack >= 0)
            {
                auditionBlip (blipTrack, blipPitch, blipVel);
                juce::Timer::callAfterDelay (180, [this]
                { if (audOn) { audOn = false; if (onAuditionOff) onAuditionOff(); } });
            }
            noteEdited (true);
            return true;
        }
        return false;
    }

private:
    //-------------------------------------------------- glyph plumbing
    static juce::Typeface::Ptr bravura()
    {
#if SOTADAW_EMBEDDED_FONTS
        static const auto tf = juce::Typeface::createSystemTypefaceFor (
            BinaryData::Bravura_otf, (size_t) BinaryData::Bravura_otfSize);
        return tf;
#else
        return nullptr;
#endif
    }
    mutable juce::Font musicFontCache { juce::FontOptions{} };
    mutable float musicFontSp = -1.0f;
    juce::Font musicFont (float staffSpacePx) const
    {
        if (std::abs (musicFontSp - staffSpacePx) > 0.001f)
        {
            musicFontSp = staffSpacePx;
            if (auto tf = bravura())
                musicFontCache = juce::Font (juce::FontOptions (tf)).withPointHeight (staffSpacePx * 4.0f);
            else
                musicFontCache = theme::ui (staffSpacePx * 3.0f);
        }
        return musicFontCache;
    }
    static juce::String gl (juce::juce_wchar c) { return juce::String::charToString (c); }
    static float textW (const juce::Font& f, const juce::String& t)
    {
        juce::GlyphArrangement ga;
        ga.addLineOfText (f, t, 0, 0);
        return ga.getBoundingBox (0, -1, true).getWidth();
    }
    void drawGlyph (juce::Graphics& g, juce::juce_wchar c, float x, float baselineY, float sp) const
    {
        juce::GlyphArrangement ga;
        ga.addLineOfText (musicFont (sp), gl (c), x, baselineY);
        ga.draw (g);
    }
    float glyphWidth (juce::juce_wchar c, float sp) const
    {
        juce::GlyphArrangement ga;
        ga.addLineOfText (musicFont (sp), gl (c), 0, 0);
        return ga.getBoundingBox (0, -1, true).getWidth();
    }

    //-------------------------------------------------- geometry
    struct MeasGeo
    {
        int sys = 0;
        float x0 = 0, w = 0;                     // absolute x span (content, after left pad)
        std::vector<double> colBeats;            // score-wide union, measure-local
        std::vector<float> colX;                 // absolute x per column
        float endX = 0;
    };
    struct SysGeo
    {
        int m0 = 0, count = 0;
        float y0 = 0, h = 0;
        std::vector<float> staffTop;             // top staff line y per staff (absolute, unscrolled)
    };
    struct Hit
    {
        juce::Rectangle<float> r;                // unscrolled space
        score::SrcRef src;
        int staff = 0, meas = 0, voice = 0, elem = 0, head = 0;
    };

    score::Model model;
    std::vector<MeasGeo> measGeo;
    std::vector<SysGeo> systems;
    std::vector<Hit> hits;
    struct TiePair { int staff, vFrom, mFrom, eFrom, mTo, eTo; };
    std::vector<TiePair> ties;
    double totalH = 0;
    bool dirty = true;

    float staffSpace = 5.0f;                     // S — the engraving scale
    double viewY = 0;
    double quant = 0;                            // 0 = AUTO
    bool mergeDrums = true;
    int insertDenom = 8; bool insertDot = false, insertTrip = false;

    bool ghosting = false;
    const Song* ghostProp = nullptr;
    std::map<int, std::set<juce::String>> ghostAdds;
    std::map<int, std::vector<SongNote>> ghostRemoves;

    std::map<juce::String, score::SrcRef> selection;
    juce::String hoverKey;
    bool audOn = false;

    struct Gesture
    {
        bool active = false, begun = false, marquee = false, onRightEdge = false;
        score::SrcRef src;
        juce::Point<float> origin, current;
        int lastStepDelta = 0, lastSemiDelta = 0;
        double lastBeatDelta = 0;
        struct Orig { score::SrcRef src; double start, len; int pitch; };
        std::vector<Orig> orig;
    };
    Gesture gesture;

    juce::TextEditor vibeBox, instBox;
    juce::TextButton composeButton, midiButton, xmlButton, pdfButton;
    juce::Rectangle<int> toolbarArea;
    struct Chip { juce::Rectangle<float> r; juce::String label; int id = 0; bool on = false; juce::String tip; };
    std::vector<Chip> chips;
    int scopeTrack = -1;                          // -1 = whole song

    juce::ScrollBar vScroll { true };

    //-------------------------------------------------- SCORE II state
    bool paperMode = true;                        // THE PAPER: ivory page on the desk
    bool printing = false;                        // exportPdf render pass
    int printW = 0;                               // layout width override while printing
    float pageL = 0, pageWv = 0;                  // page x geometry (layout output)
    float sysL = 58.0f;                           // left edge of staff lines (layout output)
    double paintPh = -1;  bool paintPlaying = false;   // captured once per paint
    score::SrcRef hoverSrc;                       // hovered note (parsed twin of hoverKey)
    juce::Point<float> hoverScreen;               // for the pitch bubble
    struct InsPoint
    {
        bool valid = false;
        int sys = -1, staff = -1, mi = -1;
        double beat = 0, rawBeat = 0;             // global beats (snapped / raw)
        int step = 0, track = -1, pitch = 60;
        juce::String label;
    };
    InsPoint hoverIns;
    juce::uint32 followPauseUntil = 0;            // user scroll outranks follow
    bool showHelp = false;
    int focusStaff = -2;                          // -2 none, -1 kit staff, >=0 track idx
    struct LabelHit
    {
        juce::Rectangle<float> r, mDot, sDot;
        int staff = 0, sys = 0;
    };
    std::vector<LabelHit> labelHits;
    struct PillChip { juce::Rectangle<float> r; juce::String label, prompt; };
    std::vector<PillChip> pillChips;              // screen space, rebuilt each paint
    bool stepMode = false;
    double stepCaret = 0;
    int stepTrackIdx = -1, lastStepPitch = -1;
    struct ClipNote { int track; double d, len, vel; int pitch; };
    std::vector<ClipNote> clipNotes;
    double clipSpan = 0, clipAnchor = 0;

    //-------------------------------------------------- palette (paper / ink)
    struct Pal
    {
        juce::Colour paper, paperLine, ink, inkSoft, faint, label, accent, ghost,
                     strike, gold, sel;
    };
    const Pal& pal() const
    {
        static const Pal paperP = [
        ] {
            Pal p;
            p.paper     = juce::Colour (0xfff6f1e6);
            p.paperLine = juce::Colour (0xffe3dac2);
            p.ink       = juce::Colour (0xff26211a);
            p.inkSoft   = juce::Colour (0xff26211a).withAlpha (0.80f);
            p.faint     = juce::Colour (0xff26211a).withAlpha (0.42f);
            p.label     = juce::Colour (0xff8a7f6a);
            p.accent    = theme::accent;
            p.ghost     = theme::agent;
            p.strike    = theme::bad;
            p.gold      = juce::Colour (0xffb8860b);
            p.sel       = theme::accent;
            return p;
        }();
        static const Pal slateP = [
        ] {
            Pal p;                                   // DARK MODE: a machined slate page —
            p.paper     = juce::Colour (0xff181a22); // material, never bare desk
            p.paperLine = juce::Colour (0xff2b2e3c);
            p.ink       = juce::Colour (0xffe9e6da); // warm off-white engraving ink
            p.inkSoft   = juce::Colour (0xffe9e6da).withAlpha (0.82f);
            p.faint     = juce::Colour (0xffe9e6da).withAlpha (0.40f);
            p.label     = juce::Colour (0xff8b8fa3);
            p.accent    = theme::accent;
            p.ghost     = theme::agent;
            p.strike    = theme::bad;
            p.gold      = juce::Colour (0xffe0b34d);
            p.sel       = theme::accent;
            return p;
        }();
        return (paperMode || printing) ? paperP : slateP;
    }

    //-------------------------------------------------- prefs (paper + zoom persist)
    static juce::File prefsFile()
    {
        return juce::File::getSpecialLocation (juce::File::userHomeDirectory)
                   .getChildFile (".config/sotadaw/score_prefs.json");
    }
    void loadPrefs()
    {
        const auto v = juce::JSON::parse (prefsFile().loadFileAsString());
        if (auto* o = v.getDynamicObject())
        {
            if (o->hasProperty ("paper")) paperMode = (bool) o->getProperty ("paper");
            if (o->hasProperty ("scale"))
                staffSpace = juce::jlimit (3.2f, 10.0f, (float) (double) o->getProperty ("scale"));
        }
    }
    void savePrefs() const
    {
        auto* o = new juce::DynamicObject();
        o->setProperty ("paper", paperMode);
        o->setProperty ("scale", (double) staffSpace);
        prefsFile().getParentDirectory().createDirectory();
        prefsFile().replaceWithText (juce::JSON::toString (juce::var (o), true));
    }

    //-------------------------------------------------- small utilities
    int layoutW() const { return printW > 0 ? printW : getWidth(); }
    int viewH() const { return juce::jmax (40, getHeight() - 34 - 22); }
    static juce::String fnum (double v)
    {
        auto s = juce::String (v, 2);
        while (s.contains (".") && (s.endsWith ("0") || s.endsWith ("."))) s = s.dropLastCharacters (1);
        return s;
    }
    juce::String noteName (int pitch) const
    {
        const auto sp = score::spellPitch (pitch, model.key);
        static const char* L = "CDEFGAB";
        juce::String a;
        if (sp.alter == 1) a = "#"; else if (sp.alter == -1) a = "b";
        else if (sp.alter >= 2) a = "##"; else if (sp.alter <= -2) a = "bb";
        return juce::String::charToString ((juce::juce_wchar) L[sp.letter]) + a
             + juce::String (sp.octave - 1);
    }
    juce::String posLabel (double gBeat) const
    {
        if (song == nullptr) return {};
        const int bar = (int) std::floor (song->barAtBeat (juce::jmax (0.0, gBeat)) + 1e-9);
        const double in = gBeat - song->barStartBeat (bar);
        return "bar " + juce::String (bar + 1) + " beat " + fnum (in + 1.0);
    }
    int staffIndexForTrack (int ti) const
    {
        for (int s = 0; s < (int) model.staves.size(); ++s)
        {
            auto& st = model.staves[(size_t) s];
            if (st.trackIdx == ti) return s;
            for (int m2 : st.mergedTracks) if (m2 == ti) return s;
        }
        return 0;
    }

    //-------------------------------------------------- model + geometry build
    void rebuildIfNeeded()
    {
        if (! dirty || song == nullptr) return;
        dirty = false;
        score::Options opt;
        opt.quant = quant;
        opt.mergeDrums = mergeDrums;
        if (ghosting && ghostProp != nullptr)
        { opt.proposal = ghostProp; opt.addedKeys = &ghostAdds; opt.removedNotes = &ghostRemoves; }
        model = score::buildModel (*song, opt);
        if (focusStaff != -2)                        // FOCUS: one staff fills the page
        {
            auto keep = model.staves;
            keep.erase (std::remove_if (keep.begin(), keep.end(), [this] (const score::Staff& s2)
                        { return focusStaff == -1 ? ! (s2.isDrums && s2.trackIdx == -1)
                                                  : s2.trackIdx != focusStaff; }),
                        keep.end());
            if (keep.empty())
                focusStaff = -2;                     // the staff left the song: release
            else
            {
                model.staves = std::move (keep);
                model.lyricStaff = -1;
                for (int si = 0; si < (int) model.staves.size(); ++si)
                {
                    const auto nm = model.staves[(size_t) si].name.toLowerCase();
                    if (nm.contains ("vocal") || nm.contains ("vox") || nm.contains ("voice")
                        || nm.contains ("sing"))
                    { model.lyricStaff = si; break; }
                }
            }
        }
        layout();
    }

    void layout()
    {
        const float S = staffSpace;
        // THE PAGE: BOTH themes engrave on a centered page — ivory in light,
        // machined slate in dark (bare-desk ink retired: material or nothing)
        pageWv = juce::jmax (320.0f, juce::jmin ((float) layoutW()
                                      - (printing ? 170.0f : 28.0f), 1380.0f));
        pageL  = juce::jmax (2.0f, ((float) layoutW() - pageWv) * 0.5f);
        sysL   = pageL + 64.0f;
        const float gutter = sysL;
        const float rightEdge = pageL + pageWv - 26.0f;
        const float usable = juce::jmax (240.0f, rightEdge - gutter);
        measGeo.assign ((size_t) model.numMeasures, {});
        systems.clear(); hits.clear(); ties.clear();
        if (model.staves.empty() || model.numMeasures == 0) { totalH = 0; return; }

        // score-wide column union + natural widths
        std::vector<float> natW ((size_t) model.numMeasures, 0.0f);
        for (int m = 0; m < model.numMeasures; ++m)
        {
            auto& G = measGeo[(size_t) m];
            std::set<long> cs;
            double beats = 4; bool meter = false;
            for (auto& st : model.staves)
                if (m < (int) st.measures.size())
                {
                    auto& M = st.measures[(size_t) m];
                    beats = M.beats; meter |= M.showMeter;
                    for (double c : M.colBeats) cs.insert (std::lround (c * 5040.0));
                }
            if (cs.empty()) cs.insert (0);
            for (long c : cs) G.colBeats.push_back ((double) c / 5040.0);
            // per-column pads: accidental / dot space demanded by ANY staff
            std::vector<float> pad (G.colBeats.size(), 0.0f);
            for (auto& st : model.staves)
                if (m < (int) st.measures.size())
                    for (int v = 0; v < 2; ++v)
                        for (auto& e : st.measures[(size_t) m].v[v])
                        {
                            const int ci = colIndex (G, e.start);
                            if (ci < 0) continue;
                            float p = 0;
                            for (auto& h : e.heads)
                            { if (h.shownAcc != -9) p = juce::jmax (p, 1.5f); if (h.otherSide) p = juce::jmax (p, 1.15f); }
                            if (e.dots > 0) p = juce::jmax (p, 0.7f);
                            pad[(size_t) ci] = juce::jmax (pad[(size_t) ci], p);
                        }
            float w = 1.0f * S + (meter ? 3.2f * S : 0.0f);
            for (size_t i = 0; i < G.colBeats.size(); ++i)
            {
                const double dt = (i + 1 < G.colBeats.size() ? G.colBeats[i + 1] : beats) - G.colBeats[i];
                const double gour = 2.1 + 1.05 * std::log2 (juce::jlimit (1.0, 32.0, dt / 0.125));
                w += pad[i] * S + (float) gour * S;
            }
            w += 1.2f * S;
            natW[(size_t) m] = w;
        }

        // key/clef prefix width (per system)
        const float prefixW = 3.6f * S + (float) std::abs (model.key.fifths) * 1.1f * S + 1.2f * S;

        // vertical plan per staff
        const bool furniture = ! model.chords.empty() || ! model.sections.empty() || ! model.tempos.empty();
        std::vector<float> topPad, botPad;
        for (int s = 0; s < (int) model.staves.size(); ++s)
        {
            auto& st = model.staves[(size_t) s];
            float tp = juce::jmax (2.6f * S, (float) (st.hiStep - 8) * 0.5f * S + 1.4f * S);
            if (s == 0 && furniture) tp += 3.0f * S;
            float bp = juce::jmax (2.6f * S, (float) (0 - st.loStep) * 0.5f * S + 1.4f * S);
            if (! st.dyns.empty() || ! st.hairs.empty()) bp += 2.2f * S;   // marks band
            if (s == model.lyricStaff && ! model.lyrics.empty()) bp += 3.0f * S;
            topPad.push_back (tp); botPad.push_back (bp);
        }

        float y = 132.0f;                         // title block rides above the first system
        if (ghosting) y += 14.0f;                 // the stand line earns a row
        int m = 0;
        while (m < model.numMeasures)
        {
            SysGeo sys;
            sys.m0 = m;
            float x = gutter + prefixW;
            int count = 0;
            while (m + count < model.numMeasures
                   && (count == 0 || x + natW[(size_t) (m + count)] <= gutter + usable))
            { x += natW[(size_t) (m + count)]; ++count; }
            sys.count = count;
            // justify (never the last system)
            float stretch = 1.0f;
            const bool last = m + count >= model.numMeasures;
            if (! last && x < gutter + usable)
            {
                float colSum = 0;
                for (int i = 0; i < count; ++i) colSum += natW[(size_t) (m + i)];
                if (colSum > 1.0f) stretch = 1.0f + (gutter + usable - x) / colSum;
                stretch = juce::jmin (stretch, 1.6f);
            }
            // vertical
            sys.y0 = y;
            float cy = y;
            for (int s = 0; s < (int) model.staves.size(); ++s)
            {
                cy += topPad[(size_t) s];
                sys.staffTop.push_back (cy);
                cy += 4.0f * S + botPad[(size_t) s] + 1.4f * S;
            }
            sys.h = cy - y;
            // horizontal per measure: columns at stretched Gourlay positions
            float mx = gutter + prefixW;
            for (int i = 0; i < count; ++i)
            {
                auto& G = measGeo[(size_t) (m + i)];
                G.sys = (int) systems.size();
                G.x0 = mx;
                double beats = 4; bool meter = false;
                for (auto& st : model.staves)
                    if (m + i < (int) st.measures.size())
                    { beats = st.measures[(size_t) (m + i)].beats; meter |= st.measures[(size_t) (m + i)].showMeter; }
                float cx = mx + (1.0f * S + (meter ? 3.2f * S : 0.0f)) * stretch;
                std::vector<float> pad (G.colBeats.size(), 0.0f);
                for (auto& st : model.staves)
                    if (m + i < (int) st.measures.size())
                        for (int v = 0; v < 2; ++v)
                            for (auto& e : st.measures[(size_t) (m + i)].v[v])
                            {
                                const int ci = colIndex (G, e.start);
                                if (ci < 0) continue;
                                float p = 0;
                                for (auto& h : e.heads)
                                { if (h.shownAcc != -9) p = juce::jmax (p, 1.5f); if (h.otherSide) p = juce::jmax (p, 1.15f); }
                                if (e.dots > 0) p = juce::jmax (p, 0.7f);
                                pad[(size_t) ci] = juce::jmax (pad[(size_t) ci], p);
                            }
                G.colX.resize (G.colBeats.size());
                for (size_t ci = 0; ci < G.colBeats.size(); ++ci)
                {
                    cx += pad[ci] * S * stretch;
                    G.colX[ci] = cx;
                    const double dt = (ci + 1 < G.colBeats.size() ? G.colBeats[ci + 1] : beats) - G.colBeats[ci];
                    const double gour = 2.1 + 1.05 * std::log2 (juce::jlimit (1.0, 32.0, dt / 0.125));
                    cx += (float) gour * S * stretch;
                }
                G.endX = mx + natW[(size_t) (m + i)] * stretch;
                G.w = G.endX - G.x0;
                mx = G.endX;
            }
            systems.push_back (sys);
            y += sys.h + 3.6f * S;
            m += count;
        }
        totalH = y + 56.0;
        viewY = juce::jlimit (0.0, juce::jmax (0.0, totalH - 34.0 - (double) viewH()), viewY);
        vScroll.setRangeLimits (0.0, juce::jmax (totalH, 1.0));
        vScroll.setCurrentRange (viewY, viewH(), juce::dontSendNotification);

        // staff labels are HANDS: name = select staff, dbl = focus, M/S dots = flags
        labelHits.clear();
        for (int sy2 = 0; sy2 < (int) systems.size(); ++sy2)
            for (int s = 0; s < (int) model.staves.size(); ++s)
            {
                const float ty = systems[(size_t) sy2].staffTop[(size_t) s];
                LabelHit lh;
                lh.staff = s; lh.sys = sy2;
                lh.r    = { juce::jmax (2.0f, sysL - 58.0f), ty - 0.6f * S, 52.0f, 3.0f * S };
                lh.mDot = { juce::jmax (2.0f, sysL - 56.0f), ty + 2.7f * S, 12.0f, 12.0f };
                lh.sDot = { juce::jmax (2.0f, sysL - 41.0f), ty + 2.7f * S, 12.0f, 12.0f };
                labelHits.push_back (lh);
            }

        buildHitsAndTies();
    }

    static int colIndex (const MeasGeo& G, double beat)
    {
        for (size_t i = 0; i < G.colBeats.size(); ++i)
            if (std::abs (G.colBeats[i] - beat) < 1e-4) return (int) i;
        return -1;
    }

    float yOfStep (int sysIdx, int staffIdx, int step) const
    {
        return systems[(size_t) sysIdx].staffTop[(size_t) staffIdx]
               + (8 - step) * staffSpace * 0.5f;
    }

    void buildHitsAndTies()
    {
        const float S = staffSpace, headW = 1.25f * S;
        for (int s = 0; s < (int) model.staves.size(); ++s)
        {
            auto& st = model.staves[(size_t) s];
            for (int v = 0; v < 2; ++v)
            {
                score::Element* prevTie = nullptr; int prevM = 0, prevE = 0;
                for (int m = 0; m < (int) st.measures.size(); ++m)
                {
                    auto& G = measGeo[(size_t) m];
                    auto& vec = st.measures[(size_t) m].v[v];
                    for (int ei = 0; ei < (int) vec.size(); ++ei)
                    {
                        auto& e = vec[(size_t) ei];
                        if (prevTie != nullptr && ! e.isRest)
                        {
                            ties.push_back ({ s, v, prevM, prevE, m, ei });
                            prevTie = nullptr;
                        }
                        if (e.tieFrom && ! e.isRest) { prevTie = &e; prevM = m; prevE = ei; }
                        if (e.isRest) continue;
                        const int ci = colIndex (G, e.start);
                        if (ci < 0) continue;
                        const float x = G.colX[(size_t) ci];
                        for (int hi = 0; hi < (int) e.heads.size(); ++hi)
                        {
                            auto& h = e.heads[(size_t) hi];
                            const float hx = x + (h.otherSide ? (e.stemUp ? headW : -headW) : 0.0f);
                            const float hy = yOfStep (G.sys, s, h.step);
                            Hit ht;
                            ht.r = { hx - 1.0f, hy - S * 0.75f, headW + 2.0f, S * 1.5f };
                            ht.src = h.src; ht.staff = s; ht.meas = m; ht.voice = v; ht.elem = ei; ht.head = hi;
                            hits.push_back (ht);
                        }
                    }
                }
            }
        }
    }

    //-------------------------------------------------- paint: the engraving
    void paintEmpty (juce::Graphics& g)
    {
        const float pw = pageWv > 0 ? pageWv : (float) getWidth() - 4.0f;
        const float px = pageWv > 0 ? pageL : 2.0f;
        paintPaper (g);
        g.setColour (pal().faint.withAlpha (0.16f));
        if (bravura() != nullptr) drawGlyph (g, smufl::gClef, px + pw * 0.5f - 40.0f, 300.0f, 24.0f);
        g.setColour (pal().inkSoft);
        g.setFont (theme::ui (15.0f));
        g.drawText ("nothing on the stand yet",
                    juce::Rectangle<int> ((int) px, 344, (int) pw, 22), juce::Justification::centred);
        g.setColour (pal().label);
        g.setFont (theme::ui (11.5f));
        g.drawText ("MIDI tracks appear here as engraved sheet music - ask the agent below,",
                    juce::Rectangle<int> ((int) px, 372, (int) pw, 16), juce::Justification::centred);
        g.drawText ("drop a .mid / .musicxml anywhere, or add a track and write notes",
                    juce::Rectangle<int> ((int) px, 390, (int) pw, 16), juce::Justification::centred);
    }

    void paintPaper (juce::Graphics& g)
    {
        const float x = pageWv > 0 ? pageL : 2.0f;
        const float w = pageWv > 0 ? pageWv : (float) getWidth() - 4.0f;
        const float y0 = 40.0f;
        const float y1 = juce::jmax (y0 + 460.0f, (float) totalH - 10.0f);
        juce::Rectangle<float> pr (x, y0, w, y1 - y0);
        for (int i = 3; i >= 1; --i)                       // soft shadow, render-cheap
        {                                                  // (deeper on the dark desk)
            g.setColour (juce::Colours::black.withAlpha ((paperMode ? 0.045f : 0.085f) * (float) i));
            g.fillRoundedRectangle (pr.expanded ((float) (4 - i) * 2.4f)
                                       .translated (0.0f, (float) (4 - i) * 1.5f), 11.0f);
        }
        g.setColour (pal().paper);
        g.fillRoundedRectangle (pr, 8.0f);
        // top sheen: daylight on ivory, a cool glass glow on slate
        g.setGradientFill ({ paperMode ? juce::Colours::white.withAlpha (0.30f)
                                       : theme::accent.withAlpha (0.055f),
                             pr.getTopLeft(),
                             juce::Colours::transparentWhite,
                             { pr.getX(), pr.getY() + 240.0f }, false });
        g.fillRoundedRectangle (pr.withHeight (juce::jmin (240.0f, pr.getHeight())), 8.0f);
        g.setColour (pal().paperLine);
        g.drawRoundedRectangle (pr, 8.0f, 1.2f);
        if (! paperMode && ! printing)                     // machined inner edge: slate is GLASS
        {
            g.setColour (juce::Colours::white.withAlpha (0.055f));
            g.drawRoundedRectangle (pr.reduced (1.4f), 7.0f, 1.0f);
        }
    }

    void paintTitle (juce::Graphics& g, float y)
    {
        if (song == nullptr) return;
        const auto name = getSongName ? getSongName() : juce::String ("score");
        g.setColour (pal().ink);
        g.setFont (theme::ui (19.0f, juce::Font::bold));
        g.drawText (name, juce::Rectangle<int> ((int) sysL, (int) y,
                        (int) juce::jmax (220.0f, pageWv - 220.0f), 24), juce::Justification::left);
        g.setColour (pal().label);
        g.setFont (theme::caps (8.5f));
        juce::String meta = model.key.label + "  -  " + fnum (song->bpm) + " BPM  -  "
                            + juce::String (model.numMeasures) + " BARS";
        if (model.swung) meta += "  -  SWING";
        if (focusStaff != -2) meta += "  -  FOCUS (dbl-click the staff name to release)";
        g.drawText (meta, juce::Rectangle<int> ((int) sysL, (int) y + 26, 780, 12),
                    juce::Justification::left);
        if (ghosting)
        {
            g.setColour (pal().ghost);
            g.drawText ("TAKE ON THE STAND - read-only - the deck holds the verdict",
                        juce::Rectangle<int> ((int) sysL, (int) y + 40, 780, 12),
                        juce::Justification::left);
        }
        g.setColour (pal().label.withAlpha (0.7f));
        g.setFont (theme::caps (7.5f));
        g.drawText ("SOTA DAW", juce::Rectangle<int> ((int) (pageL + (pageWv > 0 ? pageWv : (float) getWidth()) - 140),
                        (int) y + 3, 116, 12), juce::Justification::right);
    }

    bool staffMuted (const score::Staff& st) const
    {
        if (! isMuted) return false;
        if (st.mergedTracks.empty()) return st.trackIdx >= 0 && isMuted (st.trackIdx);
        for (int t : st.mergedTracks) if (! isMuted (t)) return false;
        return true;
    }
    bool staffSoloed (const score::Staff& st) const
    {
        if (! isSoloed) return false;
        if (st.mergedTracks.empty()) return st.trackIdx >= 0 && isSoloed (st.trackIdx);
        for (int t : st.mergedTracks) if (isSoloed (t)) return true;
        return false;
    }

    void paintSystemBlock (juce::Graphics& g, int sy)
    {
        auto& sys = systems[(size_t) sy];
        const float S = staffSpace;
        const float sysR = measGeo[(size_t) (sys.m0 + sys.count - 1)].endX;
        const auto& P = pal();

        // staff lines + identity rail (swatch, name, M/S dots) + clefs + key sigs
        for (int s = 0; s < (int) model.staves.size(); ++s)
        {
            auto& st = model.staves[(size_t) s];
            const float ty = sys.staffTop[(size_t) s];
            const int cIdx = st.trackIdx >= 0 ? st.trackIdx
                             : (st.mergedTracks.empty() ? 0 : st.mergedTracks.front());
            const bool stMuted = staffMuted (st);
            g.setColour (P.faint.withAlpha (P.faint.getFloatAlpha() * (stMuted ? 0.55f : 1.0f)));
            for (int L = 0; L < 5; ++L)
                g.fillRect (juce::Rectangle<float> (sysL, ty + L * S - 0.55f, sysR - sysL, 1.1f));
            const LabelHit* lh = nullptr;
            for (auto& l2 : labelHits) if (l2.sys == sy && l2.staff == s) { lh = &l2; break; }
            const float labelX = lh != nullptr ? lh->r.getX() : juce::jmax (2.0f, sysL - 58.0f);
            if (! printing)
            {
                g.setColour (trackColourOf ? trackColourOf (cIdx).withAlpha (0.9f) : P.accent);
                g.fillRoundedRectangle (labelX, ty + 0.6f * S, 3.0f, 2.8f * S, 1.5f);
            }
            const bool focused = focusStaff != -2
                && (st.trackIdx >= 0 ? focusStaff == st.trackIdx : focusStaff == -1);
            g.setColour (focused ? P.accent : P.label.withAlpha (stMuted ? 0.5f : 1.0f));
            g.setFont (theme::caps (8.0f));
            g.drawText (sy == 0 ? st.name.toUpperCase() : st.name.substring (0, 3).toUpperCase(),
                        juce::Rectangle<int> ((int) labelX + 7, (int) (ty + S), 46, (int) (2 * S)),
                        juce::Justification::left);
            if (! printing && lh != nullptr)
            {
                auto dot = [&g] (juce::Rectangle<float> r2, bool on, juce::Colour c, const char* t)
                {
                    g.setColour (on ? c : c.withAlpha (0.20f));
                    g.fillEllipse (r2);
                    g.setColour (on ? juce::Colours::black.withAlpha (0.75f) : c.withAlpha (0.75f));
                    g.setFont (theme::caps (6.0f));
                    g.drawText (t, r2.toNearestInt(), juce::Justification::centred);
                };
                dot (lh->mDot, stMuted, theme::bad.withAlpha (0.85f), "M");
                dot (lh->sDot, staffSoloed (st), juce::Colour (0xff6fbf73), "S");
            }
            g.setColour (P.ink);
            if (bravura() != nullptr)
            {
                if (st.clef == score::Clef::Treble)      drawGlyph (g, smufl::gClef,   sysL + 0.6f * S, yOfStep (sy, s, 2), S);
                else if (st.clef == score::Clef::Bass)   drawGlyph (g, smufl::fClef,   sysL + 0.6f * S, yOfStep (sy, s, 6), S);
                else                                     drawGlyph (g, smufl::percClef, sysL + 0.8f * S, yOfStep (sy, s, 4), S);
            }
            else
            {
                g.setFont (theme::caps (S * 2.4f));
                g.drawText (st.clef == score::Clef::Treble ? "G" : st.clef == score::Clef::Bass ? "F" : "II",
                            juce::Rectangle<int> ((int) (sysL + S), (int) ty, (int) (3 * S), (int) (4 * S)),
                            juce::Justification::centredLeft);
            }
            if (! st.isDrums && model.key.fifths != 0 && bravura() != nullptr)
            {
                static const int shT[7] = { 8, 5, 9, 6, 3, 7, 4 };   // treble sharp steps
                static const int flT[7] = { 4, 7, 3, 6, 2, 5, 1 };
                const int n = std::abs (model.key.fifths);
                for (int i = 0; i < n; ++i)
                {
                    int step = model.key.fifths > 0 ? shT[i] : flT[i];
                    if (st.clef == score::Clef::Bass) step -= 2;
                    drawGlyph (g, model.key.fifths > 0 ? smufl::accSharp : smufl::accFlat,
                               sysL + 4.0f * S + i * 1.1f * S, yOfStep (sy, s, step), S);
                }
            }
        }
        // playing measure gets a soft tint (canvas follows ears)
        const float sysT = sys.staffTop.front(), sysB = sys.staffTop.back() + 4 * S;
        if (paintPlaying && ! printing && paintPh >= 0)
        {
            const int pm = measureAtBeat (paintPh);
            if (pm >= sys.m0 && pm < sys.m0 + sys.count)
            {
                auto& G = measGeo[(size_t) pm];
                g.setColour (P.accent.withAlpha (paperMode ? 0.05f : 0.07f));
                g.fillRect (juce::Rectangle<float> (G.x0, sysT - 1.0f * S,
                                                    G.endX - G.x0, sysB - sysT + 2.0f * S));
            }
        }
        // system barline (joins all staves) + measure barlines
        g.setColour (P.ink.withAlpha (0.55f));
        g.fillRect (juce::Rectangle<float> (sysL, sysT, 1.4f, sysB - sysT));
        for (int i = 0; i < sys.count; ++i)
        {
            auto& G = measGeo[(size_t) (sys.m0 + i)];
            const bool fin = sys.m0 + i == model.numMeasures - 1;
            g.fillRect (juce::Rectangle<float> (G.endX, sysT, fin ? 1.2f : 1.0f, sysB - sysT));
            if (fin) g.fillRect (juce::Rectangle<float> (G.endX + 2.6f, sysT, 3.6f, sysB - sysT));
        }
        // measure number at each system start (bar 1 is obvious)
        if (sy > 0)
        {
            g.setColour (P.label);
            g.setFont (theme::mono (8.0f));
            g.drawText (juce::String (sys.m0 + 1),
                        juce::Rectangle<int> ((int) sysL - 2, (int) (sysT - 2.6f * S), 40, 10),
                        juce::Justification::left);
        }
        // the arrange loop region rides the score as a brace
        if (! printing && getLoop)
        {
            const auto lp = getLoop();
            if (lp.second > lp.first && lp.first >= 0)
            {
                const double b0 = measStartBeat (sys.m0);
                const double b1 = measStartBeat (sys.m0 + sys.count - 1)
                                  + measBeats (sys.m0 + sys.count - 1);
                const double a = juce::jmax (lp.first, b0), b2 = juce::jmin (lp.second, b1);
                if (b2 > a + 1e-6)
                {
                    const int ma = measureAtBeat (a), mb = measureAtBeat (b2 - 1e-6);
                    const float xa = beatToX (ma, a - measStartBeat (ma));
                    const float xb = beatToX (mb, b2 - 1e-6 - measStartBeat (mb));
                    const float yb = sysT - 2.2f * S;
                    g.setColour (P.accent.withAlpha (0.55f));
                    g.fillRect (juce::Rectangle<float> (xa, yb, juce::jmax (2.0f, xb - xa), 1.6f));
                    if (lp.first >= b0 - 1e-6) g.fillRect (juce::Rectangle<float> (xa, yb, 1.6f, 0.9f * S));
                    if (lp.second <= b1 + 1e-6) g.fillRect (juce::Rectangle<float> (xb - 1.6f, yb, 1.6f, 0.9f * S));
                }
            }
        }

        paintFurniture (g, sy);
        for (int s = 0; s < (int) model.staves.size(); ++s)
            paintStaffContent (g, sy, s, {});
        paintMarks (g, sy);
        paintTiesFor (g, sy);
        if (! printing) paintPlayhead (g, sy);
    }

    void paintMarks (juce::Graphics& g, int sy)   // dynamics letters + hairpins
    {
        auto& sys = systems[(size_t) sy];
        const float S = staffSpace;
        const double b0 = measStartBeat (sys.m0);
        const double b1 = measStartBeat (sys.m0 + sys.count - 1) + measBeats (sys.m0 + sys.count - 1);
        const bool haveFont = bravura() != nullptr;
        for (int s = 0; s < (int) model.staves.size(); ++s)
        {
            auto& st = model.staves[(size_t) s];
            if (st.dyns.empty() && st.hairs.empty()) continue;
            const float dy = sys.staffTop[(size_t) s] + 4.0f * S + 2.0f * S;
            g.setColour (pal().inkSoft);
            if (haveFont)
                for (auto& d : st.dyns)
                {
                    if (d.beat < b0 - 1e-6 || d.beat >= b1 - 1e-6) continue;
                    const int mi = measureAtBeat (d.beat);
                    const float x = beatToX (mi, d.beat - measStartBeat (mi));
                    static const juce::juce_wchar glyphs[6] = { smufl::dynPP, smufl::dynP, smufl::dynMP,
                                                                smufl::dynMF, smufl::dynF, smufl::dynFF };
                    drawGlyph (g, glyphs[juce::jlimit (0, 5, d.level)], x - 0.4f * S, dy + 0.9f * S, S * 0.9f);
                }
            for (auto& h : st.hairs)
            {
                const double a = juce::jmax (h.a, b0), b2 = juce::jmin (h.b, b1);
                if (b2 - a < 0.5) continue;
                const int ma = measureAtBeat (a), mb = measureAtBeat (b2 - 1e-6);
                const float xa = beatToX (ma, a - measStartBeat (ma));
                const float xb = beatToX (mb, b2 - 1e-6 - measStartBeat (mb));
                if (xb - xa < 3.0f * S) continue;
                const float ym = dy + 0.55f * S, half = 0.42f * S;
                g.setColour (pal().inkSoft.withAlpha (0.8f));
                if (h.cresc)
                {
                    g.drawLine (xa + 1.4f * S, ym, xb, ym - half, 1.1f);
                    g.drawLine (xa + 1.4f * S, ym, xb, ym + half, 1.1f);
                }
                else
                {
                    g.drawLine (xa, ym - half, xb - 0.4f * S, ym, 1.1f);
                    g.drawLine (xa, ym + half, xb - 0.4f * S, ym, 1.1f);
                }
            }
        }
    }

    void paintFurniture (juce::Graphics& g, int sy)
    {
        auto& sys = systems[(size_t) sy];
        const float S = staffSpace;
        const float bandY = sys.staffTop.front() - 3.4f * S;
        for (auto& c : model.chords)
            if (c.measure >= sys.m0 && c.measure < sys.m0 + sys.count)
            {
                g.setColour (pal().inkSoft);
                g.setFont (theme::ui (juce::jmax (9.0f, S * 1.9f), juce::Font::bold));
                g.drawText (c.label, (int) measGeo[(size_t) c.measure].x0, (int) (bandY - S),
                            90, (int) (2.2f * S), juce::Justification::left);
            }
        for (auto& s2 : model.sections)
            if (s2.measure >= sys.m0 && s2.measure < sys.m0 + sys.count)
            {
                g.setFont (theme::caps (8.0f));
                const auto t = s2.name.toUpperCase();
                const int tw = (int) textW (theme::caps (8.0f), t) + 12;
                juce::Rectangle<float> chip ((float) measGeo[(size_t) s2.measure].x0 - 2.0f,
                                             bandY - 3.2f * S, (float) tw, 2.2f * S);
                g.setColour (theme::panelHi.withAlpha (0.9f));
                g.fillRoundedRectangle (chip, 3.0f);
                g.setColour (theme::accent.withAlpha (0.5f));
                g.drawRoundedRectangle (chip, 3.0f, 1.0f);
                g.setColour (theme::text);
                g.drawText (t, chip.toNearestInt(), juce::Justification::centred);
            }
        for (auto& tm : model.tempos)
            if (tm.measure >= sys.m0 && tm.measure < sys.m0 + sys.count && (tm.measure > 0 || sy == 0))
            {
                const float x = measGeo[(size_t) tm.measure].x0 + (tm.measure == 0 ? 60.0f : 0.0f);
                g.setColour (pal().inkSoft);
                if (bravura() != nullptr) drawGlyph (g, smufl::metQuarterUp, x, bandY + 1.2f * S, S * 0.75f);
                g.setFont (theme::mono (juce::jmax (8.5f, S * 1.7f)));
                g.drawText ("= " + juce::String (tm.bpm, tm.bpm == (int) tm.bpm ? 0 : 1),
                            (int) x + (int) (1.6f * S), (int) (bandY - 0.2f * S), 70, (int) (2 * S),
                            juce::Justification::left);
            }
    }

    void paintStaffContent (juce::Graphics& g, int sy, int s, juce::Rectangle<int>)
    {
        auto& sys = systems[(size_t) sy];
        auto& st = model.staves[(size_t) s];
        const float S = staffSpace, headW = 1.25f * S;
        const auto ink = pal().ink;

        for (int mi = sys.m0; mi < sys.m0 + sys.count && mi < (int) st.measures.size(); ++mi)
        {
            auto& M = st.measures[(size_t) mi];
            auto& G = measGeo[(size_t) mi];
            // meter change glyphs
            if (M.showMeter && bravura() != nullptr)
            {
                const float tx = G.x0 + 1.0f * S;
                auto digits = [this, &g, S] (int n, float x, float baseline)
                {
                    const auto t = juce::String (n);
                    float cx = x;
                    for (auto ch : t)
                    { drawGlyph (g, (juce::juce_wchar) (smufl::timeSig0 + (ch - '0')), cx, baseline, S); cx += glyphWidth ((juce::juce_wchar) (smufl::timeSig0 + (ch - '0')), S) + 0.1f * S; }
                };
                g.setColour (ink);
                digits (M.num, tx, yOfStep (sy, s, 4));
                digits (M.den, tx, yOfStep (sy, s, 0));
            }
            // elements
            for (int v = 0; v < 2; ++v)
            {
                for (int ei = 0; ei < (int) M.v[v].size(); ++ei)
                {
                    auto& e = M.v[v][(size_t) ei];
                    const int ci = colIndex (G, e.start);
                    if (ci < 0) continue;
                    const float x = G.colX[(size_t) ci];
                    if (e.isRest) { paintRest (g, sy, s, e, x, G); continue; }
                    paintNoteElement (g, sy, s, mi, v, ei, e, x, G);
                }
            }
            // beams after stems
            for (auto& bm : M.beams)
                paintBeam (g, sy, s, mi, bm);
            // ghost strikes (removed notes)
            for (auto& gs : st.strikes)
                if (gs.measure == mi)
                {
                    const float x = beatToX (mi, gs.start);
                    const float y = yOfStep (sy, s, gs.step);
                    g.setColour (pal().strike.withAlpha (0.75f));
                    g.drawLine (x - 0.9f * S, y - 0.9f * S, x + 0.9f * S + headW * 0.4f, y + 0.9f * S, 1.4f);
                    g.drawLine (x - 0.9f * S, y + 0.9f * S, x + 0.9f * S + headW * 0.4f, y - 0.9f * S, 1.4f);
                    g.drawLine (x - 1.4f * S, y, x + 1.8f * S, y, 1.1f);
                }
        }
        // lyrics under the sung staff
        if (s == model.lyricStaff && ! model.lyrics.empty())
        {
            g.setColour (pal().inkSoft);
            g.setFont (theme::ui (juce::jmax (8.5f, S * 1.85f)));
            const float ly = sys.staffTop[(size_t) s] + 4 * S + 2.6f * S
                             + ((st.dyns.empty() && st.hairs.empty()) ? 0.0f : 1.9f * S);
            for (auto& syl : model.lyrics)
            {
                const int mi = measureAtBeat (syl.beat);
                if (mi < sys.m0 || mi >= sys.m0 + sys.count) continue;
                const float x = beatToX (mi, syl.beat - measStartBeat (mi));
                g.drawText (syl.text, (int) (x - 1.5f * S), (int) ly, (int) (12 * S), (int) (2.4f * S),
                            juce::Justification::left);
            }
        }
    }

    void paintNoteElement (juce::Graphics& g, int sy, int s, int mi, int v, int ei,
                           const score::Element& e, float x, const MeasGeo& G)
    {
        auto& st = model.staves[(size_t) s];
        const float S = staffSpace, headW = 1.25f * S;
        const bool haveFont = bravura() != nullptr;
        const double gStart = measStartBeat (mi) + e.start;
        const bool sounding = paintPlaying && ! printing
                              && paintPh >= gStart && paintPh < gStart + e.dur;

        // ledger lines
        g.setColour (pal().ink.withAlpha (0.45f));
        for (auto& h : e.heads)
        {
            const float hx = x + (h.otherSide ? (e.stemUp ? headW : -headW) : 0.0f);
            for (int L = 10; L <= h.step; L += 2)
                g.fillRect (juce::Rectangle<float> (hx - 0.45f * S, yOfStep (sy, s, L) - 0.5f, headW + 0.9f * S, 1.0f));
            for (int L = -2; L >= h.step; L -= 2)
                g.fillRect (juce::Rectangle<float> (hx - 0.45f * S, yOfStep (sy, s, L) - 0.5f, headW + 0.9f * S, 1.0f));
        }

        // stem geometry: outermost heads decide
        int loStep = e.heads.front().step, hiStep = e.heads.back().step;
        const float stemX = e.stemUp ? x + headW - 0.6f : x + 0.6f;
        float tipY = e.stemUp ? yOfStep (sy, s, hiStep) - 3.5f * S
                              : yOfStep (sy, s, loStep) + 3.5f * S;
        if (e.beamGroup >= 0) tipY = beamTipY (sy, s, mi, e, stemX);

        // heads
        for (int hi = 0; hi < (int) e.heads.size(); ++hi)
        {
            auto& h = e.heads[(size_t) hi];
            const float hx = x + (h.otherSide ? (e.stemUp ? headW : -headW) : 0.0f);
            const float hy = yOfStep (sy, s, h.step);
            auto col = pal().ink;
            const bool selected = selection.count (key (h.src)) > 0;
            const bool hovered = hoverKey == key (h.src);
            if (h.ghostAdd)      col = pal().ghost;
            if (sounding)        col = pal().gold;
            if (selected)        col = pal().sel;
            g.setColour (col.withAlpha (0.55f + 0.45f * juce::jlimit (0.0f, 1.0f, h.vel)));
            if (haveFont)
            {
                juce::juce_wchar c = smufl::headBlack;
                if (h.shape == score::HeadShape::X)            c = smufl::headXBlack;
                else if (h.shape == score::HeadShape::CircleX) c = smufl::headCircleX;
                else if (e.denom == 1)                         c = smufl::headWhole;
                else if (e.denom == 2)                         c = smufl::headHalf;
                drawGlyph (g, c, hx, hy, S);
            }
            else
            {
                juce::Path p;
                p.addEllipse (hx, hy - 0.62f * S, headW, 1.24f * S);
                p.applyTransform (juce::AffineTransform::rotation (-0.35f, hx + headW / 2, hy));
                if (e.denom <= 2) g.strokePath (p, juce::PathStrokeType (1.4f));
                else              g.fillPath (p);
            }
            if ((selected || hovered) && ! printing)
            {
                g.setColour ((selected ? pal().sel : pal().ink).withAlpha (selected ? 0.5f : 0.25f));
                g.drawEllipse (hx - 0.35f * S, hy - S, headW + 0.7f * S, 2.0f * S, 1.2f);
            }
            // accidental
            if (h.shownAcc != -9 && haveFont)
            {
                g.setColour (col.withAlpha (0.95f));
                const juce::juce_wchar a = h.shownAcc == 0 ? smufl::accNatural
                                          : h.shownAcc == 1 ? smufl::accSharp
                                          : h.shownAcc == -1 ? smufl::accFlat
                                          : h.shownAcc >= 2 ? smufl::accDblSharp : smufl::accDblFlat;
                drawGlyph (g, a, x - 1.35f * S, hy, S);
            }
            // dots (in the space above a line-head)
            for (int d = 0; d < e.dots; ++d)
            {
                const float dy2 = (h.step % 2 == 0) ? -0.5f * S : 0.0f;
                g.setColour (col.withAlpha (0.9f));
                g.fillEllipse (x + headW + 0.45f * S + d * 0.8f * S, yOfStep (sy, s, h.step) + dy2 - 0.22f * S,
                               0.44f * S, 0.44f * S);
            }
        }

        // stem + flags
        if (e.denom >= 2)
        {
            g.setColour (pal().ink.withAlpha (0.9f));
            const float yA = e.stemUp ? yOfStep (sy, s, loStep) : yOfStep (sy, s, hiStep);
            g.fillRect (juce::Rectangle<float> (stemX - 0.55f, juce::jmin (yA, tipY),
                                                1.1f, std::abs (yA - tipY)));
            if (e.beamGroup < 0 && e.denom >= 8 && haveFont)
            {
                const juce::juce_wchar f = e.denom == 8 ? (e.stemUp ? smufl::flag8Up : smufl::flag8Down)
                                          : e.denom == 16 ? (e.stemUp ? smufl::flag16Up : smufl::flag16Down)
                                          : (e.stemUp ? smufl::flag32Up : smufl::flag32Down);
                drawGlyph (g, f, stemX - 0.55f, tipY, S);
            }
        }
        // unbeamed triplet digit
        if (e.triplet && e.beamGroup < 0 && bravura() != nullptr)
            drawGlyph (g, smufl::tuplet3, x + headW * 0.2f, tipY + (e.stemUp ? -0.6f * S : 1.8f * S), S * 0.8f);
        // articulation on the head side (opposite the stem): staccato dot / accent
        if (e.artic != 0 && ! e.heads.empty())
        {
            const auto& anchor = e.stemUp ? e.heads.front() : e.heads.back();
            const float ax = x + headW * 0.5f;
            float ay = yOfStep (sy, s, anchor.step) + (e.stemUp ? 1.15f * S : -1.15f * S);
            if (anchor.step >= 0 && anchor.step <= 8 && anchor.step % 2 == 0)
                ay += e.stemUp ? 0.30f * S : -0.30f * S;      // clear the staff line
            g.setColour (pal().ink.withAlpha (0.9f));
            if (e.artic & 1)
                g.fillEllipse (ax - 0.21f * S, ay - 0.21f * S, 0.42f * S, 0.42f * S);
            if ((e.artic & 2) && haveFont)
                drawGlyph (g, e.stemUp ? smufl::accentBelow : smufl::accentAbove,
                           ax - 0.55f * S, ay + (e.stemUp ? 1.1f : -0.5f) * S, S * 0.8f);
        }
        juce::ignoreUnused (v, ei, G);
    }

    void paintRest (juce::Graphics& g, int sy, int s, const score::Element& e, float x, const MeasGeo& G)
    {
        const float S = staffSpace;
        g.setColour (pal().ink.withAlpha (0.55f));
        float rx = x;
        if (e.wholeMeasureRest) rx = G.x0 + G.w * 0.5f - 0.7f * S;
        if (bravura() != nullptr)
        {
            juce::juce_wchar c = smufl::restQuarter;
            if (e.wholeMeasureRest || e.denom == 1) c = smufl::restWhole;
            else if (e.denom == 2)  c = smufl::restHalf;
            else if (e.denom == 8)  c = smufl::rest8;
            else if (e.denom == 16) c = smufl::rest16;
            else if (e.denom == 32) c = smufl::rest32;
            drawGlyph (g, c, rx, yOfStep (sy, s, (e.wholeMeasureRest || e.denom == 1) ? 6 : 4), S);
            for (int d = 0; d < e.dots; ++d)
                g.fillEllipse (rx + 1.6f * S + d * 0.8f * S, yOfStep (sy, s, 5) - 0.2f * S, 0.4f * S, 0.4f * S);
        }
        else
            g.fillRect (juce::Rectangle<float> (rx, yOfStep (sy, s, e.denom <= 2 ? 6 : 4), 1.2f * S, 0.5f * S));
    }

    float beamTipY (int sy, int s, int mi, const score::Element& e, float stemX)
    {
        auto& M = model.staves[(size_t) s].measures[(size_t) mi];
        if (e.beamGroup < 0 || e.beamGroup >= (int) M.beams.size()) return 0;
        auto& bm = M.beams[(size_t) e.beamGroup];
        auto& G = measGeo[(size_t) mi];
        const float S = staffSpace, headW = 1.25f * S;
        auto stemXFor = [&] (const score::Element& el)
        {
            const int ci = colIndex (G, el.start);
            const float x = ci >= 0 ? G.colX[(size_t) ci] : G.x0;
            return el.stemUp ? x + headW - 0.6f : x + 0.6f;
        };
        auto naturalTip = [&] (const score::Element& el)
        {
            const int lo = el.heads.front().step, hi = el.heads.back().step;
            return el.stemUp ? yOfStep (sy, s, hi) - 3.5f * S : yOfStep (sy, s, lo) + 3.5f * S;
        };
        auto& first = M.v[bm.voice][(size_t) bm.idx.front()];
        auto& last  = M.v[bm.voice][(size_t) bm.idx.back()];
        const float x0 = stemXFor (first), x1 = stemXFor (last);
        float y0 = naturalTip (first), y1 = naturalTip (last);
        // the beam must clear EVERY tip; clamp slant to one staff-space
        float slant = juce::jlimit (-1.0f * S, 1.0f * S, y1 - y0);
        y1 = y0 + slant;
        for (int i : bm.idx)
        {
            auto& el = M.v[bm.voice][(size_t) i];
            const float xi = stemXFor (el);
            const float lineY = x1 > x0 ? y0 + (y1 - y0) * (xi - x0) / (x1 - x0) : y0;
            const float need = naturalTip (el);
            if (el.stemUp ? need < lineY : need > lineY) y0 += need - lineY, y1 += need - lineY;
        }
        const float t = x1 > x0 ? (stemX - x0) / (x1 - x0) : 0.0f;
        return y0 + (y1 - y0) * juce::jlimit (0.0f, 1.0f, t);
    }

    void paintBeam (juce::Graphics& g, int sy, int s, int mi, const score::Measure::Beam& bm)
    {
        auto& M = model.staves[(size_t) s].measures[(size_t) mi];
        if (bm.idx.size() < 2) return;
        auto& G = measGeo[(size_t) mi];
        const float S = staffSpace, headW = 1.25f * S;
        auto stemXFor = [&] (const score::Element& el)
        {
            const int ci = colIndex (G, el.start);
            const float x = ci >= 0 ? G.colX[(size_t) ci] : G.x0;
            return el.stemUp ? x + headW - 0.6f : x + 0.6f;
        };
        auto& first = M.v[bm.voice][(size_t) bm.idx.front()];
        const bool up = first.stemUp;
        const float x0 = stemXFor (first), x1 = stemXFor (M.v[bm.voice][(size_t) bm.idx.back()]);
        const float yA = beamTipY (sy, s, mi, first, x0),
                    yB = beamTipY (sy, s, mi, M.v[bm.voice][(size_t) bm.idx.back()], x1);
        auto yAt = [&] (float x) { return x1 > x0 ? yA + (yB - yA) * (x - x0) / (x1 - x0) : yA; };
        g.setColour (pal().ink.withAlpha (0.92f));
        auto beamSeg = [&] (float xa, float xb, int level)
        {
            const float off = (up ? 1.0f : -1.0f) * level * 0.72f * S;
            juce::Path p;
            p.startNewSubPath (xa, yAt (xa) + off);
            p.lineTo (xb, yAt (xb) + off);
            p.lineTo (xb, yAt (xb) + off + (up ? 0.5f : -0.5f) * S);
            p.lineTo (xa, yAt (xa) + off + (up ? 0.5f : -0.5f) * S);
            p.closeSubPath();
            g.fillPath (p);
        };
        beamSeg (x0, x1, 0);                                     // primary
        auto levelOf = [] (int denom) { return denom >= 32 ? 3 : denom >= 16 ? 2 : 1; };
        for (int lvl = 2; lvl <= 3; ++lvl)
        {
            for (size_t i = 0; i + 1 < bm.idx.size(); ++i)
            {
                auto& a = M.v[bm.voice][(size_t) bm.idx[i]];
                auto& b = M.v[bm.voice][(size_t) bm.idx[i + 1]];
                if (levelOf (a.denom) >= lvl && levelOf (b.denom) >= lvl)
                    beamSeg (stemXFor (a), stemXFor (b), lvl - 1);
                else if (levelOf (a.denom) >= lvl && (i == 0 || levelOf (M.v[bm.voice][(size_t) bm.idx[i - 1]].denom) < lvl))
                    beamSeg (stemXFor (a), stemXFor (a) + 1.1f * S, lvl - 1);       // right hook
                else if (levelOf (b.denom) >= lvl && i + 2 >= bm.idx.size())
                    beamSeg (stemXFor (b) - 1.1f * S, stemXFor (b), lvl - 1);       // left hook
            }
        }
        if (first.triplet && bravura() != nullptr)
            drawGlyph (g, smufl::tuplet3, (x0 + x1) * 0.5f - 0.4f * S,
                       yAt ((x0 + x1) * 0.5f) + (up ? -0.7f : 2.0f) * S, S * 0.8f);
    }

    void paintTiesFor (juce::Graphics& g, int sy)
    {
        auto& sys = systems[(size_t) sy];
        const float S = staffSpace, headW = 1.25f * S;
        g.setColour (pal().ink.withAlpha (0.75f));
        for (auto& t : ties)
        {
            if (t.mFrom < sys.m0 || t.mFrom >= sys.m0 + sys.count) continue;
            auto& stM = model.staves[(size_t) t.staff];
            auto& eA = stM.measures[(size_t) t.mFrom].v[t.vFrom][(size_t) t.eFrom];
            auto& eB = stM.measures[(size_t) t.mTo].v[t.vFrom][(size_t) t.eTo];
            auto& GA = measGeo[(size_t) t.mFrom];
            auto& GB = measGeo[(size_t) t.mTo];
            const int ca = colIndex (GA, eA.start), cb = colIndex (GB, eB.start);
            if (ca < 0 || cb < 0) continue;
            const bool wraps = GB.sys != GA.sys;
            const float xa = GA.colX[(size_t) ca] + headW + 0.2f * S;
            const float xb = wraps ? GA.endX - 0.3f * S : GB.colX[(size_t) cb] - 0.35f * S;
            for (auto& hA : eA.heads)
            {
                bool matched = false;
                for (auto& hB : eB.heads) matched |= hB.step == hA.step;
                if (! matched && ! wraps) continue;
                const float y = yOfStep (sy, t.staff, hA.step) + (eA.stemUp ? 0.85f * S : -0.85f * S);
                const float lift = eA.stemUp ? 0.8f * S : -0.8f * S;
                juce::Path p;
                p.startNewSubPath (xa, y);
                p.quadraticTo ((xa + xb) * 0.5f, y + lift, juce::jmax (xb, xa + 1.5f * S), y);
                g.strokePath (p, juce::PathStrokeType (1.2f));
            }
        }
    }

    void paintPlayhead (juce::Graphics& g, int sy)
    {
        const double ph = getPlayheadBeats ? getPlayheadBeats() : -1.0;
        if (ph < 0) return;
        const int mi = measureAtBeat (ph);
        auto& sys = systems[(size_t) sy];
        if (mi < sys.m0 || mi >= sys.m0 + sys.count) return;
        const float x = beatToX (mi, ph - measStartBeat (mi));
        const float y0 = sys.staffTop.front() - 1.5f * staffSpace;
        const float y1 = sys.staffTop.back() + 5.5f * staffSpace;
        g.setColour (theme::accent.withAlpha (0.16f));
        g.fillRect (juce::Rectangle<float> (x - 2.5f, y0, 5.0f, y1 - y0));
        g.setColour (theme::accent.withAlpha (0.85f));
        g.fillRect (juce::Rectangle<float> (x - 0.6f, y0, 1.2f, y1 - y0));
    }

    //-------------------------------------------------- beat <-> x
    double measStartBeat (int mi) const
    {
        if (model.staves.empty()) return 0;
        return model.staves.front().measures[(size_t) juce::jlimit (0, (int) model.staves.front().measures.size() - 1, mi)].startBeat;
    }
    double measBeats (int mi) const
    {
        if (model.staves.empty()) return 4;
        return model.staves.front().measures[(size_t) juce::jlimit (0, (int) model.staves.front().measures.size() - 1, mi)].beats;
    }
    int measureAtBeat (double beat) const
    {
        int lo = 0;
        for (int i = 0; i < model.numMeasures; ++i)
            if (measStartBeat (i) <= beat + 1e-6) lo = i; else break;
        return lo;
    }
    float beatToX (int mi, double local) const
    {
        auto& G = measGeo[(size_t) juce::jlimit (0, (int) measGeo.size() - 1, mi)];
        if (G.colBeats.empty()) return G.x0;
        for (size_t i = 0; i < G.colBeats.size(); ++i)
        {
            const double b0 = G.colBeats[i];
            const double b1 = i + 1 < G.colBeats.size() ? G.colBeats[i + 1] : measBeats (mi);
            if (local <= b0 + 1e-9) return G.colX[i];
            if (local < b1 - 1e-9)
            {
                const float x1 = i + 1 < G.colX.size() ? G.colX[i + 1] : G.endX - staffSpace;
                return G.colX[i] + (float) ((local - b0) / juce::jmax (1e-9, b1 - b0)) * (x1 - G.colX[i]);
            }
        }
        return G.endX - staffSpace;
    }
    double xToBeat (int mi, float x) const
    {
        auto& G = measGeo[(size_t) juce::jlimit (0, (int) measGeo.size() - 1, mi)];
        if (G.colBeats.empty()) return measStartBeat (mi);
        for (size_t i = 0; i < G.colBeats.size(); ++i)
        {
            const float x0 = G.colX[i];
            const float x1 = i + 1 < G.colX.size() ? G.colX[i + 1] : G.endX - staffSpace;
            const double b0 = G.colBeats[i];
            const double b1 = i + 1 < G.colBeats.size() ? G.colBeats[i + 1] : measBeats (mi);
            if (x <= x0) return measStartBeat (mi) + b0;
            if (x < x1) return measStartBeat (mi) + b0 + (double) ((x - x0) / juce::jmax (1.0f, x1 - x0)) * (b1 - b0);
        }
        return measStartBeat (mi) + measBeats (mi) - 1e-6;
    }
    float pxPerBeatAt (const score::SrcRef&) const
    {
        return juce::jmax (12.0f, staffSpace * 6.0f);          // stable drag feel across zooms
    }

    //-------------------------------------------------- edits
    juce::String key (const score::SrcRef& s) const { return juce::String (s.track) + ":" + juce::String (s.note); }
    SongNote* noteFor (const score::SrcRef& s)
    {
        if (song == nullptr || s.track < 0 || s.track >= (int) song->tracks.size()) return nullptr;
        auto& t = song->tracks[(size_t) s.track];
        if (t.locked || s.note < 0 || s.note >= (int) t.notes.size()) return nullptr;
        return &t.notes[(size_t) s.note];
    }
    bool trackIsDrum (int ti) const
    {
        if (song == nullptr || ti < 0 || ti >= (int) song->tracks.size()) return false;
        return score::roleForTrack (song->tracks[(size_t) ti]) != score::DrumRole::None;
    }
    int pitchAtStepDelta (int pitch, int stepDelta) const
    {
        auto sp = score::spellPitch (pitch, model.key);
        const int abs = sp.absStep + stepDelta;
        const int letter = ((abs % 7) + 7) % 7;
        const int oct = (abs - letter) / 7;
        return juce::jlimit (0, 127, oct * 12 + score::naturalPc (letter) + score::keyAlter (model.key, letter));
    }
    double insertGrid() const
    {
        double d = 4.0 / insertDenom;
        if (insertDot) d *= 1.5;
        if (insertTrip) d *= 2.0 / 3.0;
        return juce::jlimit (1.0 / 12.0, 6.0, d);
    }
    void auditionBlip (int track, int pitch, float vel)
    {
        if (onAudition == nullptr) return;
        if (audOn && onAuditionOff) onAuditionOff();
        onAudition (track, pitch, vel);
        audOn = true;
    }
    void noteEdited (bool gestureEnd)
    {
        dirty = true;
        if (gestureEnd && onChanged) onChanged();
        repaint();
    }
    void deleteNote (const score::SrcRef& s)
    {
        if (onSnapshot) onSnapshot();
        deleteNotes ({ s });
    }
    void deleteNotes (std::vector<score::SrcRef> refs)
    {
        if (song == nullptr) return;
        std::sort (refs.begin(), refs.end(), [] (auto& a, auto& b)
                   { return a.track < b.track || (a.track == b.track && a.note > b.note); });
        for (auto& r : refs)
            if (r.track >= 0 && r.track < (int) song->tracks.size()
                && ! song->tracks[(size_t) r.track].locked
                && r.note >= 0 && r.note < (int) song->tracks[(size_t) r.track].notes.size())
                song->tracks[(size_t) r.track].notes.erase (
                    song->tracks[(size_t) r.track].notes.begin() + r.note);
        selection.clear();
        mirrorSelection();
        noteEdited (true);
    }
    //---- insert resolution: ONE truth for hover ghost, dbl-click insert, click-seek
    InsPoint resolveInsert (juce::Point<float> scPos) const
    {
        InsPoint ip;
        if (song == nullptr || systems.empty()) return ip;
        int sysIdx = -1;
        for (int i = 0; i < (int) systems.size(); ++i)
            if (scPos.y >= systems[(size_t) i].y0 - 14
                && scPos.y <= systems[(size_t) i].y0 + systems[(size_t) i].h + 14)
            { sysIdx = i; break; }
        if (sysIdx < 0) return ip;
        auto& sys = systems[(size_t) sysIdx];
        int staffIdx = 0; float best = 1e9f;
        for (int s = 0; s < (int) sys.staffTop.size(); ++s)
        {
            const float mid = sys.staffTop[(size_t) s] + 2 * staffSpace;
            if (std::abs (scPos.y - mid) < best) { best = std::abs (scPos.y - mid); staffIdx = s; }
        }
        int mi = -1;
        for (int i = sys.m0; i < sys.m0 + sys.count; ++i)
            if (scPos.x >= measGeo[(size_t) i].x0 - 6 && scPos.x <= measGeo[(size_t) i].endX)
            { mi = i; break; }
        if (mi < 0 || staffIdx >= (int) model.staves.size()) return ip;
        auto& st = model.staves[(size_t) staffIdx];
        const double grid = insertGrid();
        const double raw = xToBeat (mi, scPos.x);
        const double beat = measStartBeat (mi)
                            + std::round ((raw - measStartBeat (mi)) / grid) * grid;
        const int step = (int) std::round (8.0f - (scPos.y - sys.staffTop[(size_t) staffIdx])
                                                    / (staffSpace * 0.5f));
        ip.sys = sysIdx; ip.staff = staffIdx; ip.mi = mi;
        ip.rawBeat = raw;
        ip.beat = juce::jmax (0.0, beat);
        ip.step = step;
        if (st.isDrums)
        {
            int bestT = -1, bestD = 1000;
            for (int ti : st.mergedTracks)
            {
                const int d = std::abs (score::drumStep (
                    score::roleForTrack (song->tracks[(size_t) ti])) - step);
                if (d < bestD) { bestD = d; bestT = ti; }
            }
            ip.track = bestT;
            if (bestT >= 0)
            {
                ip.pitch = song->tracks[(size_t) bestT].notes.empty() ? 36
                             : song->tracks[(size_t) bestT].notes.front().pitch;
                ip.label = song->tracks[(size_t) bestT].name;
                ip.step = score::drumStep (score::roleForTrack (song->tracks[(size_t) bestT]));
            }
        }
        else
        {
            const int absStep = step + (st.clef == score::Clef::Bass ? 18 : 30);
            const int letter = ((absStep % 7) + 7) % 7;
            ip.pitch = juce::jlimit (0, 127, ((absStep - letter) / 7) * 12
                                              + score::naturalPc (letter)
                                              + score::keyAlter (model.key, letter));
            ip.track = st.trackIdx;
            ip.label = noteName (ip.pitch);
        }
        ip.valid = ip.track >= 0 && ip.track < (int) song->tracks.size()
                   && ! song->tracks[(size_t) ip.track].locked;
        return ip;
    }

    score::SrcRef insertNote (int track, double startBeat, double len, int pitch, double vel)
    {
        if (song == nullptr || track < 0 || track >= (int) song->tracks.size()
            || song->tracks[(size_t) track].locked)
            return {};
        SongNote n;
        n.start = juce::jmax (0.0, startBeat);
        n.len = len;
        n.pitch = juce::jlimit (0, 127, pitch);
        n.vel = vel;
        song->tracks[(size_t) track].notes.push_back (n);
        return { track, (int) song->tracks[(size_t) track].notes.size() - 1 };
    }

    void insertAt (juce::Point<float> scPos)      // model-space position
    {
        const auto ip = resolveInsert (scPos);
        if (! ip.valid) return;
        if (onSnapshot) onSnapshot();
        const auto ref = insertNote (ip.track, ip.beat, insertGrid(), ip.pitch, 0.85);
        if (ref.note < 0) return;
        if (! trackIsDrum (ip.track)) { stepTrackIdx = ip.track; lastStepPitch = ip.pitch; }
        selection.clear();
        selection[key (ref)] = ref;
        mirrorSelection();
        auditionBlip (ip.track, ip.pitch, 0.85f);
        juce::Timer::callAfterDelay (220, [this] { if (audOn) { audOn = false; if (onAuditionOff) onAuditionOff(); } });
        noteEdited (true);
    }

    //---- selection verbs (the score is a first-class editor: copy travels tracks)
    void selectAll()
    {
        if (song == nullptr) return;
        selection.clear();
        for (auto& st : model.staves)
        {
            const auto ts = st.mergedTracks.empty() ? std::vector<int> { st.trackIdx }
                                                    : st.mergedTracks;
            for (int t : ts)
                if (t >= 0 && t < (int) song->tracks.size())
                    for (int n = 0; n < (int) song->tracks[(size_t) t].notes.size(); ++n)
                        selection[key ({ t, n })] = { t, n };
        }
        mirrorSelection(); repaint();
    }
    void selectStaffNotes (int staffIdx)
    {
        if (song == nullptr || staffIdx < 0 || staffIdx >= (int) model.staves.size()) return;
        auto& st = model.staves[(size_t) staffIdx];
        selection.clear();
        const auto ts = st.mergedTracks.empty() ? std::vector<int> { st.trackIdx }
                                                : st.mergedTracks;
        for (int t : ts)
            if (t >= 0 && t < (int) song->tracks.size())
                for (int n = 0; n < (int) song->tracks[(size_t) t].notes.size(); ++n)
                    selection[key ({ t, n })] = { t, n };
        if (! st.isDrums && st.trackIdx >= 0) stepTrackIdx = st.trackIdx;
        mirrorSelection(); repaint();
    }
    void deleteSelection()
    {
        if (selection.empty()) return;
        if (onSnapshot) onSnapshot();
        std::vector<score::SrcRef> refs;
        for (auto& [k2, sr] : selection) { juce::ignoreUnused (k2); refs.push_back (sr); }
        deleteNotes (refs);
    }
    void copySelection()
    {
        if (song == nullptr || selection.empty()) return;
        clipNotes.clear();
        double anchor = 1e18, end = 0;
        for (auto& [k2, sr] : selection)
        { juce::ignoreUnused (k2); if (auto* n = noteFor (sr)) anchor = juce::jmin (anchor, n->start); }
        if (anchor > 1e17) return;
        for (auto& [k2, sr] : selection)
        {
            juce::ignoreUnused (k2);
            if (auto* n = noteFor (sr))
            {
                clipNotes.push_back ({ sr.track, n->start - anchor, n->len, n->vel, n->pitch });
                end = juce::jmax (end, n->start - anchor + n->len);
            }
        }
        clipAnchor = anchor;
        const double grid = insertGrid();
        clipSpan = juce::jmax (grid, std::ceil (end / grid - 1e-9) * grid);
    }
    void pasteNotesAt (double target)
    {
        if (song == nullptr || clipNotes.empty()) return;
        if (onSnapshot) onSnapshot();
        selection.clear();
        for (auto& c : clipNotes)
        {
            const auto ref = insertNote (c.track, target + c.d, c.len, c.pitch, c.vel);
            if (ref.note >= 0) selection[key (ref)] = ref;
        }
        mirrorSelection();
        noteEdited (true);
    }
    void pasteClipboard()
    {
        if (clipNotes.empty()) return;
        const double ph = getPlayheadBeats ? getPlayheadBeats() : -1.0;
        const double grid = insertGrid();
        const double target = stepMode ? stepCaret : (ph >= 0 ? ph : clipAnchor);
        pasteNotesAt (juce::jmax (0.0, std::round (target / grid) * grid));
    }
    void duplicateSelection()
    {
        if (selection.empty()) return;
        copySelection();
        if (! clipNotes.empty()) pasteNotesAt (clipAnchor + clipSpan);
    }

    //---- step entry: the caret is a pen (N, then A-G letters land at it)
    void toggleStepMode()
    {
        if (stepMode) { stepMode = false; repaint(); return; }
        if (song == nullptr) return;
        if (stepTrackIdx < 0 || stepTrackIdx >= (int) song->tracks.size()
            || trackIsDrum (stepTrackIdx))
        {
            stepTrackIdx = -1;
            for (auto& st : model.staves)
                if (! st.isDrums && st.trackIdx >= 0) { stepTrackIdx = st.trackIdx; break; }
        }
        if (stepTrackIdx < 0) return;                // nothing melodic to write on
        const double ph = getPlayheadBeats ? getPlayheadBeats() : -1.0;
        const double grid = insertGrid();
        stepCaret = ph >= 0 ? std::round (ph / grid) * grid : 0.0;
        stepMode = true;
        scrollToBeat (stepCaret);
        repaint();
    }
    int pitchForLetter (int azIdx) const             // 0='A'..6='G', spelled through the key
    {
        static const int letterOf[7] = { 5, 6, 0, 1, 2, 3, 4 };
        const int letter = letterOf[juce::jlimit (0, 6, azIdx)];
        const int pc = ((score::naturalPc (letter) + score::keyAlter (model.key, letter)) % 12 + 12) % 12;
        const int ref = lastStepPitch >= 0 ? lastStepPitch : 60;
        int bestP = 60, bd = 999;
        for (int oct = 0; oct <= 10; ++oct)
        {
            const int cand = oct * 12 + pc;
            if (cand > 127) break;
            if (std::abs (cand - ref) < bd) { bd = std::abs (cand - ref); bestP = cand; }
        }
        return bestP;
    }
    void stepInsertLetter (int azIdx)
    {
        if (! stepMode || stepTrackIdx < 0) return;
        if (onSnapshot) onSnapshot();
        const double grid = insertGrid();
        const int pitch = pitchForLetter (azIdx);
        const auto ref = insertNote (stepTrackIdx, stepCaret, grid, pitch, 0.85);
        if (ref.note < 0) return;
        lastStepPitch = pitch;
        stepCaret += grid;
        selection.clear(); selection[key (ref)] = ref;
        mirrorSelection();
        auditionBlip (stepTrackIdx, pitch, 0.85f);
        juce::Timer::callAfterDelay (200, [this] { if (audOn) { audOn = false; if (onAuditionOff) onAuditionOff(); } });
        scrollToBeat (stepCaret);
        noteEdited (true);
    }

    //---- staff rails: focus + flags
    void toggleFocus (int staffIdx)
    {
        if (staffIdx < 0 || staffIdx >= (int) model.staves.size()) return;
        auto& st = model.staves[(size_t) staffIdx];
        const int fkey = st.trackIdx >= 0 ? st.trackIdx : -1;
        if (focusStaff == fkey) { focusStaff = -2; scopeTrack = -1; }
        else
        {
            focusStaff = fkey;
            scopeTrack = st.trackIdx >= 0 ? st.trackIdx
                         : (st.mergedTracks.empty() ? -1 : st.mergedTracks.front());
        }
        dirty = true;
        repaint();
    }
    void toggleStaffFlag (int staffIdx, bool muteFlag)
    {
        if (song == nullptr || staffIdx < 0 || staffIdx >= (int) model.staves.size()) return;
        auto& st = model.staves[(size_t) staffIdx];
        const auto ts = st.mergedTracks.empty() ? std::vector<int> { st.trackIdx }
                                                : st.mergedTracks;
        if (muteFlag)
        {
            if (! onSetMute) return;
            const bool target = ! staffMuted (st);
            for (int t : ts) if (t >= 0) onSetMute (t, target);
        }
        else
        {
            if (! onSetSolo) return;
            const bool target = ! staffSoloed (st);
            for (int t : ts) if (t >= 0) onSetSolo (t, target);
        }
        repaint();
    }

    //---- view verbs
    void scrollToBeat (double gBeat)
    {
        if (systems.empty() || measGeo.empty()) return;
        const int mi = juce::jlimit (0, (int) measGeo.size() - 1, measureAtBeat (gBeat));
        auto& sys = systems[(size_t) measGeo[(size_t) mi].sys];
        const double top = sys.y0 - viewY;
        if (top < 40.0 || top + sys.h > (double) getHeight() - 40.0)
        {
            viewY = juce::jlimit (0.0, juce::jmax (0.0, totalH - 34.0 - (double) viewH()),
                                  sys.y0 - 34.0 - (double) viewH() * 0.22);
            vScroll.setCurrentRange (viewY, viewH(), juce::dontSendNotification);
        }
    }
    void setScaleAnchored (float s, float anchorScreenY)
    {
        const float o = staffSpace;
        const float ns = juce::jlimit (3.2f, 10.0f, s);
        if (std::abs (ns - o) < 1e-4f) return;
        const double kk = (double) ns / (double) o;
        viewY = juce::jmax (0.0, (viewY + (double) anchorScreenY) * kk - (double) anchorScreenY);
        staffSpace = ns;
        dirty = true;
        savePrefs();
        repaint();
    }

    //---- SCORE II screen furniture (all screen-space, painted after the world)
    juce::String describeNote (const score::SrcRef& sr)
    {
        auto* n = noteFor (sr);
        if (n == nullptr || song == nullptr) return {};
        const auto& t = song->tracks[(size_t) sr.track];
        const auto pname = trackIsDrum (sr.track) ? t.name : noteName (n->pitch);
        return pname + "  -  " + posLabel (n->start) + "  -  len " + fnum (n->len)
             + "b  -  vel " + juce::String ((int) std::round (n->vel * 127.0))
             + "  -  " + t.name;
    }
    void paintReadout (juce::Graphics& g)
    {
        auto r = getLocalBounds().removeFromBottom (22);
        g.setColour (theme::panel.withAlpha (0.92f));
        g.fillRect (r);
        g.setColour (theme::line);
        g.fillRect (r.withHeight (1));
        juce::String left;
        if (! selection.empty())
        {
            left = describeNote (selection.begin()->second);
            if (selection.size() > 1)
                left = juce::String ((int) selection.size()) + " notes  -  " + left;
        }
        else if (hoverKey.isNotEmpty() && hoverSrc.track >= 0)
            left = describeNote (hoverSrc);
        else if (hoverIns.valid)
            left = "add here: " + hoverIns.label + "  -  " + posLabel (hoverIns.beat)
                 + "  -  1/" + juce::String (insertDenom) + (insertDot ? "." : "")
                 + (insertTrip ? " triplet" : "");
        else if (stepMode && song != nullptr)
            left = "STEP at " + posLabel (stepCaret) + "  -  "
                 + (stepTrackIdx >= 0 && stepTrackIdx < (int) song->tracks.size()
                        ? song->tracks[(size_t) stepTrackIdx].name : juce::String ("?"));
        else if (song != nullptr)
            left = juce::String ((int) model.staves.size()) + " staves  -  "
                 + juce::String (model.numMeasures) + " bars  -  " + model.key.label;
        g.setColour (theme::textDim);
        g.setFont (theme::ui (10.0f));
        g.drawText (left, r.reduced (10, 0).withTrimmedRight (r.getWidth() / 2),
                    juce::Justification::centredLeft);
        juce::String hint;
        if (ghosting)      hint = "TAKE ON THE STAND - read-only - verdict in the deck - click = seek";
        else if (stepMode) hint = "A-G add - R rest - 1-6 length - . dot - t triplet - Backspace - Esc";
        else if (! selection.empty())
                           hint = "drag move - Alt chromatic - Shift vel - Ctrl octave - Ctrl C/X/V/D - Del";
        else               hint = "dbl-click add - drag select - click seek - N step - ? keys";
        g.setColour (theme::textMute);
        g.setFont (theme::caps (7.0f));
        g.drawText (hint, r.reduced (10, 0), juce::Justification::centredRight);
    }
    void paintHoverPreview (juce::Graphics& g)   // translated (model) space
    {
        if (! hoverIns.valid || hoverKey.isNotEmpty() || ghosting || stepMode || showHelp
            || gesture.active || gesture.marquee || printing)
            return;
        const float S = staffSpace, headW = 1.25f * S;
        const float x = beatToX (hoverIns.mi, hoverIns.beat - measStartBeat (hoverIns.mi));
        const float y = yOfStep (hoverIns.sys, hoverIns.staff, hoverIns.step);
        g.setColour (pal().accent.withAlpha (0.28f));
        for (int L = 10; L <= hoverIns.step; L += 2)
            g.fillRect (juce::Rectangle<float> (x - 0.45f * S,
                yOfStep (hoverIns.sys, hoverIns.staff, L) - 0.5f, headW + 0.9f * S, 1.0f));
        for (int L = -2; L >= hoverIns.step; L -= 2)
            g.fillRect (juce::Rectangle<float> (x - 0.45f * S,
                yOfStep (hoverIns.sys, hoverIns.staff, L) - 0.5f, headW + 0.9f * S, 1.0f));
        g.setColour (pal().accent.withAlpha (0.42f));
        if (bravura() != nullptr)
            drawGlyph (g, insertDenom >= 4 ? smufl::headBlack
                          : insertDenom == 2 ? smufl::headHalf : smufl::headWhole, x, y, S);
        else
            g.fillEllipse (x, y - 0.62f * S, headW, 1.24f * S);
    }
    void paintStepCaret (juce::Graphics& g)      // translated (model) space
    {
        if (! stepMode || printing || measGeo.empty() || systems.empty()) return;
        const float S = staffSpace;
        const int mi = juce::jlimit (0, (int) measGeo.size() - 1, measureAtBeat (stepCaret));
        const int si = staffIndexForTrack (stepTrackIdx);
        auto& sys = systems[(size_t) measGeo[(size_t) mi].sys];
        if (si >= (int) sys.staffTop.size()) return;
        const float x = beatToX (mi, stepCaret - measStartBeat (mi));
        const float ty = sys.staffTop[(size_t) si] - 1.4f * S;
        const float by = sys.staffTop[(size_t) si] + 5.4f * S;
        g.setColour (pal().accent.withAlpha (0.85f));
        const float dash[2] = { 4.0f, 3.0f };
        g.drawDashedLine (juce::Line<float> (x, ty, x, by), dash, 2, 1.6f);
        juce::Rectangle<float> flag (x + 3.0f, ty - 13.0f, 40.0f, 12.0f);
        g.setColour (pal().accent.withAlpha (0.18f));
        g.fillRoundedRectangle (flag, 3.0f);
        g.setColour (pal().accent);
        g.setFont (theme::caps (6.5f));
        g.drawText ("STEP", flag.toNearestInt(), juce::Justification::centred);
    }
    void paintPill (juce::Graphics& g)           // screen space: AI verbs ON the selection
    {
        pillChips.clear();
        if (selection.empty() || ghosting || stepMode || printing || showHelp) return;
        juce::Rectangle<float> bbox;
        for (auto& h : hits)
            if (selection.count (key (h.src)) > 0)
            {
                const auto sr2 = h.r.translated (0.0f, (float) -viewY);
                bbox = bbox.isEmpty() ? sr2 : bbox.getUnion (sr2);
            }
        if (bbox.isEmpty() || bbox.getBottom() < 34.0f
            || bbox.getY() > (float) getHeight() - 22.0f)
            return;
        struct Verb { const char* label; const char* prompt; };
        static const Verb mel[] = {
            { "HARMONIZE", "Harmonize the selected notes: add chord-tone harmony under the "
                           "selected melody on the same track. Keep every selected note exactly as written." },
            { "COUNTER",   "Write a counter-melody that answers the selected phrase, on a NEW track "
                           "in a complementary register. Do not change the selected notes." },
            { "VARY",      "Recompose the selected notes as a variation: keep the harmony and groove "
                           "skeleton, refresh the contour and rhythm, land in the same bars on the same track." },
            { "CONTINUE",  "Continue the music from the end of the selection for 8 bars in the same "
                           "style, developing the selected motif. Do not change existing notes." } };
        static const Verb drm[] = {
            { "VARY",    "Vary the selected drum bars: same pulse, new detail - ghost notes, hat "
                         "variation, small displacements. Keep the kick anchors." },
            { "FILL",    "Write a drum fill in the last bar of the selection that leads into what "
                         "follows. Keep everything else as written." },
            { "COUNTER", "Add a counter-rhythm percussion line against the selected drums on a NEW "
                         "track: a complementary subdivision that locks with the groove." } };
        const bool drums = trackIsDrum (selection.begin()->second.track);
        const Verb* verbs = drums ? drm : mel;
        const int nv = drums ? 3 : 4;
        float total = 8.0f;
        for (int i = 0; i < nv; ++i) total += textW (theme::caps (7.5f), verbs[i].label) + 18.0f;
        float px = juce::jlimit (8.0f, juce::jmax (8.0f, (float) getWidth() - total - 18.0f),
                                 bbox.getCentreX() - total * 0.5f);
        float py = bbox.getY() - 34.0f;
        if (py < 40.0f) py = juce::jmin ((float) getHeight() - 50.0f, bbox.getBottom() + 8.0f);
        juce::Rectangle<float> pill (px, py, total + 8.0f, 26.0f);
        g.setColour (theme::panel.withAlpha (0.94f));
        g.fillRoundedRectangle (pill, 13.0f);
        g.setColour (theme::accent.withAlpha (0.45f));
        g.drawRoundedRectangle (pill, 13.0f, 1.0f);
        float cx = px + 8.0f;
        for (int i = 0; i < nv; ++i)
        {
            const float w = textW (theme::caps (7.5f), verbs[i].label) + 14.0f;
            juce::Rectangle<float> cr (cx, py + 4.0f, w, 18.0f);
            g.setColour (theme::accent.withAlpha (0.14f));
            g.fillRoundedRectangle (cr, 9.0f);
            g.setColour (theme::text);
            g.setFont (theme::caps (7.5f));
            g.drawText (verbs[i].label, cr.toNearestInt(), juce::Justification::centred);
            pillChips.push_back ({ cr, verbs[i].label, verbs[i].prompt });
            cx += w + 4.0f;
        }
    }
    void paintHoverBubble (juce::Graphics& g)    // screen space
    {
        if (! hoverIns.valid || hoverKey.isNotEmpty() || ghosting || stepMode || showHelp
            || gesture.active || gesture.marquee || hoverIns.label.isEmpty())
            return;
        g.setFont (theme::mono (9.0f));
        const float w = textW (theme::mono (9.0f), hoverIns.label) + 14.0f;
        juce::Rectangle<float> b (hoverScreen.x + 16.0f, hoverScreen.y - 24.0f, w, 17.0f);
        b = b.constrainedWithin (getLocalBounds().toFloat().reduced (4.0f));
        g.setColour (theme::panel.withAlpha (0.95f));
        g.fillRoundedRectangle (b, 4.0f);
        g.setColour (theme::accent.withAlpha (0.5f));
        g.drawRoundedRectangle (b, 4.0f, 1.0f);
        g.setColour (theme::text);
        g.drawText (hoverIns.label, b.toNearestInt(), juce::Justification::centred);
    }
    void paintHelp (juce::Graphics& g)           // screen space: the gesture card
    {
        if (! showHelp) return;
        const auto full = getLocalBounds().toFloat();
        g.setColour (juce::Colours::black.withAlpha (0.55f));
        g.fillRect (full);
        juce::Rectangle<float> card (0, 0, 680.0f, 356.0f);
        card = card.withCentre (full.getCentre());
        const auto ink2 = pal().ink;                       // the card wears the page's theme
        g.setColour (pal().paper);
        g.fillRoundedRectangle (card, 10.0f);
        g.setColour (pal().paperLine);
        g.drawRoundedRectangle (card, 10.0f, 1.2f);
        g.setColour (ink2);
        g.setFont (theme::ui (14.0f, juce::Font::bold));
        g.drawText ("THE SCORE - keys and hands",
                    juce::Rectangle<int> ((int) card.getX() + 24, (int) card.getY() + 14, 400, 20),
                    juce::Justification::left);
        static const char* rows[][2] = {
            { "click note",      "select (Ctrl adds) - it sounds" },
            { "drag",            "move / transpose (Alt = chromatic)" },
            { "right-edge drag", "length" },
            { "dbl-click",       "insert note (kit staff: nearest role)" },
            { "right-click",     "delete" },
            { "drag empty",      "select many" },
            { "click empty",     "seek the transport" },
            { "wheel",           "scroll - Ctrl+wheel = zoom" },
            { "Up/Down",         "step - Alt semi - Ctrl oct - Shift vel" },
            { "Left/Right",      "nudge by grid (Alt = length)" },
            { "Ctrl A/C/X/V/D",  "all / copy / cut / paste / duplicate" },
            { "Del",             "delete selection" },
            { "N",               "step entry: A-G, R rest, 1-6 length" },
            { "staff name",      "click = select staff, dbl = FOCUS" },
            { "M / S dots",      "mute / solo the staff's tracks" },
            { "Esc",             "exit step / clear / release focus" } };
        const int n = (int) (sizeof (rows) / sizeof (rows[0]));
        const int perCol = (n + 1) / 2;
        for (int i = 0; i < n; ++i)
        {
            const int colI = i / perCol, rowI = i % perCol;
            const float cx = card.getX() + 24.0f + (float) colI * 322.0f;
            const float cy = card.getY() + 52.0f + (float) rowI * 19.0f;
            g.setColour (ink2.withAlpha (0.95f));
            g.setFont (theme::mono (9.0f));
            g.drawText (rows[i][0], (int) cx, (int) cy, 118, 15, juce::Justification::left);
            g.setColour (ink2.withAlpha (0.65f));
            g.setFont (theme::ui (10.0f));
            g.drawText (rows[i][1], (int) cx + 122, (int) cy, 196, 15, juce::Justification::left);
        }
        g.setColour (ink2.withAlpha (0.5f));
        g.setFont (theme::caps (7.0f));
        g.drawText ("any click or key closes this card",
                    juce::Rectangle<int> ((int) card.getX(), (int) card.getBottom() - 26,
                                          (int) card.getWidth(), 14),
                    juce::Justification::centred);
    }

public:
    //---- THE PRINT DOOR: engrave A4 pages, write a real PDF (ScorePdf.h)
    bool exportPdf (const juce::File& out)
    {
        if (song == nullptr) return false;
        const float saveS = staffSpace;
        const double saveView = viewY;
        printing = true;
        printW = 1190;                              // A4 @ 2x (595.28pt wide)
        staffSpace = juce::jlimit (3.4f, 5.2f, saveS);
        dirty = true;
        rebuildIfNeeded();
        bool ok = false;
        if (! systems.empty())
        {
            const int pageH = 1684, margin = 100;
            const int availH = pageH - 2 * margin;
            std::vector<std::pair<int, int>> plan;   // [s0, s1)
            {
                int s0 = 0;
                float used = 96.0f;                  // title band opens page 1
                for (int sy = 0; sy < (int) systems.size(); ++sy)
                {
                    const float h = systems[(size_t) sy].h + 3.6f * staffSpace;
                    if (sy > s0 && used + h > (float) availH)
                    { plan.push_back ({ s0, sy }); s0 = sy; used = 0.0f; }
                    used += h;
                }
                plan.push_back ({ s0, (int) systems.size() });
            }
            std::vector<juce::Image> pages;
            for (size_t p = 0; p < plan.size(); ++p)
            {
                juce::Image img (juce::Image::RGB, 1190, pageH, true);
                juce::Graphics pg (img);
                pg.fillAll (pal().paper);
                float yCur = (float) margin;
                if (p == 0) { paintTitle (pg, yCur + 4.0f); yCur += 96.0f; }
                for (int sy = plan[p].first; sy < plan[p].second; ++sy)
                {
                    pg.saveState();
                    pg.addTransform (juce::AffineTransform::translation (
                        0.0f, yCur - systems[(size_t) sy].y0));
                    paintSystemBlock (pg, sy);
                    pg.restoreState();
                    yCur += systems[(size_t) sy].h + 3.6f * staffSpace;
                }
                pg.setColour (pal().label);
                pg.setFont (theme::caps (8.0f));
                pg.drawText ((getSongName ? getSongName() : juce::String()) + "   -   "
                                 + juce::String ((int) p + 1) + " / "
                                 + juce::String ((int) plan.size()) + "   -   SOTA DAW",
                             juce::Rectangle<int> (0, pageH - 46, 1190, 14),
                             juce::Justification::centred);
                pages.push_back (std::move (img));
            }
            ok = writeScorePdf (pages, out);
        }
        printing = false;
        printW = 0;
        staffSpace = saveS;
        viewY = saveView;
        dirty = true;
        repaint();
        return ok;
    }

private:
    void updateMarquee()
    {
        auto r = juce::Rectangle<float> (gesture.origin, gesture.current)
                    .translated (0, (float) viewY);
        selection.clear();
        for (auto& h : hits)
            if (r.intersects (h.r))
                selection[key (h.src)] = h.src;
        mirrorSelection();
    }
    void mirrorSelection()
    {
        if (onSelectionMirror == nullptr) return;
        std::map<int, std::set<size_t>> m;
        for (auto& [k2, sr] : selection)
        { juce::ignoreUnused (k2); if (sr.track >= 0 && sr.note >= 0) m[sr.track].insert ((size_t) sr.note); }
        onSelectionMirror (m);
    }
    const Hit* hitAt (juce::Point<float> p) const
    {
        const Hit* best = nullptr; float bd = 1e9f;
        for (auto& h : hits)
            if (h.r.expanded (2.0f).contains (p))
            {
                const float d = h.r.getCentre().getDistanceFrom (p);
                if (d < bd) { bd = d; best = &h; }
            }
        return best;
    }

    //-------------------------------------------------- toolbar
    void paintToolbar (juce::Graphics& g)
    {
        auto bar = getLocalBounds().removeFromTop (34);
        g.setColour (theme::panel.withAlpha (0.85f));
        g.fillRect (bar);
        g.setColour (theme::line);
        g.fillRect (bar.removeFromBottom (1));
        chips.clear();
        float x = (float) toolbarArea.getX() + 2.0f;
        auto addChip = [this, &g, &x] (const juce::String& label, int id, bool on, const juce::String& tip,
                                       float w = 0.0f, bool music = false)
        {
            const float cw = w > 0 ? w : textW (theme::caps (8.5f), label) + 16.0f;
            if (x + cw > (float) toolbarArea.getRight() - 4.0f) return;   // degrade CLEANLY:
                                                                          // a chip is whole or absent
            juce::Rectangle<float> r (x, 5.0f, cw, 24.0f);
            g.setColour (on ? theme::accent.withAlpha (0.22f) : theme::panelHi.withAlpha (0.75f));
            g.fillRoundedRectangle (r, 5.0f);
            g.setColour (on ? theme::accent.withAlpha (0.8f) : theme::line);
            g.drawRoundedRectangle (r.reduced (0.5f), 5.0f, 1.0f);
            g.setColour (on ? theme::text : theme::textDim);
            if (music && bravura() != nullptr)
            {
                const float gw = textW (musicFont (4.6f), label);
                juce::GlyphArrangement ga;
                ga.addLineOfText (musicFont (4.6f), label,
                                  r.getCentreX() - gw * 0.5f, r.getCentreY() + 6.0f);
                ga.draw (g);
            }
            else
            {
                g.setFont (theme::caps (8.5f));
                g.drawText (label, r.toNearestInt(), juce::Justification::centred);
            }
            chips.push_back ({ r, label, id, on, tip });
            x += cw + 4.0f;
        };
        // display quantize
        addChip ("AUTO", 100, quant <= 0, "display grid: AUTO (triplet-aware)");
        addChip ("8",  101, std::abs (quant - 0.5) < 1e-9, "display grid: eighths", 24.0f);
        addChip ("16", 102, std::abs (quant - 0.25) < 1e-9, "display grid: sixteenths", 26.0f);
        addChip ("32", 103, std::abs (quant - 0.125) < 1e-9, "display grid: thirty-seconds", 26.0f);
        x += 8.0f;
        // insert palette (real note glyphs read as themselves; keys 1-6 twin them)
        struct DV { juce::juce_wchar mg; const char* lbl; int den; };
        static const DV dv[] = { { smufl::metWhole, "1", 1 }, { smufl::metHalf, "2", 2 },
                                 { smufl::metQuarterUp, "4", 4 }, { smufl::met8, "8", 8 },
                                 { smufl::met16, "16", 16 }, { smufl::met32, "32", 32 } };
        const bool haveF = bravura() != nullptr;
        for (auto& d : dv)
            addChip (haveF ? gl (d.mg) : juce::String (d.lbl), 200 + d.den, insertDenom == d.den,
                     "insert length: 1/" + juce::String (d.den), 26.0f, haveF);
        addChip (".", 300, insertDot, "dotted insert", 22.0f);
        addChip ("3", 301, insertTrip, "triplet insert", 22.0f);
        x += 8.0f;
        // priority order under clamp: THEME before scope/zoom (those have other doors —
        // dbl-click a staff = focus/scope, ctrl+wheel = zoom; the theme has ONLY this chip)
        addChip (paperMode ? "LIGHT" : "DARK", 404, true,
                 "page theme: LIGHT ivory / DARK slate - click flips");
        addChip ("KIT", 400, mergeDrums, "merge drum tracks onto one kit staff");
        addChip ("?", 500, showHelp, "keys and hands", 20.0f);
        addChip (scopeTrack < 0 ? "SONG" : "TRACK", 401, scopeTrack >= 0,
                 "COMPOSE scope: whole song, or the focused staff only");
        addChip ("-", 402, false, "smaller engraving (ctrl+wheel too)", 20.0f);
        addChip ("+", 403, false, "larger engraving (ctrl+wheel too)", 20.0f);
        // (ghost state lives in the title band — a toolbar twin collided with the vibe box)
    }
    void toolbarClick (const juce::MouseEvent& e)
    {
        for (auto& c : chips)
            if (c.r.contains (e.position))
            {
                if (c.id == 100) quant = 0;
                else if (c.id == 101) quant = 0.5;
                else if (c.id == 102) quant = 0.25;
                else if (c.id == 103) quant = 0.125;
                else if (c.id >= 200 && c.id < 300) insertDenom = c.id - 200;
                else if (c.id == 300) insertDot = ! insertDot;
                else if (c.id == 301) insertTrip = ! insertTrip;
                else if (c.id == 400) mergeDrums = ! mergeDrums;
                else if (c.id == 401) cycleScope();
                else if (c.id == 402) { setScale (staffSpace * 0.89f); return; }
                else if (c.id == 403) { setScale (staffSpace * 1.12f); return; }
                else if (c.id == 404) { paperMode = ! paperMode; savePrefs(); }
                else if (c.id == 500) { showHelp = ! showHelp; repaint(); return; }
                dirty = true;
                repaint();
                return;
            }
    }
    void cycleScope()
    {
        if (song == nullptr) return;
        // SONG -> each staff track -> SONG
        std::vector<int> order;
        for (auto& st : model.staves)
            order.push_back (st.trackIdx >= 0 ? st.trackIdx
                                              : (st.mergedTracks.empty() ? -1 : st.mergedTracks.front()));
        if (scopeTrack < 0 && ! order.empty()) scopeTrack = order.front();
        else
        {
            auto it = std::find (order.begin(), order.end(), scopeTrack);
            scopeTrack = (it == order.end() || std::next (it) == order.end()) ? -1 : *std::next (it);
        }
    }
    void setScale (float s)
    {
        staffSpace = juce::jlimit (3.2f, 10.0f, s);
        dirty = true;
        savePrefs();
        repaint();
    }
    void compose()
    {
        if (onCompose == nullptr || song == nullptr) return;
        juce::String ask;
        ask << "Compose the full production FROM the score exactly as written: keep every existing note "
               "(pitches, rhythms, lengths) as the arrangement's melodic/rhythmic truth and build the "
               "sound design, groove detail, dynamics and mix around them.";
        if (scopeTrack >= 0 && scopeTrack < (int) song->tracks.size())
        {
            ask << " Scope: rework ONLY the track '" << song->tracks[(size_t) scopeTrack].name
                << "' around the written notes; leave every other track's notes untouched.";
            std::map<int, std::set<size_t>> m;
            for (size_t i = 0; i < song->tracks[(size_t) scopeTrack].notes.size(); ++i)
                m[scopeTrack].insert (i);
            if (onSelectionMirror) onSelectionMirror (m);         // the address rides the ask
        }
        if (vibeBox.getText().trim().isNotEmpty()) ask << " Vibe: " << vibeBox.getText().trim() << ".";
        if (instBox.getText().trim().isNotEmpty()) ask << " Instrumentation: " << instBox.getText().trim() << ".";
        onCompose (ask);
    }

    //-------------------------------------------------- timers + scroll
    void timerCallback() override
    {
        if (! isVisible()) return;
        if (getIsPlaying && getIsPlaying())
        {
            // CANVAS FOLLOWS EARS: keep the sounding system in the comfort band
            // (never while a hand is on the page — the drag outranks follow)
            if (juce::Time::getMillisecondCounter() > followPauseUntil
                && ! gesture.active && ! gesture.marquee
                && ! systems.empty() && ! measGeo.empty() && getPlayheadBeats)
            {
                const double ph = getPlayheadBeats();
                if (ph >= 0)
                {
                    const int mi = juce::jlimit (0, (int) measGeo.size() - 1, measureAtBeat (ph));
                    auto& sys = systems[(size_t) measGeo[(size_t) mi].sys];
                    const double top = sys.y0 - viewY;
                    const double vh = (double) viewH();
                    if (top < 34.0 + vh * 0.08 || top + sys.h > 34.0 + vh * 0.88)
                    {
                        const double target = juce::jlimit (0.0,
                            juce::jmax (0.0, totalH - 34.0 - vh), sys.y0 - 34.0 - vh * 0.18);
                        viewY += (target - viewY) * 0.22;
                        if (std::abs (target - viewY) < 0.8) viewY = target;
                        vScroll.setCurrentRange (viewY, viewH(), juce::dontSendNotification);
                    }
                }
            }
            repaint();
        }
    }
    void scrollBarMoved (juce::ScrollBar*, double newRange) override
    {
        followPauseUntil = juce::Time::getMillisecondCounter() + 1800;   // the hand outranks follow
        viewY = newRange;
        repaint();
    }

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ScorePage)
};

} // namespace sotadaw
