// Keymap.h - THE SPINE (docs/THE_HANDS.md H22): ONE keymap object. keyPressed
// dispatches through it, the '?' gesture map RENDERS from it (no hand-mirrored
// help table — that double-truth is dead), and ~/.config/sotadaw/keymap.json
// overlays it (the lane_heights.json precedent). Dialects (H23) will ship as
// data files over this registry. An action = id + producer-name + help placement
// + chord + when-guard + run. Letter keys match by TEXT CHAR (JUCE keycodes are
// case-hostile — the existing 'l'/'g' bindings taught us); chorded keys match by
// KeyPress. ASCII-only strings (JUCE panel law).
#pragma once

struct KeymapAction
{
    juce::String id, name, group;     // group = help-card section title
    int helpCol = 0;                  // help-card column 0..2
    juce::KeyPress key;               // chorded binding (unused when ch != 0)
    juce::juce_wchar ch = 0;          // plain-letter binding: match the text char
    juce::String keyLabel;            // painted label ("ctrl+B", "space", ...)
    bool hidden = false;              // in the map's spirit but not its ink (scene 2..8)
    std::function<bool()> when;       // nullptr = always
    std::function<void()> run;
};

class Keymap
{
public:
    KeymapAction& add (juce::String id, juce::String name, juce::String group, int col,
                       juce::KeyPress def, juce::juce_wchar ch, juce::String label,
                       std::function<bool()> when, std::function<void()> run)
    {
        acts.push_back ({ std::move (id), std::move (name), std::move (group), col,
                          def, ch, std::move (label), false, std::move (when), std::move (run) });
        return acts.back();
    }

    void clear() { acts.clear(); }           // dialect switch rebuilds the registry

    // Rebind one action by chord description ("ctrl + l", "f5", "tab", single letters
    // and punctuation take the text-char path). THE STEAL: one binding, one action —
    // any other action holding that chord is unbound (dialects take keys on purpose).
    // The action's when-guard and run stay untouched. Returns false on unknown id.
    bool assign (const juce::String& id, const juce::String& desc)
    {
        KeymapAction* target = nullptr;
        for (auto& a : acts)
            if (a.id == id) { target = &a; break; }
        if (target == nullptr) return false;
        const auto s = desc.trim();
        juce::juce_wchar ch = 0;
        juce::KeyPress kp;
        if (s.length() == 1 && ! juce::CharacterFunctions::isDigit (s[0]))
            ch = juce::CharacterFunctions::toLowerCase (s[0]);
        else
        {
            kp = juce::KeyPress::createFromDescription (s);
            if (! kp.isValid()) return false;
        }
        for (auto& a : acts)                 // steal: unbind whoever held this chord
            if (&a != target
                && ((ch != 0 && a.ch == ch) || (ch == 0 && a.key.isValid() && a.key == kp)))
            { a.ch = 0; a.key = {}; }
        target->ch = ch;
        target->key = kp;
        target->keyLabel = s;
        return true;
    }

    // A dialect pack (app/keymaps/<name>.json) = {"action.id": "chord", ...}; keys
    // starting with "_" are notes. Applied OVER the canonical map, UNDER the user
    // overlay (the user's own rebinds always win). Missing file = 0, never fatal.
    int loadDialect (const juce::File& f)
    {
        if (! f.existsAsFile()) return 0;
        const auto v = juce::JSON::parse (f.loadFileAsString());   // OWN the var: getDynamicObject()
        auto* o = v.getDynamicObject();                            // on a temporary = use-after-free
        if (o == nullptr) return 0;
        int n = 0;
        for (auto& p : o->getProperties())
            if (! p.name.toString().startsWith ("_"))
                n += assign (p.name.toString(), p.value.toString()) ? 1 : 0;
        return n;
    }

    // ~/.config/sotadaw/keymap.json = {"action.id": "ctrl + l", ...} in juce
    // KeyPress::createFromDescription grammar ("f5", "shift + cursor left", "delete").
    // "_"-prefixed keys are reserved (e.g. "_dialect"). Unknown ids ignored, never fatal.
    int loadUserOverlay()
    {
        const auto f = juce::File ("~/.config/sotadaw/keymap.json");
        if (! f.existsAsFile()) return 0;
        const auto v = juce::JSON::parse (f.loadFileAsString());   // OWN the var (lifetime law)
        auto* o = v.getDynamicObject();
        if (o == nullptr) return 0;
        int n = 0;
        for (auto& p : o->getProperties())
            if (! p.name.toString().startsWith ("_"))
                n += assign (p.name.toString(), p.value.toString()) ? 1 : 0;
        return n;
    }

    bool handle (const juce::KeyPress& k) const
    {
        const auto tc = juce::CharacterFunctions::toLowerCase (k.getTextCharacter());
        const bool chorded = k.getModifiers().isCommandDown() || k.getModifiers().isCtrlDown()
                          || k.getModifiers().isAltDown();
        for (auto& a : acts)
        {
            const bool hit = a.ch != 0 ? (! chorded && tc == a.ch)
                                       : (a.key.isValid() && k == a.key);
            if (hit && (a.when == nullptr || a.when()))
            {
                a.run();
                return true;
            }
        }
        return false;
    }

    const std::vector<KeymapAction>& actions() const { return acts; }

private:
    std::vector<KeymapAction> acts;
};
