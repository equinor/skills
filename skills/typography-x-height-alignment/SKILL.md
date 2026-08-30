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
   is corrected *towards* it. "Align X with Y" means Y is the reference — if the
   request is ambiguous, say which way you read it rather than guessing silently.
3. **Which instance**, if the fonts are variable — normally the weight the
   pairing is actually set at. See below; this changes the answer.

**Never supply metrics from memory or from a specification page.** Font vendors
revise metrics between releases — that is the exact failure documented in
section 5. If a font is named but you cannot obtain the file, **stop and ask for
it** — do not demonstrate on the bundled pair and present the result as if it
described the named fonts.

### The bundled demo pair

`assets/fonts/` ships Inter and EB Garamond, both SIL OFL, so the procedure runs
with nothing supplied — the fastest check that your environment works:

```
Inter        xRatio 0.545898  @ wght 400   (reference)
EB Garamond  xRatio 0.400000  @ wght 400   correction 1.364746
```

The pair is chosen to teach: a 36% correction cannot be mistaken for rounding,
the two `unitsPerEm` differ so raw x-heights mislead by a factor of two, and
EB Garamond's x-height moves along the weight axis while Inter's does not — so
`1.364746` is the **wght 400** answer, not *the* answer.

What it demonstrates, and why bundling OFL fonts does not contradict the
no-vendoring rule below: [`references/demo-pair.md`](references/demo-pair.md).

## 1. Extract the metrics

`fontTools` reads every common format; `brotli` is what lets it open `.woff2`.

```bash
python3 -m venv .venv && .venv/bin/pip install fonttools brotli
.venv/bin/python scripts/xheight.py REFERENCE.otf SECONDARY.woff2
```

`scripts/xheight.py` reads `OS/2` and `head` from each file and prints the
metrics, ratios and derived correction as JSON. Run it with **no arguments** to
measure the bundled demo pair — the fastest check that your environment works.

It is a file rather than a snippet on purpose: the numbers it produces are
load-bearing, and a script that is retyped from a code block can drift from the
one that was verified.

### Variable fonts: pin the instance

Most fonts shipped today are variable, and a variable file is measured at one
point on its axes. Two traps follow:

- **The default instance is often not Regular.** Montserrat's variable file
  defaults to `wght 100`, and `nameID1` gives it away — `"Montserrat Thin"`.
  Measured straight, it yields a correction that is plausible, in range, and
  wrong for any normal pairing.
- **x-height moves along the axis** whenever the font has an `MVAR` table, so a
  single scalar per family only holds at one location. For Montserrat against
  Open Sans the correction crosses 1.0 near `wght 600` — pair at Bold and the
  "smaller" face needs setting *smaller still*, inverting the correction.

```bash
.venv/bin/python scripts/xheight.py --location wght=400 REFERENCE.ttf SECONDARY.ttf
```

The script warns on both traps and always reports the `instance` it measured.
Pin the weight the pairing is actually set at; if a font's axis does not reach
it, the value is clamped and a warning says so.

Four things to check in the output before going further:

- **`unitsPerEm` differs between families** — 1000 and 2048 are both common.
  That is why everything is normalised to a ratio before comparing. Never
  compare raw `sxHeight` values.
- **`xRatio` is plausible** — roughly 0.45–0.55 for most text faces. A value
  outside that range usually means an icon or display font, or a bad `OS/2`
  table.
- **Which `method` fired.** `OS/2.sxHeight` and `measured:x-glyph-bounds` are
  not the same quality of evidence — measured glyph bounds include *overshoot*
  on rounded letters, so a measured `x` can run a few units above the true
  x-height (Amatic SC: `OS/2` says 659, the glyph measures 662). The script
  records which one it used; carry that into the token.
- **The `instance`, and any warnings.** A correction with no instance recorded
  is only meaningful for a static font.

