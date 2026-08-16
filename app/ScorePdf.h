// THE PRINT DOOR (SCORE II, 2026-08-02) — a minimal, dependency-free PDF writer:
// one JPEG image per A4 page (DCTDecode XObject). Enough PDF to open everywhere,
// small enough to audit. ScorePage::exportPdf() renders the pages; this file only
// knows bytes.
#pragma once
#include <juce_graphics/juce_graphics.h>
#include <vector>

namespace sotadaw
{

inline bool writeScorePdf (const std::vector<juce::Image>& pages, const juce::File& out)
{
    if (pages.empty()) return false;
    juce::MemoryOutputStream pdf;
    std::vector<juce::int64> offsets;                 // object byte offsets, 1-based ids
    auto obj = [&pdf, &offsets] (const juce::String& body)
    {
        offsets.push_back ((juce::int64) pdf.getPosition());
        pdf << juce::String ((int) offsets.size()) << " 0 obj\n" << body << "\nendobj\n";
    };
    auto objStream = [&pdf, &offsets] (const juce::String& dict, const void* data, size_t size)
    {
        offsets.push_back ((juce::int64) pdf.getPosition());
        pdf << juce::String ((int) offsets.size()) << " 0 obj\n" << dict << "\nstream\n";
        pdf.write (data, size);
        pdf << "\nendstream\nendobj\n";
    };

    pdf << "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n";
    const int n = (int) pages.size();
    juce::String kids;
    for (int i = 0; i < n; ++i) kids << juce::String (3 + 3 * i) << " 0 R ";
    obj ("<< /Type /Catalog /Pages 2 0 R >>");
    obj ("<< /Type /Pages /Kids [ " + kids + "] /Count " + juce::String (n) + " >>");
    for (int i = 0; i < n; ++i)
    {
        obj ("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] "
             "/Resources << /XObject << /Im0 " + juce::String (5 + 3 * i) + " 0 R >> >> "
             "/Contents " + juce::String (4 + 3 * i) + " 0 R >>");
        const juce::String content ("q 595.28 0 0 841.89 0 0 cm /Im0 Do Q");
        objStream ("<< /Length " + juce::String ((int) content.getNumBytesAsUTF8()) + " >>",
                   content.toRawUTF8(), (size_t) content.getNumBytesAsUTF8());
        juce::MemoryOutputStream jpg;
        juce::JPEGImageFormat fmt;
        fmt.setQuality (0.90f);
        if (! fmt.writeImageToStream (pages[(size_t) i], jpg)) return false;
        objStream ("<< /Type /XObject /Subtype /Image /Width "
                   + juce::String (pages[(size_t) i].getWidth())
                   + " /Height " + juce::String (pages[(size_t) i].getHeight())
                   + " /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length "
                   + juce::String ((int) jpg.getDataSize()) + " >>",
                   jpg.getData(), jpg.getDataSize());
    }
    const auto xref = (juce::int64) pdf.getPosition();
    pdf << "xref\n0 " << juce::String ((int) offsets.size() + 1) << "\n0000000000 65535 f \n";
    for (auto o : offsets)
    {
        auto s = juce::String (o);
        while (s.length() < 10) s = "0" + s;
        pdf << s << " 00000 n \n";
    }
    pdf << "trailer\n<< /Size " << juce::String ((int) offsets.size() + 1)
        << " /Root 1 0 R >>\nstartxref\n" << juce::String (xref) << "\n%%EOF\n";
    out.deleteFile();
    return out.replaceWithData (pdf.getData(), pdf.getDataSize());
}

} // namespace sotadaw
