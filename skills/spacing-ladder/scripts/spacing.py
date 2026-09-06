#!/usr/bin/env python3
"""The EDS spacing ladder, inset proportions and optical padding — derived, not typed.

Usage:
  python spacing.py table [--density comfortable]        # the ladder and the relationships
  python spacing.py control --size md --proportion squished --label md [--density all]
  python spacing.py strip --control 36 [--density comfortable]   # a seated strip's height
  python spacing.py tokens --out DIR                      # DTCG, one file per density
  python spacing.py css                                   # expressions
  python spacing.py check                                 # reproduce the documented fixtures

One sequence of values; density picks where the rung names land on it. A
control's height is never authored: it is inset × 2 + the label's cap height
rounded to the grid, and the vertical padding is what makes that true once the
label's half-leading is subtracted. Type constants match typography-scale.

Requires: Python 3.9+, nothing else.
"""
import argparse, json, math, sys
from pathlib import Path

# ---- the ladder ----------------------------------------------------------------
SEQUENCE = [1, 2, 4, 6, 8, 12, 16, 20, 24, 28, 32, 36]           # px; 36 is extrapolated
RUNGS = ["4xs", "3xs", "2xs", "xs", "sm", "md", "lg", "xl", "2xl", "3xl"]
DENSITY_OFFSET = {"compact": 0, "comfortable": 1, "relaxed": 2}   # where "4xs" lands on SEQUENCE
RELATIONSHIPS = [("page → sections", "xl"), ("container → children", "md"),
                 ("cluster → siblings", "sm"), ("selectable → its label", None),
                 ("strip → seated control", "xs")]
INSET_SIZES = ["xs", "sm", "md", "lg", "xl"]
PROPORTIONS = {"squished": -1, "squared": 0, "stretched": +1}      # vertical rung relative to horizontal

# ---- type, as typography-scale defines it ------------------------------------------
STEPS = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl"]
BASE_REM = {"compact": 0.875, "comfortable": 1.0, "relaxed": 1.15625}
COMPRESSED = (1.13, 0.13)
CAP_RATIO = 0.727539                                                # Inter, sCapHeight / unitsPerEm
GAP_RATIO, GAP_SNAP = 0.618, 2
NS, NS_FIGMA = "com.equinor.spacing", "com.equinor.figma"


def css_round(v, step):
    return math.floor(v / step + 0.5) * step


def rung(name, density):
    return SEQUENCE[RUNGS.index(name) + DENSITY_OFFSET[density]]


def shifted(name, by):
    return RUNGS[RUNGS.index(name) + by]


def font_px(step, density):
    i = STEPS.index(step) - 3
    return round(css_round(BASE_REM[density] * 2 ** (i / 5), 0.03125) * 16, 6)


def line_height_compressed(step, density):
    n, N = STEPS.index(step), len(STEPS)
    mx, drop = COMPRESSED
    return css_round(font_px(step, density) * (mx - (n / (N - 1)) ** 3 * drop), 4)


def cap_rounded(step, density, cap_ratio=CAP_RATIO):
    return css_round(font_px(step, density) * cap_ratio, 4)


def control(size, proportion, label, density, cap_ratio=CAP_RATIO):
    """Optical padding and emergent height of a control with a single-line label."""
    h_rung = size
    v_rung = shifted(size, PROPORTIONS[proportion])
    inset_h, inset_v = rung(h_rung, density), rung(v_rung, density)
    lh = line_height_compressed(label, density)
    cap = cap_rounded(label, density, cap_ratio)
    half = (lh - cap) / 2
    return {"density": density, "size": size, "proportion": proportion, "label": label,
            "labelPx": font_px(label, density), "lineHeight": lh, "capRounded": cap,
            "insetHorizontal": inset_h, "insetVertical": inset_v, "halfLeading": half,
            "paddingBlock": inset_v - half, "paddingInline": inset_h,
            "height": 2 * inset_v + cap, "iconGap": css_round(font_px(label, density) * GAP_RATIO, GAP_SNAP)}


def strip(control_height, density):
    """A chrome strip seats controls with the raw xs rung above and below."""
    seat = rung("xs", density)
    return {"density": density, "seat": seat, "control": control_height, "height": control_height + 2 * seat}


