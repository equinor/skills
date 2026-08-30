#!/usr/bin/env python3
"""Extract x-height metrics and derive the alignment correction.

Usage:  python xheight.py [REFERENCE_FONT SECONDARY_FONT ...]
With no arguments, measures the bundled demo pair in ../assets/fonts.
Requires: pip install fonttools brotli   (brotli is what opens .woff2)
"""
import sys, json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

def glyph_top(font, ch):
    """Fallback: the top of a glyph's bounding box, in font units."""
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    name = cmap.get(ord(ch))
    if not name:
        return None
    pen = BoundsPen(glyphs)
    glyphs[name].draw(pen)
    return pen.bounds[3] if pen.bounds else None

def metrics(path):
    font = TTFont(path, fontNumber=0, lazy=True)   # fontNumber: .ttc collections
    upm = font["head"].unitsPerEm
    os2 = font["OS/2"]

    x = getattr(os2, "sxHeight", None)
    cap = getattr(os2, "sCapHeight", None)
    # OS/2 < v2 omits these, and some fonts ship 0 or -1 as a sentinel.
    if not x or x <= 0:
        x = glyph_top(font, "x")
    if not cap or cap <= 0:
        cap = glyph_top(font, "H")
    if not x:
        raise SystemExit(f"{path}: no usable x-height — is this a text font?")

    return {
        "family": font["name"].getDebugName(16) or font["name"].getDebugName(1),
        "unitsPerEm": upm,
        "xHeight": x,
        "capHeight": cap,
        "xRatio": round(x / upm, 6),
        "capRatio": round(cap / upm, 6),
        "extent": round((os2.sTypoAscender - os2.sTypoDescender) / upm, 6),
        "source": path,
    }

def demo_pair():
    """The bundled fonts, looked up next to this script and then in cwd."""
    names = ["Inter.woff2", "EBGaramond.woff2"]
    here = Path(__file__).resolve().parent
    for base in (here, here.parent, Path.cwd()):
        pair = [base / "assets/fonts" / n for n in names]
        if all(p.exists() for p in pair):
            return [str(p) for p in pair]
    raise SystemExit(
        "No fonts given, and the bundled demo pair was not found.\n"
        "Either run this from the skill directory, or pass fonts explicitly:\n"
        "  python xheight.py REFERENCE.otf SECONDARY.woff2"
    )

paths = sys.argv[1:]
if not paths:
    paths = demo_pair()
    print("No fonts given — measuring the bundled demo pair.", file=sys.stderr)

fonts = [metrics(p) for p in paths]
ref = fonts[0]
# Derive from the raw font units, not from the rounded xRatio above — rounding
# an intermediate and then dividing moves the last digit.
ref_ratio = ref["xHeight"] / ref["unitsPerEm"]
for f in fonts[1:]:
    f["correction"] = round(ref_ratio / (f["xHeight"] / f["unitsPerEm"]), 6)
print(json.dumps({"reference": ref["family"], "fonts": fonts}, indent=2))
