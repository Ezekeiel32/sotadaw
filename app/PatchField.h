// PatchField.h - THE PATCHBAY (fable-uxwave, Chezy 2026-07-11: "REAL WIRES LIKE
// REASON" -> "100% REALISTIC, NEVER MESSY" -> "NOT ON TOP OF OTHER UI COMPONENTS!
// TO THE SIDE OFF THE INTERFACES! ALWAYS!" + "NOT LOOK! NOT FEEL! ESPECIALLY WHEN
// THEY MOVE!"). A transparent, hit-through overlay hanging REAL patch cables.
//
// THE THREE LAWS:
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
    float pulse = 0.0f;           // 0 = quiet cable; >0 = beads travel at this speed
    float slack = 1.0f;           // free-hang sag scale (unrouted wires + the back rack)
    bool dim = false;             // background run: thinner + fainter, never a hero
    juce::String key;             // stable identity -> wobble on birth / re-plug
};

class PatchField : public juce::Component
{
public:
    PatchField() { setInterceptsMouseClicks (false, false); }   // pure light, no hitbox

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
            bb = bb.expanded (26.0f);
            bb.setBottom (bb.getBottom() + 46.0f);               // free-hang belly room
            repaint (bb.toNearestInt());
        }
    }

    void paint (juce::Graphics& g) override
    {
        if (wires.empty()) return;
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
                : routedPath (w.a, w.aDir, w.b, w.bDir, w.via, 11.0f, lat);
            strokeCable (g, path, w.col, w.dim);
            if (w.pulse > 0.001f)                       // signal beads chase a live wire
            {
                const float plen = path.getLength();
                for (int k = 0; k < 2; ++k)
                {
                    const float t = std::fmod (anim * w.pulse * 0.16f + lw.phase * 0.1f
                                                   + (float) k * 0.5f, 1.0f);
                    const auto p = path.getPointAlongPath (plen * t);
                    g.setColour (w.col.brighter (0.4f).withAlpha (0.40f));
                    g.fillEllipse (p.x - 4.2f, p.y - 4.2f, 8.4f, 8.4f);
                    g.setColour (juce::Colours::white.withAlpha (0.90f));
                    g.fillEllipse (p.x - 1.7f, p.y - 1.7f, 3.4f, 3.4f);
                }
            }
            drawPlug (g, w.a, w.aDir, w.col, w.dim);
            drawPlug (g, w.b, w.bDir, w.col, w.dim);
        }
    }

    // MATERIAL LAW: one path, four strokes - contact shadow under it, dark outline,
    // deep rubber jacket, and a white crown riding the SAME geometry (a re-sagged
    // "sheen curve" diverges at the ends and reads as two lines - that bug is dead)
    static void strokeCable (juce::Graphics& g, const juce::Path& path,
                             juce::Colour col, bool dim)
    {
        const float W = dim ? 2.1f : 3.1f;
        const float A = dim ? 0.52f : 1.0f;
        juce::PathStrokeType body (W, juce::PathStrokeType::curved,
                                   juce::PathStrokeType::rounded);
        {   // the shadow the cable throws on the console below it
            juce::Graphics::ScopedSaveState ss (g);
            g.addTransform (juce::AffineTransform::translation (2.0f, 3.6f));
            g.setColour (juce::Colours::black.withAlpha (0.24f * A));
            g.strokePath (path, { W + 0.6f, juce::PathStrokeType::curved,
                                  juce::PathStrokeType::rounded });
        }
        g.setColour (juce::Colours::black.withAlpha (0.50f * A));   // crisp dark edge
        g.strokePath (path, { W + 1.2f, juce::PathStrokeType::curved,
                              juce::PathStrokeType::rounded });
        g.setColour (col.darker (0.32f).withMultipliedSaturation (0.85f)
                        .withAlpha (dim ? 0.55f : 0.97f));          // the rubber jacket
        g.strokePath (path, body);
        {   // specular crown: the key light catches the cable's top, along ITS body
            juce::Graphics::ScopedSaveState ss (g);
            g.addTransform (juce::AffineTransform::translation (-0.3f, -0.85f));
            g.setColour (juce::Colours::white.withAlpha (dim ? 0.10f : 0.26f));
            g.strokePath (path, { 1.0f, juce::PathStrokeType::curved,
                                  juce::PathStrokeType::rounded });
            g.setColour (col.brighter (0.55f).withAlpha (dim ? 0.14f : 0.32f));
            g.strokePath (path, { 0.7f, juce::PathStrokeType::curved,
                                  juce::PathStrokeType::rounded });
        }
    }

    // free-hang sag: horizontal travel shows slack; vertical drops stay taut
    static float hangFor (const PatchWire& w)
    {
        const float horiz = std::abs (w.b.x - w.a.x);
        const float vert  = std::abs (w.b.y - w.a.y);
        return juce::jmin (38.0f, 6.0f + horiz * 0.10f + vert * 0.02f) * w.slack;
    }

    // FREE-HANG (no route): boot -> tangent cubic into a horizontal belly hung
    // below both boot ends (biased to the lower jack) -> boot. `lat` swings the
    // belly LATERALLY (the pendulum law) - the sag itself never pumps.
    static juce::Path hangPath (juce::Point<float> a, juce::Point<float> aDir,
                                juce::Point<float> b, juce::Point<float> bDir,
                                float hang, float lat = 0.0f, float boot = 11.0f)
    {
        const auto A = a + aDir * boot;
        const auto B = b + bDir * boot;
        const float belly = juce::jmax (A.y, B.y) + juce::jmax (2.0f, hang);
        const float bx    = A.x + (B.x - A.x) * (A.y > B.y ? 0.42f : 0.58f) + lat;
        const float k     = boot * 1.8f;
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
    // real cable shows its slack.
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
            const float r = juce::jmin (16.0f, lIn * 0.42f, lOut * 0.42f);
            if (lIn > 0.5f && lOut > 0.5f && r > 1.0f)
            {
                const auto inPt  = cur + (prev - cur) * (r / lIn);
                const auto outPt = cur + (nxt - cur) * (r / lOut);
                // a long, mostly-horizontal approach carries a shallow droop
                if (std::abs (cur.y - prev.y) < 8.0f && lIn > 56.0f)
                {
                    const float d = juce::jmin (8.0f, lIn * 0.05f);
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

    static void drawPlug (juce::Graphics& g, juce::Point<float> p,
                          juce::Point<float> dir, juce::Colour col, bool dim = false)
    {
        const float da = dim ? 0.55f : 1.0f;
        // the strain-relief boot: a thick rubber cuff along the jack axis - the
        // detail that says "this cable comes OUT of this socket"
        g.setColour (col.darker (0.30f).withAlpha (0.85f * da));
        g.drawLine ({ p, p + dir * 9.5f }, 4.6f);
        g.setColour (col.brighter (0.35f).withAlpha (0.35f * da));
        g.drawLine ({ p + dir * 1.5f, p + dir * 8.0f }, 1.4f);
        g.setColour (juce::Colours::black.withAlpha (0.45f * da));         // seat shadow
        g.fillEllipse (p.x - 5.6f, p.y - 4.6f, 11.2f, 11.2f);
        g.setColour (juce::Colour (0xff262c37).withAlpha (da));            // machined collar
        g.fillEllipse (p.x - 5.0f, p.y - 5.0f, 10.0f, 10.0f);
        g.setColour (juce::Colours::white.withAlpha (0.38f * da));
        g.drawEllipse (p.x - 5.0f, p.y - 5.0f, 10.0f, 10.0f, 1.0f);
        g.setColour (col.brighter (0.10f).withAlpha (da));                 // the boot face
        g.fillEllipse (p.x - 2.9f, p.y - 2.9f, 5.8f, 5.8f);
        g.setColour (juce::Colours::white.withAlpha (0.80f * da));         // glint
        g.fillEllipse (p.x - 2.6f, p.y - 2.9f, 1.7f, 1.7f);
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
