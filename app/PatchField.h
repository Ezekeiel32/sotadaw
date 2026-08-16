// PatchField.h - THE PATCHBAY (fable-uxwave, Chezy 2026-07-11: "REAL WIRES LIKE
// REASON" -> "100% REALISTIC, NEVER MESSY" -> "NOT ON TOP OF OTHER UI COMPONENTS!
// TO THE SIDE OFF THE INTERFACES! ALWAYS!" + "NOT LOOK! NOT FEEL! ESPECIALLY WHEN
// THEY MOVE!"). A transparent, hit-through overlay hanging REAL patch cables.
//
// v4 MATERIAL (Chezy 2026-07-16: "doesn't look like wires... needs to look like
// actual wires, like Reason"): the cable is a fat rubber cylinder — 6px jacket,
// twin blurred contact shadows, dark under-shade + specular crown + gloss thread
// riding the same path. Ends wear a REAL quarter-inch plug: machined socket
// (hex-nut flange, dark throat), chrome barrel, colored strain-relief boot with
// molded ridges, all rotated along the jack axis; card ends sit on a screwed
// jack plate. The glowing "signal beads" are dead — a live wire slides a sheen
// glint down its jacket instead (light on rubber, not sci-fi orbs).
//
// THE THREE LAWS (unchanged):
//  * GUTTER LAW (routing): a cable NEVER crosses another component. It leaves the
//    card's OUTWARD edge, runs the page's empty margin as a dressed trough (the
//    console hands each wire its `via` waypoints), and enters the room from the
//    side. Corners are filleted; only near-horizontal runs droop (verticals hang
//    taut, like real cable).
//  * MATERIAL LAW (look): a wire is RUBBER, not a neon stroke - contact shadow,
//    dark outline, a deep-jacket body in the channel's colour, and a white
//    specular crown riding THE SAME path (never a second diverging curve).
//  * PENDULUM LAW (feel): endpoints are FIXED; motion is the mid-run swinging
//    LATERALLY - a whisper at rest, a decaying ~4Hz shake on birth/re-plug.
//    Nothing breathes vertically; jelly is dead.
#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include "UiTheme.h"

struct PatchWire
{
    juce::Point<float> a, b;      // endpoints in PatchField space (a = card, b = floor)
    juce::Point<float> aDir { 0.0f, 1.0f },   // unit exit axis of jack A's boot
                       bDir { 1.0f, 0.0f };   // unit exit axis of jack B's boot
    std::vector<juce::Point<float>> via;      // GUTTER LAW: routed waypoints (may be empty)
    juce::Colour col;             // the channel's own colour = the cable's jacket
    float pulse = 0.0f;           // 0 = quiet cable; >0 = a sheen glint slides at this speed
    float slack = 1.0f;           // free-hang sag scale (unrouted wires + the back rack)
    bool dim = false;             // background run: thinner + fainter, never a hero
    bool aPlate = true;           // card ends wear a screwed jack plate under the socket
    bool bPlate = false;          // floor/bezel ends land on the room's own metal
    juce::String key;             // stable identity -> wobble on birth / re-plug
};

class PatchField : public juce::Component
{
public:
    PatchField() { setInterceptsMouseClicks (false, false); }   // pure light, no hitbox

    static constexpr float BOOT = 24.0f;      // plug + boot cover this much of the run

    void setWires (std::vector<PatchWire> ws)
    {
        std::vector<Live> next;
        next.reserve (ws.size());
        for (auto& w : ws)
        {
            Live lw;
            lw.w = w;
            lw.phase = (float) (std::abs (w.key.hashCode()) % 628) * 0.01f;
            bool born = true;
            for (auto& old : wires)
                if (old.w.key == w.key)
                {
                    lw.wob = old.wob;
                    if (old.w.a.getDistanceFrom (w.a) > 14.0f
                        || old.w.b.getDistanceFrom (w.b) > 14.0f)
                        lw.wob = juce::jmax (lw.wob, 5.0f);      // re-plugged: light shake
                    born = false;
                    break;
                }
            if (born) lw.wob = 8.0f;                             // fresh cable: full swing
            next.push_back (std::move (lw));
        }
        const bool wasLoom = ! wires.empty();
        wires = std::move (next);
        if (wires.empty() && wasLoom) repaint();                 // last cable unplugged
    }

