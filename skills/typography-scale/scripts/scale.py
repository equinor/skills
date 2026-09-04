#!/usr/bin/env python3
"""Derive a typographic scale from its constants and emit it — tokens first.

Usage:
  python scale.py                          # EDS preset, all densities, DTCG tokens
  python scale.py --format table           # the ramp, for reading
  python scale.py --format css             # CSS with the expressions intact
  python scale.py --format css --css baked # CSS with literals, expression in comments
  python scale.py --format figma --out DIR # Plugin API scripts for use_figma
  python scale.py --correction 1.137288 --display Equinor   # two-ramp branch
  python scale.py --check                  # reproduce the documented fixtures

Everything derives from four constants — base, steps per octave, step offset,
snap — plus two line-height curves and a grid. Densities are values of `base`.
The numbers this prints are the numbers the skill documents; `--check` fails if
they stop agreeing.

Requires: Python 3.9+, nothing else.
"""
import argparse, json, math, sys
from pathlib import Path

# ---- the EDS preset (references/eds-preset.md) ------------------------------
STEPS = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl"]
BASE_STEP = "lg"                     # the step that *is* the base
STEPS_PER_OCTAVE = 5                 # ratio 2^(1/5)
SIZE_SNAP_REM = 0.03125              # half a pixel at a 16px root
LINE_HEIGHT_SNAP_PX = 4
CURVES = {"default": (1.39, 0.29), "compressed": (1.13, 0.13)}   # (max, drop)
DENSITIES = {"compact": 0.875, "comfortable": 1.0, "relaxed": 1.15625}  # base, rem
ROOT_PX = 16
NS = "com.equinor.typography"
NS_FIGMA = "com.equinor.figma"


def css_round(value, step):
    """CSS round(nearest): halfway cases go up. Python's round() is half-to-even
    and disagrees with the browser on exact .25 / .5 boundaries."""
    return math.floor(value / step + 0.5) * step


def clean(n):
    return round(n, 6)


def step_index(step):
    return STEPS.index(step) - STEPS.index(BASE_STEP)


def font_size_rem(base_rem, step):
    return clean(css_round(base_rem * 2 ** (step_index(step) / STEPS_PER_OCTAVE), SIZE_SNAP_REM))


def multiplier(step, curve):
    mx, drop = CURVES[curve]
    n, N = STEPS.index(step), len(STEPS)
    return mx - (n / (N - 1)) ** 3 * drop


def line_height_px(font_px, step, curve):
    return clean(css_round(font_px * multiplier(step, curve), LINE_HEIGHT_SNAP_PX))


def ramp(density, correction=None):
    base = DENSITIES[density]
    rows = []
    for s in STEPS:
        rem = font_size_rem(base, s)
        px = clean(rem * ROOT_PX)
        row = {"step": s, "index": step_index(s), "rem": rem, "px": px,
               "lh": {c: line_height_px(px, s, c) for c in CURVES}}
        if correction:
            drem = clean(css_round(rem * correction, SIZE_SNAP_REM))
            row["display_rem"] = drem
            row["display_px"] = clean(drem * ROOT_PX)
        rows.append(row)
    return rows


def octave_exceptions():
    """Pairs five steps apart whose snapped sizes are not exactly 2x."""
    out = []
    for d in DENSITIES:
        r = ramp(d)
        for i in range(len(STEPS) - STEPS_PER_OCTAVE):
            lo, hi = r[i], r[i + STEPS_PER_OCTAVE]
            if abs(hi["px"] - 2 * lo["px"]) > 1e-9:
                out.append((d, lo["step"], lo["px"], hi["step"], hi["px"]))
    return out


# ---- outputs -----------------------------------------------------------------
def dim(value, unit):
    return {"value": value, "unit": unit}


