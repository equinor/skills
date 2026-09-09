---
name: typography-weight-matching
description: 'Use when two paired font families look mismatched in weight or spacing rather than in size — one reads heavier, or headings look loose beside body text. USE FOR: finding the weight in face B that matches face A, deriving a per-step weight and letter-spacing ramp, checking whether a weight axis is perceptually evenly spaced, compensating for a face that lacks an optical-size axis, emitting matched weights, a tracking port factor and a letter-spacing compensation as DTCG tokens. DO NOT USE FOR: matching apparent size (use typography-x-height-alignment), building the size ramp (use typography-scale), choosing which typefaces to pair.'
---

# Weight matching

Two faces at the same nominal weight rarely look equally heavy. `font-weight:
400` is a *coordinate*, not a measurement — what it renders depends on where the
designer put that master and how the axis is mapped. Set Inter and Equinor both
at 400 and Equinor reads noticeably lighter, because its stem at 400 is 26%
thinner.

The same is true across sizes. Some faces carry an `opsz` axis and are corrected
automatically as they scale; faces without one are not. Pair the two and the
mismatch grows with size, on top of any x-height difference.

This skill measures both and derives the corrections.

## What you need

1. **Both font files.** Metrics come from the binary; nothing else is
   trustworthy.
2. **Which face is the reference** — normally the text face.
3. **The x-height correction, if the pair is being size-matched.** A corrected
   face is set larger, so its stems scale up with it and it needs *less* weight
   to match. Run `typography-x-height-alignment` first and pass its factor in.

`assets/fonts/` bundles Inter (SIL OFL), so `scripts/stem.py` with no
arguments measures a real variable face with both a `wght` and an `opsz` axis —
the fastest check that your environment works, and the selftest's fixture.

## 1. Measure stem width from the outlines

```bash
skill=.claude/skills/typography-weight-matching   # where the installed copy lives
python3 -m venv .venv && .venv/bin/pip install fonttools brotli   # project root, not $skill
.venv/bin/python $skill/scripts/stem.py FONT.woff2 --weights 300,400,500,700
```

Skip the venv line if the project already has a Python with `fontTools` and
`brotli`; never create anything inside `$skill`, which `npx skills update`
replaces. Every result records the file it came from by path and `sha256`.

`scripts/stem.py` reads the stem at the glyph's **vertical midpoint** by
intersecting the outline with a horizontal line — not from the bounding box.
The two diverge at the extremes of a weight axis, where flare or overshoot
widens the box without widening the stroke.

**Known divergence.** Outline and rendered measurements agree exactly across
normal working weights, but for one face at its axis maximum they differed by
2.8%. Outlines are what the font specifies, so this skill uses them; if you are
working at an axis extreme and precision matters, render and compare.

## 2. Check whether the axis is evenly spaced

Do this before choosing tiers. A `wght` axis is a coordinate system, not a
perceptual scale, and the spacing is often uneven:

```
Equinor   300 → 400  +80.6%      400 → 500  +32.3%      stem growth
Inter     300 → 400  +33.0%      400 → 500  +22.2%
```

`lighter` / `normal` / `bolder` reads as three even steps. In that first face it
is a near-doubling followed by a third of one. Anything assuming even tiers — a
weight ramp, a variable set, a designer picking "one step lighter" — inherits
that.

The cause is usually the **`avar` table**, which remaps the axis before
interpolation. Read it and the masters:

```python
TTFont(path)["avar"].segments          # axis remapping, if any
TTFont(path)["gvar"].variations[name]  # tuples → where the masters are
```

A face with masters only at its extremes plus an `avar` breakpoint will be
piecewise linear with a knee at the breakpoint. That is deliberate work, usually
so the variable font's 400 reproduces an original static Regular — not a defect.
But it does mean the named tiers are not evenly spaced, and the fix is to
**choose values rather than inherit them.**

## 3. Match weights across the pair

```bash
.venv/bin/python $skill/scripts/stem.py REFERENCE.woff2 TARGET.woff2 \
  --match 300,400,500 --correction 1.137288
```

Returns the target weight whose stem matches the reference at each tier, at the
same *perceived* size. `--correction` is the x-height correction **at the size
being matched**: when `--opsz` pins the reference's optical size, pass the
correction sampled at that same `opsz` (`typography-x-height-alignment`,
`references/optical-size.md`), not the text step's — Inter's x-height falls
5.5% between opsz 14 and 32, and the flat factor at 32px puts the bolder match
about 30 weight units low (529.8 against 563.1 at tier 500, where the command
above — measured at the text size — emits 552.7). The target's curve is
sampled once and inverted by interpolation, then corrected with one real
measurement per tier — instancing a
variable font is what costs, so the sampling dominates. Expect 20–30 seconds
for a large variable face such as Inter (measured 2026-09-04); each extra tier
adds one instancing.