    void tick()
    {
        if (! isVisible() || wires.empty()) return;
        anim += 0.033f;
        if (anim > 6283.0f) anim -= 6283.0f;
        for (auto& lw : wires)
        {
            lw.wob *= 0.94f;                                     // the swing settles
            // LAG LAW: dirty ONLY this cable's corridor (all points + shake room)
            auto bb = juce::Rectangle<float> (lw.w.a, lw.w.b);
            for (auto& v : lw.w.via) bb = bb.getUnion ({ v, v });
            bb = bb.expanded (32.0f);                            // fat jacket + plug flanges
            bb.setBottom (bb.getBottom() + 54.0f);               // free-hang belly room
            repaint (bb.toNearestInt());
        }
    }

    void paint (juce::Graphics& g) override
    {
        if (wires.empty()) return;
        // PASS 1: every cable's rubber. PASS 2: every plug ON TOP — a crossing
        // run must never paint over a neighbour's connector (Reason's own order).
        for (auto& lw : wires)
        {
            const auto& w = lw.w;
            if (w.a.getDistanceFrom (w.b) < 8.0f) continue;
            // PENDULUM LAW: lateral swing of the mid-run; endpoints never move.
            // rest = a whisper; birth/replug = a decaying ~4Hz shake
            const float lat = 1.0f * std::sin (anim * 0.7f + lw.phase)
                            + lw.wob * 0.9f * std::sin (anim * 4.6f + lw.phase);
            const auto path = w.via.empty()
                ? hangPath (w.a, w.aDir, w.b, w.bDir,
                            hangFor (w) + 0.4f * std::sin (anim * 0.8f + lw.phase), lat)
                : routedPath (w.a, w.aDir, w.b, w.bDir, w.via, BOOT, lat);
            strokeCable (g, path, w.col, w.dim);
            if (w.pulse > 0.001f)                       // signal = a sheen sliding the jacket
            {
                const float plen = path.getLength();
                const float W = w.dim ? 3.4f : 6.2f;
                for (int k = 0; k < 2; ++k)
                {
                    const float t = std::fmod (anim * w.pulse * 0.11f + lw.phase * 0.1f
                                                   + (float) k * 0.5f, 1.0f);
                    const float d = plen * t;
                    if (d < BOOT + 10.0f || d > plen - BOOT - 10.0f) continue;
                    const auto p0 = path.getPointAlongPath (juce::jmax (0.0f, d - 8.0f));
                    const auto p1 = path.getPointAlongPath (juce::jmin (plen, d + 8.0f));
                    g.setColour (w.col.brighter (0.65f).withAlpha (0.45f));
                    g.drawLine ({ p0, p1 }, W * 0.52f);
                    g.setColour (juce::Colours::white.withAlpha (0.38f));
                    g.drawLine ({ p0 + juce::Point<float> (0.0f, -W * 0.16f),
                                  p1 + juce::Point<float> (0.0f, -W * 0.16f) }, W * 0.22f);
                }
            }
        }
        for (auto& lw : wires)
        {
            const auto& w = lw.w;
            if (w.a.getDistanceFrom (w.b) < 8.0f) continue;
            drawPlug (g, w.a, w.aDir, w.col, w.dim, w.aPlate);
            drawPlug (g, w.b, w.bDir, w.col, w.dim, w.bPlate);
        }
    }