# ---- outputs ---------------------------------------------------------------------
def table(density):
    lines = [f"{density}: the ladder", "  " + "  ".join(f"{r}={rung(r, density)}" for r in RUNGS), "", "  relationships"]
    for rel, r in RELATIONSHIPS:
        if r is None:
            lines.append(f"    {rel:<24} inset  per component, optically corrected (see `control`)")
        else:
            lines.append(f"    {rel:<24} {r:>3}  {rung(r, density)}px" + ("  (raw: no optical compensation)" if r == "xs" else ""))
    lines += ["", "  inset proportions (horizontal / vertical)"]
    for s in INSET_SIZES:
        lines.append("    " + f"{s:<3}" + "  ".join(f"{p}: {rung(s, density)}/{rung(shifted(s, k), density)}" for p, k in PROPORTIONS.items()))
    return "\n".join(lines) + "\n"


def dim(v):
    return {"value": int(v) if float(v).is_integer() else v, "unit": "px"}


def tokens(density):
    ladder = {r: {"$type": "dimension", "$value": dim(rung(r, density)), "$extensions": {
        NS: {"derived": {"expression": "SEQUENCE[index(rung) + offset(density)]",
                         "inputs": {"sequence": SEQUENCE, "rung": r, "offset": DENSITY_OFFSET[density]}},
             "density": density, **({"extrapolated": True} if rung(r, density) == 36 else {})},
        NS_FIGMA: {"collection": "Spacing", "mode": density, "scopes": ["GAP", "WIDTH_HEIGHT"]}}} for r in RUNGS}
    inset = {}
    for s in INSET_SIZES:
        inset[s] = {"horizontal": {"$type": "dimension", "$value": f"{{spacing.ladder.{s}}}"}}
        for p, k in PROPORTIONS.items():
            inset[s][f"vertical-{p}"] = {"$type": "dimension", "$value": f"{{spacing.ladder.{shifted(s, k)}}}"}
    optical = {}
    for s in INSET_SIZES:
        for p in PROPORTIONS:
            c = control(s, p, s if s in STEPS else "md", density)
            optical[f"{s}-{p}"] = {"$type": "dimension", "$value": dim(c["paddingBlock"]), "$extensions": {
                NS: {"derived": {"expression": "inset - (lineHeight - round(fontSize * capRatio, 4px)) / 2",
                                 "inputs": {"inset": f"{{spacing.inset.{s}.vertical-{p}}}", "label": c["label"],
                                            "lineHeight": c["lineHeight"], "fontSize": c["labelPx"], "capRatio": CAP_RATIO}},
                     "height": c["height"], "density": density,
                     "note": "deliberately off the 4px grid; never round it — the height is what lands"},
                NS_FIGMA: {"collection": "Spacing", "mode": density, "scopes": ["GAP"]}}}
    return {"spacing": {"ladder": ladder, "inset": inset, "optical-padding": optical}}


def css():
    out = ["/* One sequence; density moves the rung names along it. */"]
    for d in DENSITY_OFFSET:
        sel = ":root" if d == "comfortable" else f"[data-density='{d}']"
        out.append(sel + " {")
        for r in RUNGS:
            out.append(f"  --spacing-{r}: {rung(r, d)}px;" + ("  /* extrapolated */" if rung(r, d) == 36 else ""))
        out.append("}")
    out.append("/* Inset proportions: the vertical rung is one below, the same, or one above the horizontal. */")
    out.append(":root {")
    for s in INSET_SIZES:
        out.append(f"  --inset-{s}-horizontal: var(--spacing-{s});")
        for p, k in PROPORTIONS.items():
            out.append(f"  --inset-{s}-vertical-{p}: var(--spacing-{shifted(s, k)});")
    out.append("  /* optical padding: the label's half-leading comes off; height = inset × 2 + cap */")
    out.append(f"  --cap-rounded-md: round(calc(var(--font-size-md) * {CAP_RATIO}), 4px);")
    out.append("  --half-leading-md: calc((var(--line-height-md-compressed) - var(--cap-rounded-md)) / 2);")
    for p in PROPORTIONS:
        out.append(f"  --optical-padding-md-{p}: calc(var(--inset-md-vertical-{p}) - var(--half-leading-md));")
    out.append(f"  --icon-gap-md: round(calc(var(--font-size-md) * {GAP_RATIO}), {GAP_SNAP}px);")
    out.append("}")
    return "\n".join(out) + "\n"


