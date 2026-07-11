// uismoke — offscreen paint harness for the visible-lane components (#38).
// Constructs each self-contained component, feeds test data, paints into a
// juce::Image (SOFTWARE rendering — no X server, no peer, never touches a
// display), saves PNGs. Proves construct/layout/paint don't crash AND gives
// the agent a real picture to inspect — the safe replacement for the
// display-incident snapshot path.
//   uismoke <outdir>
#include <juce_gui_basics/juce_gui_basics.h>
#include "PresetBrowser.h"
#include "HearStrip.h"
#include "PadGrid.h"
#include "ChatPanel.h"
#include "SurgicalBadge.h"
#include "TunePanel.h"
#include "HistoryPanel.h"
#include "GhostGlass.h"

static void savePng (juce::Component& c, int w, int h, const juce::File& out)
{
    c.setBounds (0, 0, w, h);
    juce::Image img (juce::Image::ARGB, w, h, true);
    {
        juce::Graphics g (img);
        c.paintEntireComponent (g, false);        // no peer needed — software raster
    }
    juce::PNGImageFormat png;
    out.deleteFile();
    juce::FileOutputStream os (out);
    if (os.openedOk() && png.writeImageToStream (img, os))
        std::cout << "[uismoke] " << out.getFileName() << " " << w << "x" << h << " OK\n";
    else
        std::cout << "[uismoke] FAILED " << out.getFileName() << "\n";
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI juceInit;      // message manager, no window
    const juce::File dir = juce::File::getCurrentWorkingDirectory()
                               .getChildFile (argc > 1 ? argv[1] : "ui_smoke");
    dir.createDirectory();
    const auto root = juce::File (SOTADAW_ROOT);

    // 0) THE CHAT — every message kind as one real conversation, busy + dead states.
    // This is the panel Chezy called "Windows 98"; it gets styled by pixels now.
    {
        ChatPanel chat;
        chat.headerInfo = "139 skills - KG online";
        chat.agentBusy = true;
        chat.add (ChatPanel::Kind::user, "make the drop hit harder and darker, keep the vocal airy");
        chat.add (ChatPanel::Kind::tool, "get_song demo_track");
        chat.add (ChatPanel::Kind::tool, "get_song demo_track");
        chat.add (ChatPanel::Kind::tool, "set_track_param bass fx[0].cutoff 900");
        chat.add (ChatPanel::Kind::agent, "Pushed the drop: **kick +2 dB** into a tighter comp, reese lowpassed "
                                          "to `900 Hz` with drive, snare layered with a 909 clap. Vocal untouched. "
                                          "Rendered: **-9.8 LUFS**, `0 clipped`, low band now leads.");
        chat.add (ChatPanel::Kind::report,
                  "[doctor] eval_house: 3 issue(s):\n"
                  "  [A1] no arrangement - it's a loop, not a song -> arrange / finish\n"
                  "  [F1] 'bass' is dead-mechanical -> humanize\n"
                  "  [X1] no master limiter -> finish (master safety)\n"
                  "  CLEAN after prescribe: 1 remaining");
        // the long-reply fold: an essay with headings, bullets and a table must
        // collapse to ~14 lines with a fade + "show all" chip (the wall-of-text law)
        chat.add (ChatPanel::Kind::agent,
                  "## What I changed\n"
                  "- kick: +2 dB, comp attack 8 ms -> 4 ms\n"
                  "- reese: LP 900 Hz, drive 0.4, width 0.7\n"
                  "- snare: layered clap_909 at -3 dB\n"
                  "- master: trim +1.5 dB into the brickwall\n"
                  "## Why it works\n"
                  "The kick and reese were fighting 60-90 Hz. Sidechaining the reese "
                  "1.5 dB under the kick opens the fundamental, and the tighter comp "
                  "attack lets the transient lead the low end instead of smearing it.\n"
                  "## Arrangement\n"
                  "| Bars | Section | Layers |\n"
                  "| 1-8 | Intro | pad, melody(half) |\n"
                  "| 9-16 | Build | + kick, 808 on F1 |\n"
                  "| 17-26 | Drop | full kit + bass + acid |\n"
                  "| 27-36 | Break | pad + vox, no drums |\n"
                  "| 37-52 | Drop II | full kit, acid 2600 |\n"
                  "| 53-62 | Outro | pad + melody(+harmony) |\n"
                  "## Next moves\n"
                  "- hum a topline over bars 17-26 and I'll voice it\n"
                  "- the break could take a riser: bandpass sweep 300 -> 6000 Hz\n"
                  "- if the drop still feels soft, ask me to push the 909 layer");
        chat.add (ChatPanel::Kind::status, "rendering proposal...");
        chat.add (ChatPanel::Kind::error, "loop_gen: no loop DNA for 'gabber2'");
        chat.add (ChatPanel::Kind::analysis, "ears", { "proposal", "-1.5", "0", "-11.9" });
        chat.add (ChatPanel::Kind::perception,
                  "hear: 8.3s, 8 mel bands x 32 cols, bpm 115\n"
                  " 9.7k|  . .. .:. .. . .:. .. .\n"
                  " 4.9k| ::--::--=::--::--=::--=\n"
                  " 2.3k| ==++==++*==++==++*==++*\n"
                  " 943 | ++**++**#++**++**#++**#\n"
                  " 391 | **##**##%**##**##%**##%\n"
                  " 190 | %%@@%%@@@%%@@%%@@@%%@@@\n"
                  "  ons| x.x.x.x.x.x.x.x.x.x.x.x\n"
                  "  bar| 1   2   3   4   5   6");
        chat.add (ChatPanel::Kind::proposal, "drop rework: 6 tracks changed - kick/bass/snare gain+fx, "
                                             "14 ghost notes on snare, master trim +1.5 dB",
                   { "intro", "build", "drop", "break", "drop2", "outro" });
        {   // f124: waveform-on-proposal pixel proof (synthetic peaks)
            std::vector<float> pk;
            for (int i = 0; i < 170; ++i)
                pk.push_back (0.15f + 0.8f * std::abs (std::sin (i * 0.09f)) * (i % 47 < 4 ? 1.0f : 0.55f));
            chat.setProposalPeaks (pk);
        }
        savePng (chat, 330, 640, dir.getChildFile ("chat.png"));
        chat.toggleExpand (4);          // unfold the essay (msg 4: the long agent reply)
        savePng (chat, 330, 900, dir.getChildFile ("chat_expanded.png"));
        {   // AGENT-FIRST WIDTH: the ladder-kill + bigger adaptive HEARS proof —
            // a status-heavy scene at the agent-mode column width (Chezy live)
            ChatPanel wide;
            wide.add (ChatPanel::Kind::user, "make the midi more like the song, sharper drums");
            wide.add (ChatPanel::Kind::status, "resident agent (opus, warm) working...");
            wide.add (ChatPanel::Kind::status, "...composing, still streaming...");
            wide.add (ChatPanel::Kind::status, "...composing (1 min in), still streaming...");
            wide.add (ChatPanel::Kind::status, "...composing (2 min in), still streaming...");
            wide.add (ChatPanel::Kind::status, "...composing (3 min in), still streaming...");
            wide.add (ChatPanel::Kind::perception,
                      "hear: 207.3s, 14 mel bands (top=high) x 96 cols, bpm 111.1\n"
                      "12.0k|.:. .. .:. ..:. .. .:. ..:. .. .:. ..:. .. .:. ..:. .. .:. ..:. .:.\n"
                      " 9.7k|... ..:.. ..:.. ..:.. ..:.. ..:.. ..:.. ..:.. ..:.. ..:.. ..:.. ...\n"
                      " 7.7k|:.. .:.::. .:.::. .:.::. .:.::. .:.::. .:.::. .:.::. .:.::. .:.::. :.\n"
                      " 6.2k|::.:.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::.::\n"
                      " 4.9k|====--====--====--====--====--====--====--====--====--====--====--==\n"
                      " 2.3k|++==++==++==++==++==++==++==++==++==++==++==++==++==++==++==++==++==+\n"
                      " 1.3k|**++**++**++**++**++**++**++**++**++**++**++**++**++**++**++**++**++\n"
                      " 943 |##**##**##**##**##**##**##**##**##**##**##**##**##**##**##**##**##**\n"
                      " 391 |%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##%%##\n"
                      " 190 |@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%@@%%\n"
                      "  ons|x...x...x...x...x...x...x...x...x...x...x...x...x...x...x...x...x...\n"
                      "  bar|1   5   9   13  17  21  25  29  33  37  41  45  49  53  57  61  65 ");
            wide.add (ChatPanel::Kind::status, "[take] SURGICAL: 1614 notes - guitar+piano - +1021/-1021");
            wide.add (ChatPanel::Kind::status, "proposal accepted + committed");
            wide.add (ChatPanel::Kind::status, "exporting C2PA-signed master...");
            wide.add (ChatPanel::Kind::agent, "Done - the drums are sharper and the piano sits forward. "
                                              "Sanity-check the drop and tell me the next move.");
            savePng (wide, 660, 760, dir.getChildFile ("chat_agentwidth.png"));
        }
        ChatPanel welcome;              // the first-open state: watermark + starter chips
        welcome.headerInfo = "141 skills - KG online";
        savePng (welcome, 330, 640, dir.getChildFile ("chat_welcome.png"));
        ChatPanel dead;
        dead.agentDead = true;
        dead.add (ChatPanel::Kind::user, "hello?");
        savePng (dead, 330, 200, dir.getChildFile ("chat_dead.png"));

        // THE JUMBLE BAND (Chezy live 2026-07-10): a SHORT conversation in a TALL
        // panel — bottom-anchoring leaves a void above the rows, and the coach
        // used to paint hero + starter chips INTO it (colliding with, and staying
        // clickable over, the first messages whenever topOffset < 344). The void
        // above this scene's rows must be EMPTY MATERIAL — no headline, no chips.
        {
            ChatPanel jb;
            jb.add (ChatPanel::Kind::status, "new project: untitled_25 (4 starter voices, agent-ready)");
            jb.add (ChatPanel::Kind::user,   "make the best psytrance goa 4 minute track, india beach rave");
            jb.add (ChatPanel::Kind::status, "[ctx] NOW: beat 0.0 (bar 0.0, 0:00.00, 120.0 bpm)");
            jb.add (ChatPanel::Kind::status, "resident agent (opus, first-spin) working...");
            jb.add (ChatPanel::Kind::agent,  "I'll build a full goa/psytrance track on the proposal copy. "
                                             "Loading the tools I need in one shot, then seeding from the "
                                             "knowledge graph's psytrance DNA.");
            jb.add (ChatPanel::Kind::tool,   "start_session genre goa trance psytrance");
            jb.add (ChatPanel::Kind::tool,   "list_instruments");
            savePng (jb, 660, 560, dir.getChildFile ("chat_jumbleband.png"));
        }
        // short EMPTY panel: the headline coaches, but the chips are WITHHELD —
        // all four must fit above the fold or none show (no half-clipped teaching)
        {
            ChatPanel tight;
            savePng (tight, 330, 300, dir.getChildFile ("chat_welcome_short.png"));
        }
    }
    // 0b) tooltip glass — the LnF draw path rendered straight to pixels
    {
        SotaLookAndFeel lnf;
        const juce::String tip = "the preset rail: 4,366 factory sounds - drag one onto any lane";
        const auto b = lnf.getTooltipBounds (tip, { 40, 40 }, { 0, 0, 500, 200 });
        juce::Image img (juce::Image::ARGB, b.getWidth() + 28, b.getHeight() + 28, true);
        {
            juce::Graphics g (img);
            g.fillAll (theme::bg);
            g.setOrigin (14, 14);
            lnf.drawTooltip (g, tip, b.getWidth(), b.getHeight());
        }
        juce::PNGImageFormat png;
        auto out = dir.getChildFile ("tooltip.png");
        out.deleteFile();
        juce::FileOutputStream os (out);
        if (os.openedOk() && png.writeImageToStream (img, os))
            std::cout << "[uismoke] tooltip.png OK\n";
    }
    // 1) preset browser — populated + a mood search
    {
        sotadaw::PresetBrowser pb;
        pb.loadLibrary (root.getChildFile ("library.json"));
        savePng (pb, 230, 520, dir.getChildFile ("preset_browser.png"));
    }
    // 2) hear strip — empty state AND a synthetic tensor (bar grid + playhead beam)
    {
        sotadaw::HearStrip hs;
        savePng (hs, 900, 46, dir.getChildFile ("hear_empty.png"));
        std::vector<std::vector<int>> tg (8, std::vector<int> (64, 0));
        for (int r = 0; r < 8; ++r)
            for (int c = 0; c < 64; ++c)
                tg[(size_t) r][(size_t) c] = juce::jlimit (0, 9,
                    (7 - r) + ((c % 8) == 0 ? 2 : 0) - ((c / 8) % 2) * 2);
        std::vector<int> ons (64, 0);
        for (int c = 0; c < 64; c += 4) ons[(size_t) c] = 8;
        hs.setTensor (std::move (tg), std::move (ons), 32.0, 120.0, "PROPOSAL - demo");
        hs.setPlayheadNorm (0.4);
        savePng (hs, 900, 46, dir.getChildFile ("hear_full.png"));
    }
    // 3) pad grid — empty AND populated
    {
        sotadaw::PadGrid pg;
        int scenes = 5, active = 2;
        pg.getNumScenes  = [&] { return scenes; };
        pg.getSceneName  = [] (int i) { return juce::StringArray { "Drums", "+Bass", "+Keys", "FULL", "Break" }[i]; };
        pg.getActiveScene = [&] { return active; };
        pg.onPad = [] (int) {};
        savePng (pg, 900, 78, dir.getChildFile ("pad_grid.png"));
        scenes = 0;
        savePng (pg, 900, 78, dir.getChildFile ("pad_grid_empty.png"));
    }
    // 9) THE SCALPEL VERDICT chips — all three states from real event-shaped JSON
    //    (the green payload is verbatim from the 2026-07-05 live E2E run).
    {
        struct Strip : juce::Component
        {
            sotadaw::SurgicalBadge a, b, c;
            Strip()
            {
                a.setVerdict (juce::JSON::parse (
                    R"({"clean": true, "full_write": false, "summary": "SURGICAL: every change is receipted.",)"
                    R"( "touched_tracks": ["808", "kick", "kick_loop"], "note_changes": 3,)"
                    R"( "receipts": ["kick+kick_loop: set vel 1 on 2 in bars 4.475-4.525", "808: insert 1 in bars 4.425-4.575"],)"
                    R"( "out_of_scope": []})"));
                b.setVerdict (juce::JSON::parse (
                    R"({"clean": true, "full_write": true, "note_changes": 214, "receipts": ["FULL WRITE: 8 tracks"],)"
                    R"( "touched_tracks": [], "out_of_scope": []})"));
                c.setVerdict (juce::JSON::parse (
                    R"({"clean": false, "note_changes": 5, "receipts": [], "touched_tracks": ["piano"],)"
                    R"( "out_of_scope": ["track:piano gainDb -6.5 -> -2.0", "meta:bpm 132.0 -> 140.0"]})"));
                addAndMakeVisible (a); addAndMakeVisible (b); addAndMakeVisible (c);
            }
            void resized() override
            {
                auto r = getLocalBounds().reduced (8, 6);
                a.setBounds (r.removeFromLeft (a.preferredWidth())); r.removeFromLeft (10);
                b.setBounds (r.removeFromLeft (b.preferredWidth())); r.removeFromLeft (10);
                c.setBounds (r.removeFromLeft (c.preferredWidth()));
            }
            void paint (juce::Graphics& g) override { g.fillAll (theme::bg); }
        } strip;
        savePng (strip, 640, 40, dir.getChildFile ("surgical_badges.png"));
    }
    // 10) THE TUNE LAB — fresh state + loaded with the REAL choir tpain report
    {
        TunePanel tp;
        tp.setTarget ("vocals", true, { "melody", "pads" }, "", false);
        savePng (tp, 980, TunePanel::idealHeight, dir.getChildFile ("tune_lab.png"));
        auto repF = root.getChildFile ("songs/_tune_choir_tpain.report.json");
        auto rep = repF.existsAsFile() ? juce::JSON::parse (repF.loadFileAsString())
                 : juce::JSON::parse (
                    R"J({"stats":{"events":51,"corrected":38,"median_abs_cents_off":8.1,"resynth_pct":26.0},)J"
                    R"J("notes":[{"beat0":16.07,"sung":"D5+130c","target_name":"C#5","cents_moved":-130.0,"reason":"chord(C#+F+G#)"},)J" R"J(
                    R"J({"beat0":10.08,"sung":"E5-69c","target_name":"F5","cents_moved":69.0,"reason":"chord(C+F+G#)"},)J" R"J(
                    R"J({"beat0":4.01,"sung":"D#5+26c","target_name":"D#5","cents_moved":-26.0,"reason":"scale(F minor)"},)J" R"J(
                    R"J({"beat0":2.35,"sung":"E2+53c","target_name":"D#2","cents_moved":0.0,"reason":"held(quiet)"}]})J");
        tp.setTarget ("vocals", true, { "melody", "pads" }, "b8-b16", true, true);   // take carries tuning
        tp.setReport (rep);
        savePng (tp, 980, TunePanel::idealHeight, dir.getChildFile ("tune_lab_report.png"));
        TunePanel busyPanel;                       // the busy state must read ALIVE
        busyPanel.setTarget ("vocals", true, {}, "", false);
        busyPanel.setBusy (true);
        for (int i = 0; i < 11; ++i) busyPanel.tick();
        savePng (busyPanel, 980, TunePanel::idealHeight, dir.getChildFile ("tune_lab_busy.png"));
    }
    // 11) THE TIME MACHINE v3 — history as MATERIAL: filmstrip cards on a day-
    // separated spine, the life graph scrubber, hearing state, loading shimmer.
    {
        HistoryPanel hp;
        const juce::int64 now = juce::Time::currentTimeMillis() / 1000;

        // kept-material density grid: a motif with two carved breakdowns (like a real song)
        auto mkGrid = [] (const char* motif)
        {
            juce::String s;
            const int n = (int) strlen (motif);
            for (int i = 0; i < 240; ++i)
            {
                const bool brk = (i > 58 && i < 76) || (i > 166 && i < 184);
                s << (brk ? '0' : motif[i % n]);
            }
            return s;
        };
        auto mkPts = [] (float step, int pitch, int range, float len, float from, float to)
        {
            std::vector<HistoryPanel::Pt> v;
            int k = 0;
            for (float b = from; b < to; b += step, ++k)
                v.push_back ({ b, len, pitch + (k * 5) % juce::jmax (1, range) });
            return v;
        };
        auto strip = [] (const char* nm, juce::StringArray grid,
                         std::vector<HistoryPanel::Pt> a = {},
                         std::vector<HistoryPanel::Pt> r = {}, bool pr = false)
        {
            HistoryPanel::Strip s;
            s.name = nm; s.grid = std::move (grid);
            s.added = std::move (a); s.removed = std::move (r); s.propChange = pr;
            return s;
        };
        auto mk = [&] (const char* sha, const char* age, juce::int64 epoch, const char* subj,
                       int kind, int a, int r, juce::StringArray touched,
                       std::vector<HistoryPanel::Strip> strips, int mass)
        {
            HistoryPanel::Row row;
            row.sha = sha; row.age = age; row.epoch = epoch; row.subject = subj;
            row.song = "untitled_1"; row.kind = kind; row.added = a; row.removed = r;
            row.touched = std::move (touched); row.stats = true;
            row.strips = std::move (strips); row.beats = 96.0f; row.mass = mass;
            row.path = "songs/untitled_1.json";
            return row;
        };

        const juce::String kickG = mkGrid ("f00e"), snareG = mkGrid ("00e0"),
                           hatG = mkGrid ("4343"), bassG = mkGrid ("7007"),
                           padG = mkGrid ("3333"), leadG = mkGrid ("0560");
        std::vector<HistoryPanel::Row> rows {
            mk ("ed18bbe", "15 minutes ago", now - 900,
                "accept proposal on untitled_1: (ui)", 0, 869, 3016, { "lead" },
                { strip ("kick", { kickG }), strip ("snare", { snareG }),
                  strip ("hats", { hatG, hatG, hatG }), strip ("bass", { bassG }),
                  strip ("pad", { padG, padG, padG }),
                  strip ("lead", { leadG, leadG, leadG },
                         mkPts (2.0f, 74, 9, 1.4f, 2.0f, 94.0f),
                         mkPts (0.5f, 70, 14, 0.4f, 0.0f, 96.0f), true) },
                18771),
            mk ("9c21af0", "6 hours ago", now - 6 * 3600,
                "reject take on untitled_1: too bright, lost the groove [1353 notes]",
                3, 1353, 0, { "lead", "pad" },
                { strip ("pad", { padG, padG, padG }, mkPts (1.0f, 55, 12, 0.9f, 0.0f, 96.0f)),
                  strip ("lead", { leadG, leadG, leadG }, mkPts (0.75f, 76, 10, 0.5f, 8.0f, 88.0f)) },
                20124),
            mk ("254d95c", "9 hours ago", now - 9 * 3600,
                "accept proposal on untitled_1: (ui)", 0, 223, 0,
                { "goabass", "hats", "kick", "riser", "snare" },
                { strip ("kick", { kickG }, mkPts (4.0f, 36, 1, 0.3f, 64.0f, 96.0f)),
                  strip ("snare", { snareG }, mkPts (8.0f, 38, 1, 0.3f, 66.0f, 96.0f)),
                  strip ("hats", { hatG, hatG, hatG }, mkPts (1.0f, 42, 3, 0.2f, 64.0f, 96.0f)),
                  strip ("bass", { bassG }, {}, {}, true),
                  strip ("pad", { padG, padG, padG }),
                  strip ("lead", { leadG, leadG, leadG }, {}, {}, true) },
                20918),
            mk ("77b01c2", "9 hours ago", now - 9 * 3600 - 1800,
                "revise take on untitled_1: darker, more sub", 4, 41, 12, { "bass" },
                { strip ("bass", { bassG }, mkPts (2.0f, 33, 5, 1.6f, 0.0f, 80.0f),
                                            mkPts (13.0f, 45, 3, 0.7f, 0.0f, 80.0f)) },
                20736),
            mk ("58fc565", "yesterday", now - 30 * 3600,
                "accept proposal on untitled_1: (ui)", 0, 614, 265,
                { "goaarp", "goabass", "hats", "kick", "snare" },
                { strip ("kick", { kickG }), strip ("snare", { snareG }),
                  strip ("hats", { hatG, hatG, hatG },
                         mkPts (3.0f, 42, 3, 0.2f, 32.0f, 64.0f),
                         mkPts (7.0f, 44, 2, 0.2f, 0.0f, 32.0f)),
                  strip ("bass", { bassG }) },
                20695),
            mk ("bd1e5d2", "2 days ago", now - 50 * 3600,
                "untitled_1: born from a prompt", 0, 20346, 0,
                { "acid", "bass", "kick", "pad", "snare" },
                { strip ("kick", {}, mkPts (1.0f, 36, 1, 0.3f, 0.0f, 96.0f)),
                  strip ("snare", {}, mkPts (2.0f, 38, 1, 0.3f, 1.0f, 96.0f)),
                  strip ("bass", {}, mkPts (0.5f, 33, 7, 0.4f, 0.0f, 96.0f)),
                  strip ("pad", {}, mkPts (4.0f, 57, 12, 3.5f, 0.0f, 96.0f)) },
                20346),
        };
        const juce::StringArray chips { "kick", "snare", "hats", "bass", "acid", "pad", "lead", "goabass" };
        hp.setRows (rows, "untitled_1", false, "", chips);
        savePng (hp, 980, HistoryPanel::idealHeight, dir.getChildFile ("time_machine.png"));
        savePng (hp, 1460, HistoryPanel::idealHeight, dir.getChildFile ("time_machine_wide.png"));

        hp.setActive ("254d95c");                    // HEARING a version: green card + bars
        for (int i = 0; i < 7; ++i) hp.tick();
        savePng (hp, 980, HistoryPanel::idealHeight, dir.getChildFile ("time_machine_active.png"));

        hp.setActive ({});
        hp.setFilter ("lead");                       // one lane's story
        savePng (hp, 980, HistoryPanel::idealHeight, dir.getChildFile ("time_machine_lane.png"));
        hp.setFilter ({});

        auto loading = rows;                         // the quick git pass: shimmer strips
        for (auto& r : loading) { r.stats = false; r.strips.clear(); r.mass = 0; }
        hp.setRows (loading, "untitled_1", false, "", chips);
        for (int i = 0; i < 9; ++i) hp.tick();
        savePng (hp, 980, HistoryPanel::idealHeight, dir.getChildFile ("time_machine_loading.png"));

        hp.setRows (rows, "untitled_1", true,
                    "212 commits - 47 accepts - 11 songs - the whole DAW so far", chips);
        savePng (hp, 980, HistoryPanel::idealHeight, dir.getChildFile ("time_machine_all.png"));
    }
    // 12) PHANTOM GLASS — frosted panes over fake lanes (composing tint)
    {
        struct Stage : juce::Component
        {
            GhostGlass glass;
            Stage()
            {
                addAndMakeVisible (glass);
                glass.setPanes ({ { 10, 12, 940, 66 }, { 10, 86, 940, 66 } }, GhostGlass::composing);
            }
            void resized() override { glass.setBounds (getLocalBounds()); }
            void paint (juce::Graphics& g) override
            {
                g.fillAll (theme::bg);
                for (int y : { 12, 86, 160 })         // fake lanes under the glass
                {
                    g.setColour (theme::lane);
                    g.fillRoundedRectangle (10.0f, (float) y, 940.0f, 66.0f, 6.0f);
                    g.setColour (theme::grid);
                    for (int x = 30; x < 950; x += 40)
                        g.fillRect (x, y + 10, 14, 46);
                }
            }
        } stage;
        savePng (stage, 960, 238, dir.getChildFile ("phantom_glass.png"));
    }
    // 13) DRAG CHIP — the glass pill that rides every internal drag (never a
    //     whole-list snapshot again). Widths + colours on a dark stage.
    {
        struct Stage : juce::Component
        {
            void paint (juce::Graphics& g) override
            {
                g.fillAll (theme::bg);
                struct Row { const char* label; juce::Colour c; };
                const Row rows[] = { { "Short Snare",        juce::Colour (0xff7ddc8a) },
                                     { "accordion",          theme::accent },
                                     { "Deep Cut Snare TAL", juce::Colour (0xffe0b34c) },
                                     { "a_very_long_sound_name_that_clamps", theme::warn } };
                int y = 12;
                for (auto& r : rows)
                {
                    const auto img = theme::dragChip (r.label, r.c);
                    g.drawImage (img.getImage(), juce::Rectangle<float> (12.0f, (float) y,
                                     (float) img.getScaledBounds().getWidth(),
                                     (float) img.getScaledBounds().getHeight()));
                    y += 34;
                }
            }
        } stage;
        savePng (stage, 300, 152, dir.getChildFile ("drag_chip.png"));
    }
    std::cout << "[uismoke] done -> " << dir.getFullPathName() << "\n";
    return 0;
}