    // MATERIAL LAW v4: one path, seven strokes - two soft contact shadows, a crisp
    // dark outline, the deep rubber jacket, a darker under-shade hugging the belly,
    // a colour crown catching the key light, and a thin white gloss thread. All on
    // the SAME geometry (a re-sagged "sheen curve" diverges at the ends and reads
    // as two lines - that bug stays dead; sub-pixel vertical offsets only).
    static void strokeCable (juce::Graphics& g, const juce::Path& path,
                             juce::Colour col, bool dim)
    {
        const float W = dim ? 3.4f : 6.2f;
        const float A = dim ? 0.55f : 1.0f;
        const auto curved = juce::PathStrokeType::curved;
        const auto rounded = juce::PathStrokeType::rounded;
        {   // the shadow the cable throws on the console below it (two passes = blur)
            juce::Graphics::ScopedSaveState ss (g);
            g.addTransform (juce::AffineTransform::translation (2.4f, 5.0f));
            g.setColour (juce::Colours::black.withAlpha (0.10f * A));
            g.strokePath (path, { W + 4.0f, curved, rounded });
        }
        {
            juce::Graphics::ScopedSaveState ss (g);
            g.addTransform (juce::AffineTransform::translation (1.6f, 3.2f));
            g.setColour (juce::Colours::black.withAlpha (0.20f * A));
            g.strokePath (path, { W + 1.2f, curved, rounded });
        }
        g.setColour (juce::Colours::black.withAlpha (0.60f * A));   // crisp dark edge
        g.strokePath (path, { W + 1.7f, curved, rounded });
        g.setColour (col.darker (0.30f).withMultipliedSaturation (1.06f)
                        .withAlpha (dim ? 0.60f : 0.98f));          // the rubber jacket
        g.strokePath (path, { W, curved, rounded });
        {   // cylinder under-shade: the jacket's own belly turns from the light
            juce::Graphics::ScopedSaveState ss (g);
            g.addTransform (juce::AffineTransform::translation (0.0f, W * 0.20f));
            g.setColour (col.darker (0.85f).withAlpha (0.35f * A));
            g.strokePath (path, { W * 0.52f, curved, rounded });
        }
        {   // specular crown: the key light catches the cable's top, along ITS body
            juce::Graphics::ScopedSaveState ss (g);
            g.addTransform (juce::AffineTransform::translation (0.0f, -W * 0.22f));
            g.setColour (col.brighter (0.42f).withAlpha (dim ? 0.16f : 0.42f));
            g.strokePath (path, { W * 0.40f, curved, rounded });
            g.addTransform (juce::AffineTransform::translation (0.0f, -W * 0.08f));
            g.setColour (juce::Colours::white.withAlpha (dim ? 0.10f : 0.30f));
            g.strokePath (path, { W * 0.17f, curved, rounded });
        }
    }

    // free-hang sag: horizontal travel shows slack; vertical drops stay taut
    static float hangFor (const PatchWire& w)
    {
        const float horiz = std::abs (w.b.x - w.a.x);
        const float vert  = std::abs (w.b.y - w.a.y);
        return juce::jmin (46.0f, 8.0f + horiz * 0.12f + vert * 0.025f) * w.slack;
    }

    // FREE-HANG (no route): boot -> tangent cubic into a horizontal belly hung
    // below both boot ends (biased to the lower jack) -> boot. `lat` swings the
    // belly LATERALLY (the pendulum law) - the sag itself never pumps.
    static juce::Path hangPath (juce::Point<float> a, juce::Point<float> aDir,
                                juce::Point<float> b, juce::Point<float> bDir,
                                float hang, float lat = 0.0f, float boot = BOOT)
    {
        const auto A = a + aDir * boot;
        const auto B = b + bDir * boot;
        const float belly = juce::jmax (A.y, B.y) + juce::jmax (2.0f, hang);
        const float bx    = A.x + (B.x - A.x) * (A.y > B.y ? 0.42f : 0.58f) + lat;
        const float k     = boot * 1.1f;
        juce::Path p;
        p.startNewSubPath (a);
        p.lineTo (A);
        p.cubicTo (A + aDir * k, { bx - (bx - A.x) * 0.45f, belly }, { bx, belly });
        p.cubicTo ({ bx + (B.x - bx) * 0.45f, belly }, B + bDir * k, B);
        p.lineTo (b);
        return p;
    }

    // GUTTER LAW (routed): boot -> filleted polyline through the console's
    // waypoints -> boot. Verticals run taut (they only LEAN with the pendulum,
    // strongest mid-run); near-horizontal spans droop a little - that's where a
    // real cable shows its slack. v4: bigger fillets + deeper droop so the
    // trough run reads as hung cable, never a PCB trace.
    static juce::Path routedPath (juce::Point<float> a, juce::Point<float> aDir,
                                  juce::Point<float> b, juce::Point<float> bDir,
                                  const std::vector<juce::Point<float>>& via,
                                  float boot, float lat)
    {
        std::vector<juce::Point<float>> pts;
        pts.reserve (via.size() + 4);
        pts.push_back (a);
        pts.push_back (a + aDir * boot);
        const int nVia = (int) via.size();
        for (int i = 0; i < nVia; ++i)
        {   // pendulum envelope: zero at the ends, full swing mid-run
            const float env = std::sin (juce::MathConstants<float>::pi
                                        * (float) (i + 1) / (float) (nVia + 1));
            pts.push_back (via[(size_t) i] + juce::Point<float> (lat * env, 0.0f));
        }
        pts.push_back (b + bDir * boot);
        pts.push_back (b);

        juce::Path p;
        p.startNewSubPath (pts[0]);
        p.lineTo (pts[1]);
        for (size_t i = 2; i + 1 < pts.size(); ++i)
        {   // fillet the corner AT pts[i]: stop short, quadratic through it
            const auto prev = pts[i - 1], cur = pts[i], nxt = pts[i + 1];
            const float lIn  = cur.getDistanceFrom (prev);
            const float lOut = nxt.getDistanceFrom (cur);
            const float r = juce::jmin (24.0f, lIn * 0.42f, lOut * 0.42f);
            if (lIn > 0.5f && lOut > 0.5f && r > 1.0f)
            {
                const auto inPt  = cur + (prev - cur) * (r / lIn);
                const auto outPt = cur + (nxt - cur) * (r / lOut);
                // a long, mostly-horizontal approach carries a shallow droop
                if (std::abs (cur.y - prev.y) < 8.0f && lIn > 56.0f)
                {
                    const float d = juce::jmin (12.0f, lIn * 0.06f);
                    const auto mid = (prev + inPt) * 0.5f + juce::Point<float> (0.0f, d);
                    p.quadraticTo (mid, inPt);
                }
                else
                    p.lineTo (inPt);
                p.quadraticTo (cur, outPt);
            }
            else
                p.lineTo (cur);
        }
        p.lineTo (pts.back());
        return p;
    }

