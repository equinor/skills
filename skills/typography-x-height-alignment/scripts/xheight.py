#!/usr/bin/env python3
"""Extract x-height metrics and derive the alignment correction.

Usage:
  python xheight.py                                   # bundled demo pair
  python xheight.py REFERENCE.ttf SECONDARY.woff2     # default instances
  python xheight.py --location wght=400 A.ttf B.ttf   # pinned instance
  python xheight.py --location opsz=14,wght=400 A.ttf B.ttf

The first font is the reference; every other font is corrected towards it.

Variable fonts are measured at a specific point on their axes, so the output
always records which one. A file's default instance is often not Regular —
Montserrat's is wght 100 — and x-height moves along the weight axis whenever
the font has an MVAR table, so a correction is only valid at the location it
was measured at.

Requires: pip install fonttools brotli   (brotli is what opens .woff2)
"""
import sys, json, hashlib
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib import instancer


def glyph_top(font, ch):
    """Fallback: the top of a glyph's bounding box, in font units."""
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    name = cmap.get(ord(ch))
    if not name:
        return None
    pen = BoundsPen(glyphs)
    glyphs[name].draw(pen)
    return pen.bounds[3] if pen.bounds else None


def metrics(path, location=None):
    font = TTFont(path)
    warnings = []

    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue)
            for a in font["fvar"].axes} if "fvar" in font else {}
    has_mvar = "MVAR" in font

    if axes:
        # Pin only the axes this font has, clamped to its own range.
        want = {t: v for t, v in (location or {}).items() if t in axes}
        for t in (location or {}):
            if t not in axes:
                warnings.append(f"has no {t} axis; --location {t} ignored")
        pinned = {}
        for tag, value in want.items():
            lo, _, hi = axes[tag]
            clamped = min(max(value, lo), hi)
            if clamped != value:
                warnings.append(
                    f"{tag}={value} is outside this font's range "
                    f"[{lo}, {hi}]; measured at {clamped}")
            pinned[tag] = clamped
        if pinned:
            instancer.instantiateVariableFont(font, pinned, inplace=True)
        instance = {t: pinned.get(t, axes[t][1]) for t in axes}
        unpinned = [t for t in axes if t not in pinned]
        if unpinned:
            note = ("; opsz cannot be pinned in CSS, see "
                    "references/optical-size.md" if "opsz" in unpinned else "")
            warnings.append(
                "axes left at their default: "
                + ", ".join(f"{t}={axes[t][1]:g}" for t in unpinned)
                + " — name them in --location if the pairing sets them" + note)
        if not pinned and axes.get("wght", (None, 400, None))[1] != 400:
            warnings.append(
                f"default instance is wght {axes['wght'][1]}, not 400 — "
                f"pass --location wght=400 unless you mean this weight")
        if has_mvar:
            warnings.append(
                "MVAR present: x-height varies along the axes, so this "
                "correction holds only at the instance above")
    else:
        instance = None
        if location:
            warnings.append("static font, no fvar table; --location ignored")

    upm = font["head"].unitsPerEm
    os2 = font["OS/2"]

    x, method = getattr(os2, "sxHeight", None), "OS/2.sxHeight"
    if not x or x <= 0:
        x, method = glyph_top(font, "x"), "measured:x-glyph-bounds"
        warnings.append("no usable OS/2.sxHeight; measured the 'x' glyph, "
                        "which includes overshoot on rounded designs")
    cap = getattr(os2, "sCapHeight", None)
    if not cap or cap <= 0:
        cap = glyph_top(font, "H")     # may still be None; the correction never uses it
    if not x:
        raise SystemExit(f"{path}: no usable x-height — is this a text font?")

    return {
        "family": font["name"].getDebugName(16) or font["name"].getDebugName(1),
        "nameID1": font["name"].getDebugName(1),   # often names the instance
        "instance": instance,
        "unitsPerEm": upm,
        "xHeight": x,
        "capHeight": cap,       # None if the font declares none and has no H
        "xRatio": round(x / upm, 6),
        "capRatio": None if not cap else round(cap / upm, 6),
        "extent": round((os2.sTypoAscender - os2.sTypoDescender) / upm, 6),
        "method": method,
        "source": str(path),
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "warnings": warnings,
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


def parse_args(argv):
    import argparse
    p = argparse.ArgumentParser(
        description="Extract x-height metrics and derive the alignment "
                    "correction. The first font is the reference.",
        epilog="With no fonts given, measures the bundled demo pair.")
    p.add_argument("fonts", nargs="*", metavar="FONT",
                   help="reference first, then the fonts corrected towards it")
    p.add_argument("--location", metavar="AXIS=VALUE[,AXIS=VALUE]",
                   help="pin variable-font axes, e.g. wght=400 or opsz=14,wght=400")
    a = p.parse_args(argv)
    location = None
    if a.location:
        try:
            location = {k: float(v) for k, v in
                        (kv.split("=", 1) for kv in a.location.split(","))}
        except ValueError:
            p.error(f"--location expects AXIS=VALUE pairs, got {a.location!r}")
    return a.fonts, location


paths, location = parse_args(sys.argv[1:])
if not paths:
    paths = demo_pair()
    print("No fonts given — measuring the bundled demo pair.", file=sys.stderr)

fonts = [metrics(p, location) for p in paths]
ref = fonts[0]
# Derive from the raw font units, not from the rounded xRatio above — rounding
# an intermediate and then dividing moves the last digit.
ref_ratio = ref["xHeight"] / ref["unitsPerEm"]
for f in fonts[1:]:
    f["correction"] = round(ref_ratio / (f["xHeight"] / f["unitsPerEm"]), 6)

for f in fonts:
    for w in f["warnings"]:
        print(f"warning: {f['family']}: {w}", file=sys.stderr)

print(json.dumps({"reference": ref["family"], "fonts": fonts}, indent=2))