def tokens(density, correction=None, display=None):
    base = DENSITIES[density]
    size_expr = f"round(base * pow(2, step / {STEPS_PER_OCTAVE}), {SIZE_SNAP_REM}rem)"
    lh_expr = "round(fontSize * (max - pow(n / (N - 1), 3) * drop), 4px)"
    fs, lh, disp = {}, {}, {}
    for row in ramp(density, correction):
        s = row["step"]
        fs[s] = {"$type": "dimension", "$value": dim(row["rem"], "rem"), "$extensions": {
            NS: {"derived": {"expression": size_expr,
                             "inputs": {"base": dim(base, "rem"), "step": row["index"]}},
                 "step": s, "density": density},
            NS_FIGMA: {"collection": "Typography", "mode": density, "scopes": ["FONT_SIZE"]}}}
        lh[s] = {}
        for c, (mx, drop) in CURVES.items():
            lh[s][c] = {"$type": "dimension", "$value": dim(row["lh"][c], "px"), "$extensions": {
                NS: {"derived": {"expression": lh_expr,
                                 "inputs": {"fontSize": f"{{typography.font-size.{s}}}", "n": STEPS.index(s),
                                            "N": len(STEPS), "max": mx, "drop": drop}},
                     "step": s, "curve": c, "density": density},
                NS_FIGMA: {"collection": "Typography", "mode": density, "scopes": ["LINE_HEIGHT"]}}}
        if correction:
            disp[s] = {"$type": "dimension", "$value": dim(row["display_rem"], "rem"), "$extensions": {
                NS: {"derived": {"expression": f"round(fontSize * correction, {SIZE_SNAP_REM}rem)",
                                 "inputs": {"fontSize": f"{{typography.font-size.{s}}}",
                                            "correction": correction}},
                     "step": s, "family": display or "display", "density": density,
                     "lineHeight": f"{{typography.line-height.{s}}}"},
                NS_FIGMA: {"collection": "Typography", "mode": density, "scopes": ["FONT_SIZE"]}}}
    out = {"typography": {"font-size": fs, "line-height": lh}}
    if correction:
        out["typography"]["font-size-display"] = disp
    return out


def css(density_list, baked, correction=None, display=None):
    lines = [":root {"]
    for d in density_list:
        sel = ":root" if d == "comfortable" else f"[data-density='{d}']"
        lines.append(f"  /* {d}: base {DENSITIES[d]}rem */")
    lines.append(f"  --_base: {DENSITIES['comfortable']}rem;")
    lines.append("}")
    for d in density_list:
        if d != "comfortable":
            lines.append(f"[data-density='{d}'] {{ --_base: {DENSITIES[d]}rem; }}")
    lines.append(":root {")
    for row in ramp("comfortable", correction):
        s, i = row["step"], row["index"]
        expr = f"round(calc(var(--_base) * pow(2, {i}/{STEPS_PER_OCTAVE})), {SIZE_SNAP_REM}rem)"
        if baked:
            lines.append(f"  --font-size-{s}: {row['rem']}rem; /* {expr} */")
        else:
            lines.append(f"  --font-size-{s}: {expr}; /* {row['px']}px at comfortable */")
        for c, (mx, drop) in CURVES.items():
            n = STEPS.index(s)
            lexpr = f"round(calc(var(--font-size-{s}) * ({mx} - pow({n}/{len(STEPS)-1}, 3) * {drop})), 4px)"
            if baked:
                lines.append(f"  --line-height-{s}-{c}: {row['lh'][c]}px; /* {lexpr} */")
            else:
                lines.append(f"  --line-height-{s}-{c}: {lexpr}; /* {row['lh'][c]}px at comfortable */")
        if correction:
            dexpr = f"round(calc(var(--font-size-{s}) * {correction}), {SIZE_SNAP_REM}rem)"
            lines.append(f"  --font-size-display-{s}: {row['display_rem'] if baked else dexpr}"
                         f"{'rem' if baked else ''}; /* {row['display_px']}px, {display or 'display'} */")
    lines.append("}")
    if baked:
        lines.insert(0, "/* Baked values: the browser never evaluates the expressions in the comments. */")
    return "\n".join(lines) + "\n"


