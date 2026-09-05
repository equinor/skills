#!/usr/bin/env python3
"""Measure stem width from glyph outlines, and match weights across a font pair.

Usage:
  python stem.py                                     # bundled Inter, default weights
  python stem.py FONT.ttf --weights 300,400,500      # one face, several weights
  python stem.py REFERENCE.ttf TARGET.ttf --match 300,400,500 --correction 1.137288
  python stem.py REFERENCE.ttf TARGET.ttf --tracking --at 400,460
  python stem.py REF.ttf TARGET.ttf --match 400 --format tokens --display Equinor

`--format tokens` emits DTCG tokens with the derivation attached; `json` (the
default) is the raw measurement. Every result records the files it came from,
by path and sha256.

Stem width is read at the vertical midpoint of the glyph, not from its bounding
box. The two differ at the extremes of a weight axis, where flare or overshoot
widens the box without widening the stroke.

Requires: pip install fonttools brotli   (brotli is what opens .woff2)
"""
import sys, json, hashlib, argparse, datetime
from pathlib import Path
try:
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.boundsPen import BoundsPen
    import brotli  # noqa: F401  — what opens .woff2
except ImportError as e:                       # exit 2 with instructions, not a traceback
    sys.stderr.write(f"missing dependency: {e.name}\n"
                     "install fontTools and brotli in the project's Python environment, e.g. at the\n"
                     "project root: python3 -m venv .venv && .venv/bin/pip install fonttools brotli\n")
    sys.exit(2)

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
            # TrueType routinely chains off-curve points with implied on-curve
            # midpoints between them. Expand to individual quadratic segments.
            ctrl, end = list(pts[:-1]), pts[-1]
            if end is None:                      # all-off-curve closed contour
                end = ctrl[0]
            pieces = []
            for i, c in enumerate(ctrl):
                nxt = end if i == len(ctrl) - 1 else (
                    (c[0] + ctrl[i + 1][0]) / 2, (c[1] + ctrl[i + 1][1]) / 2)
                pieces.append((c, nxt))
            prev = cur
            for c, e in pieces:
                start = prev
                for i in range(1, FLATTEN + 1):
                    p = _quad(start, c, e, i / FLATTEN)
                    segs.append((prev, p)); prev = p
            cur = end
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