**The offsets will not be constant.** Where the target's response curve is
concave, the same relative stem change costs fewer weight units at the light end
than the heavy end. Expect something like +75 / +60 / +55 rather than one offset.

**These are stem-matched.** They mean "looks as heavy as the reference at this
tier". If the display face is meant to read *heavier* than body text, apply an
emphasis offset on top of the matched values, not instead of them.

## 4. Compensate for a missing optical-size axis

An `opsz` axis makes a face lighter and tighter as it grows, and the browser
applies it for free — `font-optical-sizing: auto` is the initial value, and the
axis value tracks the font size in px, clamped to the axis range.

A face without the axis gets none of that. To give it the same treatment
deliberately, measure what the reference's axis does and reproduce it:

```
relStem(px) = stem(ref, opsz=clamp(px, lo, hi)) / stem(ref, opsz=at-reference-size)
target weight(px) = matched weight, adjusted so the target's stem falls by the same ratio
```

Two things to know before trusting a single curve:

- **The axes are not independent.** In the pair measured here, the optical
  correction peaked at the reference face's *default* weight and fell away on
  both sides — −5.56% at 400 against −4.93% at 300 and −1.89% at 700. Compute
  per tier rather than scaling one curve three ways.
- **The correction stops at the axis maximum.** Above it, the face is no longer
  corrected — usually the display range, where it matters most, and where the
  face without an axis was never corrected at all.

The full closed form, and how it was verified, is in
[`references/algorithm.md`](references/algorithm.md).

**The same axis tightens the spacing**, and this half is the one a reader
sees first: at 32px the face with the axis sits closer, letter to letter,
than the face without it. Inter's side space at 500 falls from 0.0967em at
opsz 14 to 0.0718em at opsz 32, 26%; Equinor's stays wherever its weight puts
it. The compensation is a letter-spacing per step, in the **target's** em:

```
letterSpacing(step) = sideSpace(ref, opsz = step px, tier) / correction(step)
                    − sideSpace(target, matched weight)
```

```bash
.venv/bin/python $skill/scripts/stem.py Inter.woff2 Equinor.woff2 \
  --letter-spacing --at 500,563.1 --opsz 32 --correction 1.074219 --px 32
```

`correction` is the x-height correction **at that opsz**, as in section 3.
Measured for the pair here on 2026-09-09, in Equinor's em, for the tiers
lighter / normal / bolder = Inter 300 / 400 / 500: +0.010 / +0.006 / +0.004 at
14px — under a sixth of a pixel — and −0.0187 / −0.0139 / −0.0141 at 32px,
−0.65 to −0.5px on the 34.5px heading. The normal and bolder tiers agree to
0.0002em at the top of the axis because what is being compensated is the
axis, not the weight; the light tier needs more because Inter's axis tightens
its light weight most (side space 0.1138 → 0.0769em, 32%). Every tier crosses
zero between `xl` and `2xl` (18.5–21px), so emit per step — and per tier,
because the light tier wants 0.005em more at the top of the axis — and expect
the text steps to come out at zero. The target is measured at its own default
`opsz`, which is the point when it has no axis; the script warns when it has
one. Section 5 then
ports any tracking ramp the reference *already* has on top of this, and a
design system's own per-style tracking adds the same way: this value is a
compensation, never a replacement.

## 5. Port letter-spacing by side space, not one-to-one

Tracking removes an absolute amount per character, but how it *reads* depends on
how much side space was there to begin with.

```bash
.venv/bin/python $skill/scripts/stem.py REFERENCE.woff2 TARGET.woff2 --tracking --at 400,460
```

Pass the **matched** weights — side space shrinks as ink grows, so measuring
both faces at 400 misstates the ratio for a pair that is not weight-matched.
(460 is the matched 458.5 rounded to the nearest 5 for a named tier; the
factor is 0.821 either way.)

```
Inter    @400   advance 0.5363em   ink 0.4322em   side space 0.1042em   19.4%
Equinor  @460   advance 0.4905em   ink 0.4050em   side space 0.0855em   17.4%
port factor = 0.0855 / 0.1042 = 0.82
```