def figma_scripts(correction=None, display=None, family="Inter", style="Regular"):
    """Two Plugin API scripts for `use_figma` (or a local plugin): variables, then styles."""
    modes = list(DENSITIES)
    values = {d: ramp(d, correction) for d in modes}
    var_rows = []
    for row in values["comfortable"]:
        s = row["step"]
        var_rows.append({"name": f"font-size/{s}", "scopes": ["FONT_SIZE"],
                         "values": {d: values[d][STEPS.index(s)]["px"] for d in modes},
                         "css": f"var(--font-size-{s})"})
        for c in CURVES:
            var_rows.append({"name": f"line-height/{s}/{c}", "scopes": ["LINE_HEIGHT"],
                             "values": {d: values[d][STEPS.index(s)]["lh"][c] for d in modes},
                             "css": f"var(--line-height-{s}-{c})"})
        if correction:
            var_rows.append({"name": f"font-size-display/{s}", "scopes": ["FONT_SIZE"],
                             "values": {d: values[d][STEPS.index(s)]["display_px"] for d in modes},
                             "css": f"var(--font-size-display-{s})"})
    variables_js = f"""// Generated by typography-scale/scripts/scale.py — variables. Idempotent: reuses by name.
const ROWS = {json.dumps(var_rows, indent=2)};
const MODES = {json.dumps(modes)};
const collections = await figma.variables.getLocalVariableCollectionsAsync();
let col = collections.find(c => c.name === 'Typography');
if (!col) {{ col = figma.variables.createVariableCollection('Typography'); col.renameMode(col.modes[0].modeId, MODES[0]); }}
const modeId = {{}};
for (const m of MODES) {{
  const found = col.modes.find(x => x.name === m);
  modeId[m] = found ? found.modeId : col.addMode(m);
}}
const existing = {{}};
for (const id of col.variableIds) {{ const v = await figma.variables.getVariableByIdAsync(id); if (v) existing[v.name] = v; }}
const created = [], updated = [];
for (const r of ROWS) {{
  let v = existing[r.name];
  if (!v) {{ v = figma.variables.createVariable(r.name, col, 'FLOAT'); created.push(v.id); }} else updated.push(v.id);
  v.scopes = r.scopes;
  for (const m of MODES) v.setValueForMode(modeId[m], r.values[m]);
  v.setVariableCodeSyntax('WEB', r.css);
}}
return {{ collectionId: col.id, modes: modeId, createdVariableIds: created, updatedVariableIds: updated }};
"""
    style_rows = []
    for s in STEPS:
        style_rows.append({"name": f"text/{s}", "size": f"font-size/{s}", "lh": f"line-height/{s}/default"})
        style_rows.append({"name": f"label/{s}", "size": f"font-size/{s}", "lh": f"line-height/{s}/compressed"})
        if correction:
            style_rows.append({"name": f"display/{s}", "size": f"font-size-display/{s}",
                               "lh": f"line-height/{s}/default", "family": display or "display"})
    styles_js = f"""// Generated by typography-scale/scripts/scale.py — text styles bound to the variables above.
const STYLES = {json.dumps(style_rows, indent=2)};
const FONT = {{ family: {json.dumps(family)}, style: {json.dumps(style)} }};
const fonts = await figma.listAvailableFontsAsync();
const families = new Set(fonts.map(f => f.fontName.family));
const need = new Set([FONT.family, ...STYLES.map(s => s.family).filter(Boolean)]);
for (const f of need) if (!families.has(f)) throw new Error(`Font not available in this file: ${{f}}`);
const byName = {{}};
for (const v of await figma.variables.getLocalVariablesAsync('FLOAT')) byName[v.name] = v;
const existing = {{}};
for (const st of await figma.getLocalTextStylesAsync()) existing[st.name] = st;
const created = [], updated = [];
for (const s of STYLES) {{
  const fontName = {{ family: s.family || FONT.family, style: FONT.style }};
  await figma.loadFontAsync(fontName);
  let st = existing[s.name];
  if (!st) {{ st = figma.createTextStyle(); st.name = s.name; created.push(st.id); }} else updated.push(st.id);
  st.fontName = fontName;
  const size = byName[s.size], lh = byName[s.lh];
  if (!size || !lh) throw new Error(`Variable missing for ${{s.name}}: run the variables script first`);
  st.setBoundVariable('fontSize', size);
  st.setBoundVariable('lineHeight', lh);
  st.description = `CSS: ${{size.codeSyntax.WEB}} / ${{lh.codeSyntax.WEB}}`;
}}
return {{ createdStyleIds: created, updatedStyleIds: updated }};
"""
    return {"figma-variables.js": variables_js, "figma-text-styles.js": styles_js}


def table(density_list, correction=None):
    out = []
    for d in density_list:
        out.append(f"{d} (base {DENSITIES[d]}rem)")
        hdr = f"{'step':>4} {'px':>6} {'default':>8} {'compressed':>10}" + (f" {'display':>8}" if correction else "")
        out.append(hdr)
        for r in ramp(d, correction):
            line = f"{r['step']:>4} {r['px']:>6g} {r['lh']['default']:>8g} {r['lh']['compressed']:>10g}"
            if correction:
                line += f" {r['display_px']:>8g}"
            out.append(line)
        out.append("")
    return "\n".join(out)


