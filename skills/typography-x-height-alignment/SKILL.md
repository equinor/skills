---
name: typography-x-height-alignment
description: 'Aligns paired font families by measured x-height so they look the same size at the same step. USE FOR: two fonts that look mismatched at one nominal size, extracting metrics from font files, deriving the correction factor, choosing between size-adjust and baked font-size tokens, emitting the correction as a design token. DO NOT USE FOR: building the size ramp itself (use typography-scale), choosing which typefaces to pair, font licensing or hosting.'
---

# x-height alignment

Two faces set at the same nominal size rarely look the same size. Apparent size
is **x-height**, not em: the em square is an arbitrary container, and where a
designer put the lowercase letters inside it varies by hundreds of units between
families. Set Inter and Equinor both at 16px and Equinor reads smaller — not
because it *is* smaller, but because 48% of its em is lowercase against Inter's
55%.

This skill turns that into one measured number, recorded where a build can check
it.

## What you need before starting

1. **The font files themselves** — `.ttf`, `.otf`, `.woff2`, or a URL to
   fetch. Metrics come out of the binary; nothing else is trustworthy.
2. **Which family is the reference** (the "master"). Normally the text face,
   because body copy is what everything else is judged against. Everything else
   is corrected *towards* it.

**Never supply metrics from memory or from a specification page.** Font vendors
revise metrics between releases — that is the exact failure documented in
section 5. If a font is named but you cannot obtain the file, **stop and ask for
it** — do not demonstrate on the bundled pair and present the result as if it
described the named fonts.

### The bundled demo pair

`assets/fonts/` ships Inter and EB Garamond, both SIL OFL, so the procedure runs
with nothing supplied. Run the script with no arguments to check your
environment works and to see the output shape:

```
Inter        upm 2048   xHeight 1118   xRatio 0.545898   (reference)
EB Garamond  upm 1000   xHeight  400   xRatio 0.400000   correction 1.364746
```

This pair is chosen to teach, not to flatter. A 36% correction is impossible to
mistake for rounding, and because the two fonts have different `unitsPerEm`, the
raw x-heights (1118 against 400) suggest Inter's is nearly *three* times larger
when it is 1.36×. Normalise or be wrong by a factor of two.

It is also a fair test of the alternative: ask a language model how to pair
these two and you get "EB Garamond has a low x-height, so boost your headings —
32px or more." Correct diagnosis, guessed number. The measured answer is
`0.545898 / 0.400 = 1.364746`, which at a 32px step sets EB Garamond at 43.5px.

Bundling these binaries does not contradict the rule below about not vendoring
fonts. That rule is about **licence-restricted** faces — Equinor's cannot be
redistributed. OFL fonts can, provided the licence travels with them; see
[`assets/fonts/README.md`](assets/fonts/README.md) for authorship, provenance
and the terms, which are **not** this repository's MIT licence.

## 1. Extract the metrics

`fontTools` reads every common format; `brotli` is what lets it open `.woff2`.

```bash
python3 -m venv .venv && .venv/bin/pip install fonttools brotli
```

```python
# xheight.py — usage: python xheight.py REFERENCE.otf SECONDARY.woff2 ...
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
    for base in (Path(__file__).resolve().parent, Path.cwd()):
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
```

Three things to check in the output before going further:

- **`unitsPerEm` differs between families** — 1000 and 2048 are both common.
  That is why everything is normalised to a ratio before comparing. Never
  compare raw `sxHeight` values.
- **`xRatio` is plausible** — roughly 0.45–0.55 for most text faces. A value
  outside that range usually means an icon or display font, or a bad `OS/2`
  table.
- **Whether the fallback fired.** Measured glyph bounds include *overshoot* on
  rounded letters, so a measured `x` can run a few units above the true
  x-height (Amatic SC: `OS/2` says 659, the glyph measures 662). Prefer `OS/2`
  when it is valid; note it in the output when you had to measure.