That is Inter at its default `opsz`, 14. Pin `--opsz` to read the reference
at a heading size and the factor moves with it (1.13 at opsz 32, where Inter
has tightened and Equinor has not); the token records which.

So the target's tracking ramp is the reference's **scaled by 0.82**. Identical em
tracking would eat a larger share of the target's gap and read too tight — at
32px, −0.047em removes 45% of one face's side space and 55% of the other's.

## 6. Ask before emitting, then emit tokens first

> Will these weights be used in CSS only, or also in Figma, React Native or
> another non-CSS target?

The answer changes the value, not the packaging. CSS and Figma take the
matched weight as measured — `font-weight: 458.5` is valid CSS and a variable
font renders it; a Figma text style binds `fontWeight` to a variable holding it.
React Native rounds weights to hundreds, so there emit with `--snap 100`: the
token carries the snapped value, the measured one and the residual, and the
pairing is checked at the snapped weight rather than assumed. The same applies
in CSS wherever the *variable* font may not load and a static face stands in —
a question for the project's `browserslist` and its `@font-face` fallbacks,
not for this skill. For the letter-spacing compensation the answer changes the
**unit**: CSS takes the em value as is; Figma and React Native take px, so
pass `--px` with the step's size and the token carries em, percent and px. A
Figma variable bound to letter-spacing is applied in pixels whatever unit the
layer shows — switching the layer to `%` drops the binding (Plugin API,
checked 2026-09-09) — so the px is the value that goes into Figma. A
question that would not change the output is not asked.

Then emit the tokens, and derive everything else from them:

```bash
.venv/bin/python $skill/scripts/stem.py REF.woff2 TARGET.woff2 \
  --match 300,400,500 --correction 1.137288 --format tokens --display Equinor
.venv/bin/python $skill/scripts/stem.py REF.woff2 TARGET.woff2 \
  --tracking --at 400,458.5 --format tokens --display Equinor
.venv/bin/python $skill/scripts/stem.py REF.woff2 TARGET.woff2 \
  --letter-spacing --at 500,563.1 --opsz 32 --correction 1.074219 --px 32 \
  --format tokens --display Equinor
```

One `fontWeight` token per tier, one port-factor token, and one
`letter-spacing` compensation per tier and step, each with its derivation, the
axis location it was measured at and the `sha256` of both files:
[`references/token-shape.md`](references/token-shape.md). Pass
`--correction-token` with the alias of the x-height token so the chain back to
the measurement survives.

## 7. Verify

- **Look at it.** The arithmetic can be right and the pairing still wrong;
  weight matching does not fix width, contrast or colour.
- **Check the tiers you chose actually progress evenly**, by re-measuring stem
  growth between them. That is the claim worth being able to defend.
- **Re-derive on font updates.** A weight or factor stored as a literal, far
  from the metrics, goes stale silently when the foundry ships a revision.
  Generate the table from the algorithm and commit the generated values.

## Test pairings

Optical-size axes are common but far from universal, so mixed-capability pairs
are the normal case. Checked directly with `--weights`:

| Has `opsz` | No `opsz` |
| --- | --- |
| Inter | Roboto |
| Literata | Open Sans |
| Source Serif 4 | Lora |
| Fraunces | Montserrat |
| Nunito Sans | Work Sans |

Any left-column face paired with a right-column one exercises everything here.
**Literata + Work Sans** and **Source Serif 4 + Montserrat** are good tests: real
pairings, one axis-corrected face and one not, and both freely available. Fetch
from `github.com/google/fonts`.

## Representative requests

Acceptance criteria — the matched-weight path, the uneven-tier check, the
refusal path when a file cannot be obtained, auditing committed weights, and
the headings that read loose at 32px — plus a routing check:
[`references/representative-requests.md`](references/representative-requests.md).

## Positions this skill takes

Five choices here cost something, and each rests on a measurement rather than a
preference: matching by measured stem, choosing tiers instead of inheriting the
axis, porting tracking by side space, compensating a missing `opsz` per tier
and stopping at the axis ceiling, and committing generated values with their
inputs. The first also carries an accessibility consequence worth knowing about
before it is claimed as a justification:
[`references/positions.md`](references/positions.md).

## Related

- **`typography-x-height-alignment`** — run first when the pair also differs in
  apparent size; its correction factor is an input here.
- **`typography-scale`** — the size ramp these weights are indexed against.

## Provenance

Derived in the EDS token rework in **`equinor/ids-meetup-oslo-26`**
(Equinor-internal), `eds-tokens-reworked/docs/optical-sizing.md`.