# ---- the documented fixtures -------------------------------------------------
FIXTURE = {
    "comfortable_px": [10.5, 12, 14, 16, 18.5, 21, 24.5, 28, 32, 37],
    "comfortable_default": [16, 16, 20, 24, 24, 28, 32, 36, 36, 40],
    "comfortable_compressed": [12, 12, 16, 20, 20, 24, 28, 28, 32, 36],
    "ratio_percent": [152, 133, 143, 150, 130, 133, 131, 129, 113, 108],
    "octave_exceptions": [("compact", "xs", 9.0, "2xl", 18.5), ("compact", "md", 12.0, "4xl", 24.5),
                          ("comfortable", "sm", 12.0, "3xl", 24.5), ("relaxed", "xs", 12.0, "2xl", 24.5),
                          ("relaxed", "xl", 21.5, "6xl", 42.5)],
    # positions.md §6: × 1.019345 at comfortable, display px
    "small_correction_display": {"xs": 10.5, "sm": 12, "md": 14.5, "lg": 16.5, "xl": 19, "3xl": 25, "6xl": 37.5},
}


def check():
    r = ramp("comfortable")
    fails = []
    def eq(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got}, documented {want}")
    eq("comfortable sizes", [x["px"] for x in r], FIXTURE["comfortable_px"])
    eq("comfortable line-height default", [x["lh"]["default"] for x in r], FIXTURE["comfortable_default"])
    eq("comfortable line-height compressed", [x["lh"]["compressed"] for x in r], FIXTURE["comfortable_compressed"])
    eq("ratio table", [math.floor(x["lh"]["default"] / x["px"] * 100 + 0.5) for x in r], FIXTURE["ratio_percent"])
    eq("octave exceptions", octave_exceptions(), FIXTURE["octave_exceptions"])
    small = {x["step"]: x["display_px"] for x in ramp("comfortable", 1.019345)}
    eq("small correction survives the snap", {k: small[k] for k in FIXTURE["small_correction_display"]},
       FIXTURE["small_correction_display"])
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    if not fails:
        print("ok: comfortable ramp, both line-height curves, ratio table, "
              f"{len(FIXTURE['octave_exceptions'])} octave exceptions, snap-limit table")
    return 1 if fails else 0


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog="Constants are the EDS preset (references/eds-preset.md).")
    p.add_argument("--density", choices=[*DENSITIES, "all"], default="all")
    p.add_argument("--format", choices=["tokens", "css", "figma", "table"], default="tokens")
    p.add_argument("--css", choices=["expressions", "baked"], default="expressions",
                   help="for --format css: ship the expressions (evergreen) or literals")
    p.add_argument("--correction", type=float, metavar="FACTOR",
                   help="x-height correction for a second family → baked display ramp")
    p.add_argument("--display", metavar="FAMILY", help="name of the corrected family")
    p.add_argument("--family", default="Inter", help="text family for Figma text styles")
    p.add_argument("--style", default="Regular", help="font style name for Figma text styles")
    p.add_argument("--out", metavar="DIR", help="write files here instead of stdout")
    p.add_argument("--check", action="store_true", help="reproduce the documented fixtures and exit")
    a = p.parse_args(argv)
    if a.check:
        return check()
    densities = list(DENSITIES) if a.density == "all" else [a.density]
    files = {}
    if a.format == "tokens":
        for d in densities:
            files[f"scale.{d}.tokens.json"] = json.dumps(tokens(d, a.correction, a.display), indent=2) + "\n"
    elif a.format == "css":
        files["scale.css"] = css(densities, a.css == "baked", a.correction, a.display)
    elif a.format == "figma":
        files.update(figma_scripts(a.correction, a.display, a.family, a.style))
    else:
        files["scale.txt"] = table(densities, a.correction)
    if a.out:
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        for name, body in files.items():
            (out / name).write_text(body)
            print(f"wrote {out / name}", file=sys.stderr)
    else:
        for name, body in files.items():
            if len(files) > 1:
                print(f"// ---- {name}" if name.endswith(".js") else f"/* ---- {name} */" if name.endswith(".css") else f"# ---- {name}", file=sys.stderr)
            sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