    // THE QUARTER-INCH PLUG (v4): everything after the socket flange is drawn in
    // a frame rotated along the jack axis — chrome barrel, insulator ring, the
    // cable-colored strain-relief boot with molded ridges. Card ends sit on a
    // screwed jack plate so the connector reads as INSTALLED hardware, not a dot.
    static void drawPlug (juce::Graphics& g, juce::Point<float> p,
                          juce::Point<float> dir, juce::Colour col,
                          bool dim = false, bool plate = false)
    {
        const float da = dim ? 0.62f : 1.0f;
        const float ang = std::atan2 (dir.y, dir.x);
        {   // ---- rotated hardware: plate, barrel, boot (local +x = out along dir) ----
            juce::Graphics::ScopedSaveState ss (g);
            g.addTransform (juce::AffineTransform::rotation (ang, p.x, p.y));
            const float X = p.x, Y = p.y;
            if (plate)
            {   // the jack plate: brushed tab bridging the card edge, two screws
                juce::Rectangle<float> pl (X - 13.0f, Y - 8.5f, 18.0f, 17.0f);
                g.setColour (juce::Colours::black.withAlpha (0.30f * da));
                g.fillRoundedRectangle (pl.translated (0.6f, 1.6f), 4.0f);
                g.setColour (juce::Colour (0xff1d2230).withAlpha (0.96f * da));
                g.fillRoundedRectangle (pl, 4.0f);
                g.setGradientFill ({ juce::Colours::white.withAlpha (0.10f * da),
                                     pl.getTopLeft(),
                                     juce::Colours::white.withAlpha (0.015f * da),
                                     pl.getBottomLeft(), false });
                g.fillRoundedRectangle (pl, 4.0f);
                g.setColour (juce::Colours::white.withAlpha (0.09f * da));
                g.drawRoundedRectangle (pl.reduced (0.5f), 4.0f, 1.0f);
                for (const float sy : { -5.4f, 5.4f })
                {   // machine screws, slot catching the light
                    g.setColour (juce::Colour (0xff10141c).withAlpha (da));
                    g.fillEllipse (X - 9.8f - 1.5f, Y + sy - 1.5f, 3.0f, 3.0f);
                    g.setColour (juce::Colours::white.withAlpha (0.30f * da));
                    g.drawLine (X - 9.8f - 1.0f, Y + sy - 0.6f,
                                X - 9.8f + 1.0f, Y + sy + 0.6f, 0.7f);
                }
            }
            // chrome barrel: x 2..13 — three stripes fake the machined cylinder
            {
                juce::Rectangle<float> bar (X + 2.0f, Y - 3.6f, 11.0f, 7.2f);
                g.setColour (juce::Colours::black.withAlpha (0.35f * da));   // seat shadow
                g.fillRoundedRectangle (bar.translated (0.6f, 1.4f), 2.4f);
                g.setColour (juce::Colour (0xff8f97a6).withAlpha (da));
                g.fillRoundedRectangle (bar, 2.4f);
                g.setColour (juce::Colour (0xffd7dde8).withAlpha (0.92f * da)); // top light
                g.fillRoundedRectangle (bar.withHeight (2.4f).translated (0.0f, 0.8f), 1.2f);
                g.setColour (juce::Colour (0xff3a404d).withAlpha (0.90f * da)); // turned belly
                g.fillRoundedRectangle (bar.withHeight (2.0f).withY (bar.getBottom() - 2.6f), 1.0f);
            }
            // insulator ring: x 13..15.4
            g.setColour (juce::Colour (0xff14171f).withAlpha (da));
            g.fillRoundedRectangle (X + 13.0f, Y - 3.3f, 2.4f, 6.6f, 1.0f);
            // strain-relief boot: x 15.4..28, cable colour, tapering into the run
            {
                juce::Path boot;
                boot.startNewSubPath (X + 15.4f, Y - 4.1f);
                boot.lineTo (X + 26.5f, Y - 2.6f);
                boot.quadraticTo (X + 28.6f, Y, X + 26.5f, Y + 2.6f);
                boot.lineTo (X + 15.4f, Y + 4.1f);
                boot.closeSubPath();
                g.setColour (juce::Colours::black.withAlpha (0.28f * da));
                {
                    juce::Graphics::ScopedSaveState s2 (g);
                    g.addTransform (juce::AffineTransform::translation (0.5f, 1.3f));
                    g.fillPath (boot);
                }
                g.setColour (col.darker (0.25f).withAlpha (0.97f * da));
                g.fillPath (boot);
                for (const float rx : { 17.4f, 20.0f, 22.6f })   // molded grip ridges
                {
                    g.setColour (col.darker (0.75f).withAlpha (0.55f * da));
                    g.drawLine (X + rx, Y - 3.5f, X + rx, Y + 3.5f, 1.1f);
                }
                g.setColour (juce::Colours::white.withAlpha (0.24f * da));   // rubber sheen
                g.drawLine (X + 16.0f, Y - 2.5f, X + 25.6f, Y - 1.6f, 1.0f);
            }
        }
        // ---- the socket flange, screen-space (a nut is round enough from here) ----
        g.setColour (juce::Colours::black.withAlpha (0.42f * da));           // seat shadow
        g.fillEllipse (p.x - 8.0f, p.y - 6.8f, 16.0f, 16.0f);
        {   // hex-nut flange: six facets around the collar
            juce::Path hex;
            const float R = 7.4f;
            for (int i = 0; i < 6; ++i)
            {
                const float a2 = juce::MathConstants<float>::pi / 3.0f * (float) i
                               + juce::MathConstants<float>::pi / 6.0f;
                const juce::Point<float> v (p.x + R * std::cos (a2), p.y + R * std::sin (a2));
                if (i == 0) hex.startNewSubPath (v); else hex.lineTo (v);
            }
            hex.closeSubPath();
            g.setColour (juce::Colour (0xff2a3140).withAlpha (da));
            g.fillPath (hex);
            g.setGradientFill ({ juce::Colours::white.withAlpha (0.22f * da),
                                 { p.x, p.y - 8.0f },
                                 juce::Colours::white.withAlpha (0.0f),
                                 { p.x, p.y + 8.0f }, false });
            g.fillPath (hex);
            g.setColour (juce::Colours::black.withAlpha (0.40f * da));
            g.strokePath (hex, juce::PathStrokeType (1.0f));
        }
        g.setColour (juce::Colour (0xff454e60).withAlpha (da));              // machined collar
        g.fillEllipse (p.x - 5.2f, p.y - 5.2f, 10.4f, 10.4f);
        g.setColour (juce::Colours::white.withAlpha (0.34f * da));           // bevel light
        g.drawEllipse (p.x - 5.2f, p.y - 5.2f, 10.4f, 10.4f, 1.0f);
        g.setColour (juce::Colour (0xff07090d).withAlpha (da));              // the throat
        g.fillEllipse (p.x - 3.3f, p.y - 3.3f, 6.6f, 6.6f);
        g.setColour (col.brighter (0.10f).withAlpha (0.85f * da));           // seated plug face
        g.fillEllipse (p.x - 2.1f, p.y - 2.1f, 4.2f, 4.2f);
        g.setColour (juce::Colours::white.withAlpha (0.75f * da));           // glint
        g.fillEllipse (p.x - 1.9f, p.y - 2.3f, 1.6f, 1.6f);
    }

    // kept for the engine room's rack-back harness (drawn inside its own raster)
    static juce::Path cablePath (juce::Point<float> a, juce::Point<float> aDir,
                                 juce::Point<float> b, juce::Point<float> bDir,
                                 float hang, float boot = 11.0f)
    { return hangPath (a, aDir, b, bDir, hang, 0.0f, boot); }

private:
    struct Live { PatchWire w; float wob = 0.0f, phase = 0.0f; };

    std::vector<Live> wires;
    float anim = 0.0f;
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PatchField)
};