**Do not vendor the font binaries to get reproducibility.** Many licences
forbid redistribution. Commit the extracted metrics plus the source URL and
extraction date — measurements are not the font, and they are what the build
actually needs.

## 2. Derive the correction

```
correction = referenceXRatio / selfXRatio
```

```
Inter (ref)  upm 2048  xHeight 1118  →  0.545898
Equinor      upm 1000  xHeight  480  →  0.480000  →  1.137288  (113.73%)
CommitMono   upm 1000  xHeight  540  →  0.540000  →  1.010922  (101.09%)
```

The secondary face is then set at `nominalSize × correction`. At a 14px step
Equinor is set at 15.92px, and the two read as the same size.

The reference family's own correction is `1.0` by definition. Emit it anyway —
a consumer that special-cases "the one without a factor" will break the first
time the reference changes.

## 3. Emit it as a token, with the derivation attached

The correction is the output of this skill. Emit DTCG, and put the rule *and
its inputs* in `$extensions` so a build can recompute and assert rather than
trust a committed number:

```json
{
  "typography": {
    "font-family": {
      "text": { "$type": "fontFamily", "$value": ["Inter", "sans-serif"] },
      "display": { "$type": "fontFamily", "$value": ["Equinor", "sans-serif"] }
    },
    "x-height-correction": {
      "text": {
        "$type": "number",
        "$value": 1,
        "$description": "Reference family — corrected against itself."
      },
      "display": {
        "$type": "number",
        "$value": 1.137288,
        "$description": "Scale Equinor by this to match Inter's x-height.",
        "$extensions": {
          "com.equinor.typography": {
            "derived": {
              "expression": "referenceXRatio / selfXRatio",
              "inputs": {
                "reference": "{typography.font-family.text}",
                "referenceXRatio": 0.545898,
                "selfXRatio": 0.48
              }
            },
            "metrics": {
              "unitsPerEm": 1000,
              "xHeight": 480,
              "capHeight": 700,
              "extent": 1.0,
              "source": "https://cdn.example.com/font/EquinorVariable-VF.woff2",
              "extractedAt": "2026-08-29",
              "method": "OS/2.sxHeight"
            }
          }
        }
      }
    }
  }
}
```

**Namespace:** DTCG requires `$extensions` keys to be reverse-DNS. Use the
project's existing namespace if it has one — grep for `"$extensions"` in the
token files — otherwise ask for the organisation's domain rather than inventing
one. `com.equinor.typography` above is the reference implementation's.

**Record `method`.** `OS/2.sxHeight` and `measured:x-glyph-bounds` are not the
same quality of evidence, and the difference matters when someone re-derives
the number against a newer release of the font.

## 4. Delivering the correction

Emitting the factor is not the same as applying it, and the right mechanism
depends on where the type will render. **Ask before emitting anything beyond
the token file:**

> Will this be used in a CSS-only environment, or also in Figma / React Native /
> other non-CSS targets?

**CSS only** → **one** size ramp for both families, with `size-adjust` in the
`@font-face` doing the correction. It corrects continuously, so it fixes the
face at *any* size, including off-scale ones. This is the simpler output: no
second scale, no per-family font-size tokens.

The percentage must be **written by the generator**, not by a person:

```js
// emit-font-faces.js — reads the token file, writes the stylesheet
const t = JSON.parse(readFileSync('tokens/typography.tokens.json', 'utf8'))
const corrections = t.typography['x-height-correction']

for (const [family, token] of Object.entries(corrections)) {
  const ext = token.$extensions?.['com.equinor.typography']
  const pct = +(token.$value * 100).toFixed(4)
  out.push(`@font-face {
  font-family: '${ext.metrics.family}';
  src: url('${ext.metrics.source}') format('woff2-variations');${
    token.$value === 1 ? '' : `
  /* generated from ${ext.metrics.method}, extracted ${ext.metrics.extractedAt} */
  size-adjust: ${pct}%;`}
}`)
}
```

