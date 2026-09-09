#!/usr/bin/env python3
"""Build the Inter + Equinor typography tokens, one DTCG file per density.

Runs the three typography skills' scripts as libraries, once per step where a
skill's CLI takes one value per run (the x-height correction and the matched
weights depend on the step's optical size), and assembles their output into
one token file per density. Every number is derived here from the font files
and the scale constants; nothing is typed in.

  python build.py --equinor /path/to/EquinorVariable-VF.woff2 [--out .]

Needs the fontTools venv the skills document (fonttools, brotli). Inter is the
copy bundled with typography-weight-matching; Equinor is fetched from the EDS
CDN by the caller and never committed (its licence forbids redistribution).
"""
import argparse, datetime, hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for skill in ("typography-scale", "typography-x-height-alignment", "typography-weight-matching"):
    sys.path.insert(0, str(ROOT / "skills" / skill / "scripts"))
import scale as SC          # noqa: E402  typography-scale
import xheight as XH        # noqa: E402  typography-x-height-alignment
import stem as ST           # noqa: E402  typography-weight-matching

NS, NS_FIGMA = SC.NS, SC.NS_FIGMA
INTER = ROOT / "skills/typography-weight-matching/assets/fonts/Inter.woff2"
TIERS = {"lighter": 300, "normal": 400, "bolder": 600}      # Inter's chosen tiers (weight-matching §2)
OPSZ_RANGE = (14, 32)                                         # Inter's optical-size axis


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clamp(v, lo, hi):
    return min(max(v, lo), hi)


class Measure:
    """Memoised measurements, so 30 steps × 3 tiers do not re-instance the fonts."""

    def __init__(self, equinor):
        self.eq = str(equinor)
        self.inter = str(INTER)
        self.eq_curve = ST.curve(self.eq)                      # stem by weight, sampled once
        self.eq_x = XH.metrics(self.eq, {"wght": 400})
        self._x, self._stem, self._side, self._eq_side = {}, {}, {}, {}

    def inter_x(self, opsz):
        if opsz not in self._x:
            self._x[opsz] = XH.metrics(self.inter, {"wght": 400, "opsz": opsz})
        return self._x[opsz]

    def inter_stem(self, wght, opsz):
        k = (wght, opsz)
        if k not in self._stem:
            self._stem[k] = ST.stem(ST.at(self.inter, {"wght": wght, "opsz": opsz}))
        return self._stem[k]

    def inter_side(self, wght, opsz):
        k = (wght, opsz)
        if k not in self._side:
            self._side[k] = ST.side_space(self.inter, wght, opsz)
        return self._side[k]

    def eq_side(self, wght):
        if wght not in self._eq_side:
            self._eq_side[wght] = ST.side_space(self.eq, wght)
        return self._eq_side[wght]

    def match(self, wght, opsz, correction):
        """stem.match(), with the target curve cached: the reference stem at (wght, opsz)
        divided by the correction, inverted on Equinor's curve, refined once."""
        goal = self.inter_stem(wght, opsz) / correction
        pts = self.eq_curve
        found = ST.invert(pts, goal)
        if found is None:
            return None
        lo, hi = pts[0][0], pts[-1][0]
        for (wa, sa), (wb, sb) in zip(pts, pts[1:]):
            if wa <= found <= wb and sb != sa:
                slope = (sb - sa) / (wb - wa)
                measured = ST.stem(ST.at(self.eq, {"wght": found}))
                found = clamp(found + (goal - measured) / slope, lo, hi)
                break
        return round(found, 1)