def curve(path, samples=11):
    """Stem width across the target's weight axis, sampled once.

    Instancing a font is expensive, so sample the curve once and invert by
    interpolation rather than re-instancing inside a search loop. Eleven
    samples over the axis plus one measured correction per tier (see match())
    lands within about a tenth of a weight unit.
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
    """Target weights whose stems match the reference at the same perceived size.

    The sampled curve gives a first estimate by interpolation; one real
    measurement at that estimate, corrected along the local slope, takes the
    residual from about a weight unit to a few hundredths. One instancing per
    tier is the cost."""
    points = curve(target_path)
    out = {}
    for w in ref_weights:
        loc = {"wght": w}
        if opsz is not None:
            loc["opsz"] = opsz
        goal = stem(at(ref_path, loc)) / correction
        found = invert(points, goal)
        if found is not None:
            lo, hi = points[0][0], points[-1][0]
            for (wa, sa), (wb, sb) in zip(points, points[1:]):
                if wa <= found <= wb and sb != sa:
                    slope = (sb - sa) / (wb - wa)
                    measured = stem(at(target_path, {"wght": found}))
                    found = min(max(found + (goal - measured) / slope, lo), hi)
                    break
        key = int(w) if float(w).is_integer() else w
        out[key] = None if found is None else round(found, 1)
    return out


NS = "com.equinor.typography"
NS_FIGMA = "com.equinor.figma"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source(path):
    return {"path": str(path), "sha256": sha256(path)}


def demo_font():
    """The bundled Inter, looked up next to this script."""
    here = Path(__file__).resolve().parent
    for base in (here.parent, here, Path.cwd()):
        f = base / "assets/fonts/Inter.woff2"
        if f.exists():
            return str(f)
    raise SystemExit("No font given and the bundled Inter was not found; pass a font path.")


def today():
    return datetime.date.today().isoformat()


def weight_tokens(ref, target, matches, correction, correction_token, display, opsz, snap=None):
    """DTCG fontWeight tokens: the target weight that matches the reference at each tier.

    `snap` rounds the value to a multiple (React Native takes hundreds only) and
    records what was measured and what the rounding cost, so nobody later reads
    500 as the measurement."""
    fam = display or "display"
    out = {}
    for tier, w in matches.items():
        if w is None:
            continue
        value = w if not snap else int(round(w / snap) * snap)
        inputs = {"tier": tier, "correction": correction_token or correction,
                  "correctionValue": correction,
                  "instance": ({"opsz": opsz} if opsz is not None else {}) | {"wght": tier}}
        derived = {"expression": "stem(target, w) = stem(reference, tier) / correction", "inputs": inputs}
        if snap:
            derived["expression"] += f"; value = round(w / {snap}) * {snap}"
            derived["measured"] = w
            derived["residual"] = round(value - w, 1)
        out[str(tier)] = {"$type": "fontWeight", "$value": value, "$extensions": {
            NS: {"derived": derived,
                 "metrics": {"reference": source(ref), "target": source(target), "glyph": "l",
                             "method": "outline:mid-height-stem", "extractedAt": today()},
                 "family": fam},
            NS_FIGMA: {"collection": "Typography", "scopes": ["FONT_WEIGHT"]}}}
    return {"typography": {"font-weight": {fam: out}}}


def tracking_tokens(ref, target, a, b, factor, display):
    fam = display or "display"
    return {"typography": {"letter-spacing-port-factor": {fam: {
        "$type": "number", "$value": factor, "$extensions": {
            NS: {"derived": {"expression": "target.sideSpaceEm / reference.sideSpaceEm",
                             "inputs": {"reference": a, "target": b}},
                 "metrics": {"reference": source(ref), "target": source(target),
                             "glyphs": "a-z", "method": "outline:advance-minus-ink",
                             "extractedAt": today()},
                 "family": fam}}}}}}


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="Measure stem width from glyph outlines, and match weights across a font pair.",
        epilog="With no fonts given, measures the bundled Inter.")
    p.add_argument("fonts", nargs="*", metavar="FONT", help="one face, or REFERENCE then TARGET")
    p.add_argument("--weights", default="300,400,500,700", metavar="W,W,...",
                   help="weights to measure a single face at (default 300,400,500,700)")
    p.add_argument("--match", metavar="W,W,...", help="reference tiers to find matching target weights for")
    p.add_argument("--correction", type=float, default=1.0, metavar="FACTOR",
                   help="x-height correction applied to the target (typography-x-height-alignment)")
    p.add_argument("--correction-token", metavar="ALIAS", help="DTCG alias of the correction token")
    p.add_argument("--opsz", type=float, metavar="PX", help="pin the reference's optical size when matching")
    p.add_argument("--tracking", action="store_true", help="side space of both faces and the port factor")
    p.add_argument("--at", default="400,400", metavar="WREF,WTARGET", help="weights for --tracking (matched!)")
    p.add_argument("--format", choices=["json", "tokens"], default="json")
    p.add_argument("--display", metavar="FAMILY", help="name of the target family, for token paths")
    p.add_argument("--snap", type=int, metavar="N",
                   help="round matched weights to a multiple of N and record the residual (React Native: 100)")
    a = p.parse_args(argv)
    if (a.match or a.tracking) and len(a.fonts) != 2:
        p.error("--match and --tracking need REFERENCE and TARGET")
    if a.format == "tokens" and not (a.match or a.tracking):
        p.error("--format tokens applies to --match or --tracking; a single-face measurement is not a token")
    return a, p


def main(argv):
    a, p = parse_args(argv)
    floats = lambda t: [float(x) for x in t.split(",")]
    if a.tracking:
        ref, target = a.fonts
        wa, wb = floats(a.at)
        sa, sb = side_space(ref, wa), side_space(target, wb)
        sa["weight"], sb["weight"] = wa, wb
        factor = round(sb["sideSpaceEm"] / sa["sideSpaceEm"], 3)
        if a.format == "tokens":
            print(json.dumps(tracking_tokens(ref, target, sa, sb, factor, a.display), indent=2))
        else:
            print(json.dumps({"reference": {**source(ref), **sa}, "target": {**source(target), **sb},
                              "portFactor": factor}, indent=2))
    elif a.match:
        ref, target = a.fonts
        matches = match(ref, target, floats(a.match), a.correction, opsz=a.opsz)
        for tier, v in matches.items():
            if v is None:
                print(f"warning: tier {tier} falls outside the target's weight axis (null)", file=sys.stderr)
        if a.format == "tokens":
            print(json.dumps(weight_tokens(ref, target, matches, a.correction, a.correction_token,
                                           a.display, a.opsz, a.snap), indent=2))
        else:
            print(json.dumps({"reference": source(ref), "target": source(target), "correction": a.correction,
                              "opsz": a.opsz, "matches": matches}, indent=2))
    else:
        if len(a.fonts) > 1:
            p.error("one face for --weights; add --match or --tracking for a pair")
        path = a.fonts[0] if a.fonts else demo_font()
        if not a.fonts:
            print("No font given — measuring the bundled Inter.", file=sys.stderr)
        info = axis_info(path)
        info.update(source(path))
        info["stem"] = {int(w): round(stem(at(path, {"wght": w})), 6) for w in floats(a.weights)}
        print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