```css
/* Generated — do not edit. Source: tokens/typography.tokens.json */
@font-face {
  font-family: 'Equinor';
  src: url('https://cdn.example.com/font/EquinorVariable-VF.woff2') format('woff2-variations');
  /* generated from OS/2.sxHeight, extracted 2026-08-29 */
  size-adjust: 113.7288%;
}
```

The distinction is not cosmetic. A hand-typed `113.7288%` is correct the day it
is typed and silently wrong after the next font release; a generated one is
re-derived from the metrics on every build. Two things make that real:

- **The stylesheet is a build artefact** — generated header, not hand-edited,
  and ideally not committed.
- **A test asserts the emitted percentage still equals**
  `round(refXRatio / selfXRatio × 100, 4)` **recomputed from the font files**,
  so a font update either moves the value or fails the build. Without that test
  the generator is just a slower way to produce the same stale literal.

**Also Figma, React Native, or anything else** → do **not** use `size-adjust`.
It is a CSS `@font-face` descriptor: React Native loads fonts natively and never
parses it, and Figma has no equivalent, so both silently render the uncorrected
face while CSS looks right. Bake the corrected sizes into per-family font-size
tokens instead — that is the `typography-scale` skill's two-scale output, and
this token file is its input.

**Never both.** `size-adjust` *and* baked sizes double-corrects.

## 5. Why this must be derived, not transcribed

EDS shipped `size-adjust: 105.9%` for its display face, labelled
`/* Match Inter x-height */`. The metrics require 113.73%.

The value was almost certainly right when written — 105.9% implies an x-height
around 0.5155, against today's 0.480 — and was never recalculated when the font
was updated. So the face rendered at roughly 93% of Inter's x-height, visibly
mismatched, under a comment asserting the opposite. The mono face had the same
defect: 95.2% shipped where 101.09% is required.

Nothing there is an arithmetic mistake. A number derived from font metrics was
stored as a literal, far from the metrics, with no test relating the two — so a
font update invalidates it *silently*. There is no build step that can fail.

So: extract in the build, from the fonts actually being served; derive the
factor; and assert the relationship in a test, so a font update either moves the
value or breaks the build. Where you find a discrepancy you cannot resolve,
record it — hypothesis, impact, status — rather than quietly correcting it. The
105.9% finding is only legible because someone wrote down what it implied about
the older font.

## 6. Check the result

- **Render both families at the same corrected step and compare lowercase.**
  The arithmetic can be right and the pairing still wrong — correction aligns
  x-heights, not stroke weight, width or colour.
- **Do not correct the line-height.** The point of alignment is that both faces
  look the same size at the same step, so they should share the line box. See
  `typography-scale`.
- **Check vertical extent before believing an overflow report.**
  `(typoAscender − typoDescender) / unitsPerEm` — a face can carry a larger
  nominal size and still occupy less vertical space (Equinor 1.000em against
  Inter's 1.210em), so the corrected face is usually not the one overflowing.

## Related

- **`typography-scale`** — applies the correction across a size ramp, and emits
  the two-scale output for non-CSS targets.

## Provenance

The metric conventions, the `$extensions` shape and the 105.9% finding come
from the EDS token rework in **`equinor/ids-meetup-oslo-26`**
(Equinor-internal), prepared for the Into Design Systems Oslo meetup,
9 September 2026:

| Path | What it establishes |
| --- | --- |
| `eds-tokens-reworked/src/font-metrics.json` | Committed metrics with source URLs, and the recorded discrepancy |
| `eds-tokens-reworked/src/formulas.ts` | `xHeightCorrection()` |
| `eds-tokens-reworked/src/build/tokens.ts` | The `derived: { expression, inputs }` extension shape |
| `eds-tokens-reworked/DECISIONS.md` | Decision 5 — bake the correction; font size only |