# ---- fixtures ----------------------------------------------------------------------
FIXTURE = {
    "ladder": {"compact": [1, 2, 4, 6, 8, 12, 16, 20, 24, 28], "comfortable": [2, 4, 6, 8, 12, 16, 20, 24, 28, 32],
               "relaxed": [4, 6, 8, 12, 16, 20, 24, 28, 32, 36]},
    # the md squished button with an md label: DECISIONS.md, contracts, the internal skill
    "button": {"compact": (6, 24), "comfortable": (10, 36), "relaxed": (12, 44)},      # (paddingBlock, height)
    "chip_sm_squished": {"comfortable": (6, 24)},
    "tooltip_xs_squared_sm": {"compact": 20, "comfortable": 24, "relaxed": 36},
    "strip": {"compact": 36, "comfortable": 52, "relaxed": 68},
    "icon_gap_md": {"compact": 8, "comfortable": 8, "relaxed": 10},
}


def check():
    fails = []
    def eq(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got}, documented {want}")
    for d, want in FIXTURE["ladder"].items():
        eq(f"ladder {d}", [rung(r, d) for r in RUNGS], want)
    for d, (pad, h) in FIXTURE["button"].items():
        c = control("md", "squished", "md", d); eq(f"button {d}", (c["paddingBlock"], c["height"]), (pad, h))
    for d, (pad, h) in FIXTURE["chip_sm_squished"].items():
        c = control("sm", "squished", "sm", d); eq(f"chip {d}", (c["paddingBlock"], c["height"]), (pad, h))
    for d, h in FIXTURE["tooltip_xs_squared_sm"].items():
        eq(f"tooltip {d}", control("xs", "squared", "sm", d)["height"], h)
    for d, h in FIXTURE["strip"].items():
        eq(f"strip {d}", strip(control("md", "squished", "md", d)["height"], d)["height"], h)
    for d, g in FIXTURE["icon_gap_md"].items():
        eq(f"icon gap {d}", control("md", "squished", "md", d)["iconGap"], g)
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if not fails:
        print("ok: ladder at three densities, button 24/36/44, chip 24, tooltip 20/24/36, strips 36/52/68, icon gap")
    return 1 if fails else 0


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("table"); t.add_argument("--density", default="comfortable", choices=[*DENSITY_OFFSET, "all"])
    c = sub.add_parser("control")
    c.add_argument("--size", default="md", choices=INSET_SIZES); c.add_argument("--proportion", default="squished", choices=list(PROPORTIONS))
    c.add_argument("--label", default="md", choices=STEPS); c.add_argument("--density", default="all", choices=[*DENSITY_OFFSET, "all"])
    c.add_argument("--cap-ratio", type=float, default=CAP_RATIO, help="label face's capHeight / unitsPerEm (Inter 0.727539)")
    s = sub.add_parser("strip"); s.add_argument("--control", type=float, required=True, help="height of the tallest seated control")
    s.add_argument("--density", default="comfortable", choices=[*DENSITY_OFFSET, "all"])
    k = sub.add_parser("tokens"); k.add_argument("--out", required=True)
    sub.add_parser("css"); sub.add_parser("check")
    a = p.parse_args(argv)
    dens = list(DENSITY_OFFSET) if getattr(a, "density", None) in (None, "all") else [a.density]
    if a.cmd == "table":
        for d in dens: sys.stdout.write(table(d) + "\n")
    elif a.cmd == "control":
        print(json.dumps([control(a.size, a.proportion, a.label, d, a.cap_ratio) for d in dens], indent=2))
    elif a.cmd == "strip":
        print(json.dumps([strip(a.control, d) for d in dens], indent=2))
    elif a.cmd == "tokens":
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        for d in DENSITY_OFFSET:
            (out / f"spacing.{d}.tokens.json").write_text(json.dumps(tokens(d), indent=2) + "\n"); print(out / f"spacing.{d}.tokens.json", file=sys.stderr)
    elif a.cmd == "css":
        sys.stdout.write(css())
    elif a.cmd == "check":
        return check()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
