#!/usr/bin/env python3
"""Measure stem width from glyph outlines, and match weights across a font pair.

Usage:
  python stem.py FONT.ttf --weights 300,400,500      # one face, several weights
  python stem.py REFERENCE.ttf TARGET.ttf --match 400 --correction 1.137288

Stem width is read at the vertical midpoint of the glyph, not from its bounding
box. The two differ at the extremes of a weight axis, where flare or overshoot
widens the box without widening the stroke.

Requires: pip install fonttools brotli   (brotli is what opens .woff2)
"""
import sys, json
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen

FLATTEN = 64          # line segments per curve; sub-unit precision at any upm


def _segments(pen_value, start):
    """Flatten a recorded outline into straight segments."""
    segs, cur = [], start
    for op, pts in pen_value:
        if op == "moveTo":
            cur = pts[0]
        elif op == "lineTo":
            segs.append((cur, pts[0])); cur = pts[0]
        elif op == "qCurveTo":
            prev = cur
            for i in range(1, FLATTEN + 1):
                t = i / FLATTEN
                p = _quad(cur, pts[0], pts[-1], t) if len(pts) == 2 else pts[-1]
                segs.append((prev, p)); prev = p
            cur = pts[-1]
        elif op == "curveTo":
            prev = cur
            for i in range(1, FLATTEN + 1):
                t = i / FLATTEN
                p = _cubic(cur, pts[0], pts[1], pts[2], t)
                segs.append((prev, p)); prev = p
            cur = pts[2]
        elif op == "closePath":
            pass
    return segs


def _quad(p0, p1, p2, t):
    u = 1 - t
    return (u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0],
            u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1])


def _cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])


def stem(font, char="l"):
    """Widest ink run across the glyph at its vertical midpoint, in em units."""
    upm = font["head"].unitsPerEm
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    name = cmap.get(ord(char))
    if not name:
        raise SystemExit(f"no glyph for {char!r}")

    bounds = BoundsPen(glyphs); glyphs[name].draw(bounds)
    if not bounds.bounds:
        raise SystemExit(f"glyph {char!r} has no outline")
    _, y0, _, y1 = bounds.bounds
    mid = (y0 + y1) / 2

    rec = RecordingPen(); glyphs[name].draw(rec)
    xs = []
    for (ax, ay), (bx, by) in _segments(rec.value, (0, 0)):
        if (ay - mid) * (by - mid) <= 0 and ay != by:          # crosses the line
            xs.append(ax + (mid - ay) / (by - ay) * (bx - ax))
    if len(xs) < 2:
        raise SystemExit(f"could not scan {char!r} at mid-height")
    xs.sort()
    runs = [(xs[i + 1] - xs[i]) for i in range(0, len(xs) - 1, 2)]
    return max(runs) / upm


def at(path, location):
    font = TTFont(path)
    if "fvar" in font and location:
        axes = {a.axisTag for a in font["fvar"].axes}
        loc = {k: v for k, v in location.items() if k in axes}
        if loc:
            instancer.instantiateVariableFont(font, loc, inplace=True)
    return font


def axis_info(path):
    font = TTFont(path, lazy=True)
    if "fvar" not in font:
        return {"variable": False, "axes": {}}
    return {"variable": True,
            "axes": {a.axisTag: [a.minValue, a.defaultValue, a.maxValue]
                     for a in font["fvar"].axes}}


def side_space(path, weight=400):
    """Mean side space as a fraction of advance, over lowercase a-z.

    What letter-spacing eats into. Two faces with different side space respond
    differently to the same em tracking.
    """
    font = at(path, {"wght": weight})
    upm, glyphs, cmap = font["head"].unitsPerEm, font.getGlyphSet(), font.getBestCmap()
    hmtx = font["hmtx"]
    adv = ink = 0
    for ch in "abcdefghijklmnopqrstuvwxyz":
        name = cmap.get(ord(ch))
        if not name:
            continue
        bounds = BoundsPen(glyphs); glyphs[name].draw(bounds)
        if not bounds.bounds:
            continue
        x0, _, x1, _ = bounds.bounds
        adv += hmtx[name][0]; ink += (x1 - x0)
    return {"advanceEm": round(adv / 26 / upm, 6),
            "inkEm": round(ink / 26 / upm, 6),
            "sideSpaceEm": round((adv - ink) / 26 / upm, 6),
            "sideSpaceShare": round((adv - ink) / adv, 6)}


def curve(path, samples=21):
    """Stem width across the target's weight axis, sampled once.

    Instancing a font is expensive, so sample the curve once and invert by
    interpolation rather than re-instancing inside a search loop.
    """
    axes = axis_info(path)["axes"]
    lo, _, hi = axes.get("wght", [300, 400, 700])
    step = (hi - lo) / (samples - 1)
    return [(lo + i * step, stem(at(path, {"wght": lo + i * step})))
            for i in range(samples)]


def invert(points, goal):
    """Weight at which the sampled curve reaches `goal`, or None if out of range."""
    for (wa, sa), (wb, sb) in zip(points, points[1:]):
        if (sa - goal) * (sb - goal) <= 0 and sa != sb:
            return wa + (goal - sa) / (sb - sa) * (wb - wa)
    return None


def match(ref_path, target_path, ref_weights, correction, opsz=None):
    """Target weights whose stems match the reference at the same perceived size."""
    points = curve(target_path)
    out = {}
    for w in ref_weights:
        loc = {"wght": w}
        if opsz is not None:
            loc["opsz"] = opsz
        goal = stem(at(ref_path, loc)) / correction
        found = invert(points, goal)
        out[int(w)] = None if found is None else round(found, 1)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    fonts = [a for a in args if not a.startswith("--")]
    def opt(name, default=None):
        return args[args.index(name) + 1] if name in args else default

    if "--tracking" in args:
        ref, target = fonts[0], fonts[1]
        # Compare at the MATCHED weights — side space shrinks as ink grows, so
        # measuring both at 400 misstates the ratio for an unmatched pair.
        wa, wb = [float(x) for x in opt("--at", "400,400").split(",")]
        a, b = side_space(ref, wa), side_space(target, wb)
        a["weight"], b["weight"] = wa, wb
        print(json.dumps({"reference": {"path": ref, **a},
                          "target": {"path": target, **b},
                          "portFactor": round(b["sideSpaceEm"] / a["sideSpaceEm"], 3)}, indent=2))
    elif "--match" in args:
        ref, target = fonts[0], fonts[1]
        corr = float(opt("--correction", "1.0"))
        ws = [float(x) for x in opt("--match", "400").split(",")]
        matches = match(ref, target, ws, corr,
                        opsz=float(opt("--opsz")) if opt("--opsz") else None)
        print(json.dumps({"reference": ref, "target": target,
                          "correction": corr, "matches": matches}, indent=2))
    else:
        path = fonts[0]
        info = axis_info(path)
        info["path"] = path
        info["stem"] = {int(w): round(stem(at(path, {"wght": float(w)})), 6)
                        for w in opt("--weights", "300,400,500,700").split(",")}
        print(json.dumps(info, indent=2))