**Do not vendor the font binaries to get reproducibility.** Many licences forbid
redistribution. Commit the extracted metrics, the source and the extraction date
— measurements are not the font, and they are what the build needs. For a local
file with no URL, record the path and the `sha256` the script emits: a checksum
pins the exact bytes measured, which is what the URL stood in for.

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
"x-height-correction": {
  "display": {
    "$type": "number",
    "$value": 1.137288,
    "$extensions": {
      "com.equinor.typography": {
        "derived": {
          "expression": "referenceXRatio / selfXRatio",
          "inputs": { "referenceXRatio": 0.545898, "selfXRatio": 0.48 }
        },
        "metrics": { "unitsPerEm": 1000, "xHeight": 480, "source": "…",
                     "extractedAt": "2026-08-29", "method": "OS/2.sxHeight" }
      }
    }
  }
}
```

The committed `$value` is then *checkable*: a build reads `derived.expression`
and its `inputs`, recomputes, and fails if they disagree.

Full example, the reverse-DNS namespace rule, and why `method` is recorded:
[`references/token-shape.md`](references/token-shape.md).

## 4. Delivering the correction

Emitting the factor is not the same as applying it, and the right mechanism
depends on where the type will render. **Ask before emitting anything beyond
the token file:**

> Will this be used in a CSS-only environment, or also in Figma / React Native /
> other non-CSS targets? And which weight is the pairing set at?

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

**This is not a rule that the least capable platform decides everything.** Bake
the correction because it is a *value* the platforms would otherwise disagree
about — not because Figma and React Native set the ceiling. Capabilities one
platform has and another lacks, such as text-box trimming, are a different case
and should not be levelled down:
[`references/positions.md`](references/positions.md).

## 5. Why this must be derived, not transcribed

A correction is a *quotient of two measurements*. Written into a stylesheet as a
literal it stops being that, and becomes a number that happens to be right today.

The bundled pair shows how fast that expires: EB Garamond against Inter needs
`1.364746` at `wght 400` and `1.302860` at `wght 700`, because EB Garamond's
x-height moves along the weight axis and Inter's does not. Nothing about the
literal says which weight it belongs to, so a stylesheet carrying it is silently
wrong for every heading not set at Regular.

Font revisions do the same thing more slowly. A foundry adjusts an x-height
between releases; the transcribed percentage does not move, because nothing
relates it to the metrics any more. The typical symptom is a `size-adjust`
value with a comment asserting the faces match, in a stylesheet where they
visibly do not — the comment is the last trace of a derivation nobody can rerun.

There is no arithmetic mistake in any of this. The defect is structural: a
derived value stored far from its inputs, with no test relating the two, so an
upstream change invalidates it *silently*. No build step can fail.

So:

- **Extract in the build**, from the fonts actually being served.
- **Derive the factor**; never write the percentage by hand.
- **Record the inputs alongside it** — both metrics, the instance, the method —
  so the claim is checkable rather than merely stated.
- **Assert the relationship in a test**, so a font update either moves the value
  or breaks the build.
- **Record a discrepancy you cannot resolve** — hypothesis, impact, status —
  rather than quietly correcting it. A wrong number whose reasoning is written
  down can be diagnosed later; one silently fixed teaches nobody why.

## 6. Check the result

- **Render both at the same corrected step and compare lowercase.** The
  arithmetic can be right and the pairing still wrong — correction aligns
  x-heights, not stroke weight, width or colour.
- **Do not correct the line-height.** Both faces look the same size at the same
  step, so they share the line box. See `typography-scale`.
- **Check vertical extent before believing an overflow report.**
  `(typoAscender − typoDescender) / unitsPerEm` — a face can carry a larger
  nominal size and still occupy less vertical space, so the corrected face is
  usually not the one overflowing.

## Representative requests

Three acceptance criteria — the no-fonts demo path, the files-given path, and
the refusal path when a font is named but unavailable — plus a routing check,
each with the mistake it prevents:
[`references/representative-requests.md`](references/representative-requests.md).

## Related

- **`typography-scale`** — applies the correction across a size ramp, and emits
  the two-scale output for non-CSS targets.

## Provenance

The metric conventions and the `$extensions` shape come from the EDS token
rework in **`equinor/ids-meetup-oslo-26`**
(Equinor-internal), prepared for the Into Design Systems Oslo meetup,
9 September 2026:

| Path | What it establishes |
| --- | --- |
| `eds-tokens-reworked/src/font-metrics.json` | Committed metrics with their sources, and the extraction discipline |
| `eds-tokens-reworked/src/formulas.ts` | `xHeightCorrection()` |
| `eds-tokens-reworked/src/build/tokens.ts` | The `derived: { expression, inputs }` extension shape |
| `eds-tokens-reworked/DECISIONS.md` | Decision 5 — bake the correction; font size only |