def build(density, m, today):
    base = SC.DENSITIES[density]
    out = SC.tokens(density)["typography"]                  # font-size and line-height, both curves
    fig = lambda scopes: {"collection": "Typography", "mode": density, "scopes": scopes}

    # CSS expressions beside the derived values
    for i, s in enumerate(SC.STEPS):
        out["font-size"][s]["$extensions"][NS]["css"] = (
            f"round(calc(var(--_base) * pow(2, {i - SC.STEPS.index(SC.BASE_STEP)}/{SC.STEPS_PER_OCTAVE})), {SC.SIZE_SNAP_REM}rem)")
        out["font-size"][s]["$extensions"][NS]["px"] = SC.clean(out["font-size"][s]["$value"]["value"] * SC.ROOT_PX)
        for c, (mx, drop) in SC.CURVES.items():
            out["line-height"][s][c]["$extensions"][NS]["css"] = (
                f"round(calc(var(--font-size-{s}) * ({mx} - pow({i}/{len(SC.STEPS) - 1}, 3) * {drop})), {SC.LINE_HEIGHT_SNAP_PX}px)")

    corr_group, disp, w_eq, ls_eq = {}, {}, {t: {} for t in TIERS}, {t: {} for t in TIERS}
    corr_values = []
    for i, s in enumerate(SC.STEPS):
        rem = out["font-size"][s]["$value"]["value"]
        px = SC.clean(rem * SC.ROOT_PX)
        opsz = clamp(px, *OPSZ_RANGE)
        xi = m.inter_x(opsz)
        corr = round(xi["xRatio"] / m.eq_x["xRatio"], 6)
        corr_values.append(corr)
        corr_group[s] = {"$type": "number", "$value": corr, "$extensions": {
            NS: {"derived": {"expression": "referenceXRatio / selfXRatio",
                             "inputs": {"reference": "{typography.font-family.text}", "referenceXRatio": xi["xRatio"],
                                        "selfXRatio": m.eq_x["xRatio"]}},
                 "metrics": {"family": "Equinor", "unitsPerEm": m.eq_x["unitsPerEm"], "xHeight": m.eq_x["xHeight"],
                             "reference": {"family": "Inter", "unitsPerEm": xi["unitsPerEm"], "xHeight": xi["xHeight"],
                                           "instance": {"opsz": opsz, "wght": 400}},
                             "instance": {"wght": 400}, "method": "OS/2.sxHeight", "extractedAt": today},
                 "step": s, "density": density,
                 "note": "Inter's x-height moves with its opsz axis; this is the correction at this step's rendered size"}}}
        drem = SC.clean(SC.css_round(rem * corr, SC.SIZE_SNAP_REM))
        disp[s] = {"$type": "dimension", "$value": SC.dim(drem, "rem"), "$extensions": {
            NS: {"derived": {"expression": f"round(fontSize * correction, {SC.SIZE_SNAP_REM}rem)",
                             "inputs": {"fontSize": f"{{typography.font-size.{s}}}",
                                        "correction": f"{{typography.x-height-correction.display.{s}}}",
                                        "correctionValue": corr}},
                 "css": f"round(calc(var(--font-size-{s}) * {corr}), {SC.SIZE_SNAP_REM}rem)",
                 "px": SC.clean(drem * SC.ROOT_PX), "step": s, "family": "Equinor", "density": density,
                 "lineHeight": f"{{typography.line-height.{s}}}",
                 "note": "baked: Figma and React Native cannot evaluate the expression; the CSS may use either"},
            NS_FIGMA: fig(["FONT_SIZE"])}}
        for tier, wght in TIERS.items():
            matched = m.match(wght, opsz, corr)
            if matched is None:
                w_eq[tier][s] = {"$type": "fontWeight", "$value": None, "$extensions": {NS: {
                    "warning": f"Inter {wght} at opsz {opsz} has a stem no weight on Equinor's axis reaches"}}}
                continue
            w_eq[tier][s] = {"$type": "fontWeight", "$value": matched, "$extensions": {
                NS: {"derived": {"expression": "weight where stem(Equinor) = stem(Inter @ tier, opsz) / correction",
                                 "inputs": {"tier": wght, "referenceStemEm": round(m.inter_stem(wght, opsz), 6),
                                            "correction": f"{{typography.x-height-correction.display.{s}}}",
                                            "correctionValue": corr}},
                     "metrics": {"glyph": "l", "method": "outline:mid-height-stem",
                                 "instance": {"opsz": opsz, "wght": wght}, "extractedAt": today},
                     "css": f"font-weight: {matched};", "step": s, "tier": tier, "density": density},
                NS_FIGMA: fig(["FONT_WEIGHT"])}}
            ls = ST.letter_spacing(m.inter, m.eq, wght, matched, corr, opsz, px)
            em = ls["letterSpacingEm"]
            ls_eq[tier][s] = {"$type": "number", "$value": em, "$extensions": {
                NS: {"derived": {"expression": "reference.sideSpaceEm / correction - target.sideSpaceEm",
                                 "inputs": {"reference": {k: ls["reference"][k] for k in ("sideSpaceEm", "weight", "opsz")},
                                            "target": {k: ls["target"][k] for k in ("sideSpaceEm", "weight")},
                                            "correction": f"{{typography.x-height-correction.display.{s}}}",
                                            "correctionValue": corr}},
                     "metrics": {"glyphs": "a-z", "method": "outline:advance-minus-ink",
                                 "instance": {"opsz": opsz, "wght": wght}, "extractedAt": today},
                     "units": {"em": em, "percent": round(em * 100, 4),
                               "px": {"at": ls["targetPx"], "value": ls["letterSpacingPx"]}},
                     "css": f"letter-spacing: {em}em;", "step": s, "tier": tier, "density": density,
                     "note": "em of Equinor's own size; Figma takes percent, React Native px"},
                NS_FIGMA: {**fig(["LETTER_SPACING"]), "unit": "PERCENT", "value": round(em * 100, 4)}}}

    lo, hi = min(corr_values), max(corr_values)
    corr_group["$extensions"] = {NS: {"drift": {"axis": "opsz", "sampledAt": [SC.clean(out["font-size"][s]["$value"]["value"] * SC.ROOT_PX) for s in SC.STEPS],
                                                "range": [lo, hi], "max": round(hi / lo - 1, 4)}}}
    w_inter = {tier: {"$type": "fontWeight", "$value": wght, "$extensions": {
        NS: {"note": "chosen tier on Inter's axis, the reference; Equinor's tiers are matched to it per step",
             "css": f"font-weight: {wght};"},
        NS_FIGMA: fig(["FONT_WEIGHT"])}} for tier, wght in TIERS.items()}

    return {"typography": {
        "font-family": {"text": {"$type": "fontFamily", "$value": "Inter"},
                        "display": {"$type": "fontFamily", "$value": "Equinor"}},
        "font-size": out["font-size"],
        "line-height": out["line-height"],
        "x-height-correction": {"display": corr_group},
        "font-size-display": disp,
        "font-weight": {"Inter": w_inter, "Equinor": w_eq},
        "letter-spacing": {"Equinor": ls_eq},
    }}


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--equinor", required=True, help="path to EquinorVariable-VF.woff2 (from the EDS CDN; not committed)")
    p.add_argument("--out", default=str(Path(__file__).resolve().parent))
    a = p.parse_args(argv)
    m = Measure(a.equinor)
    today = datetime.date.today().isoformat()
    meta = {"fonts": {"Inter": {"path": "skills/typography-weight-matching/assets/fonts/Inter.woff2", "sha256": sha(INTER)},
                      "Equinor": {"path": "https://cdn.eds.equinor.com/font/EquinorVariable-VF.woff2", "sha256": sha(a.equinor)}},
            "builtAt": today, "builder": "demo/typography-tokens/build.py",
            "skills": ["typography-scale", "typography-x-height-alignment", "typography-weight-matching"]}
    for d in SC.DENSITIES:
        doc = build(d, m, today)
        doc["$extensions"] = {NS: meta}
        path = Path(a.out) / f"typography.{d}.tokens.json"
        path.write_text(json.dumps(doc, indent=2) + "\n")
        print(path, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
