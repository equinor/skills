---
name: typography-weight-matching
description: 'Use when two paired font families look mismatched in weight or spacing rather than in size — one reads heavier, or headings look loose beside body text. USE FOR: finding the weight in face B that matches face A, deriving a per-step weight and letter-spacing ramp, checking whether a weight axis is perceptually evenly spaced, compensating for a face that lacks an optical-size axis. DO NOT USE FOR: matching apparent size (use typography-x-height-alignment), building the size ramp (use typography-scale), choosing which typefaces to pair.'
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

## 1. Measure stem width from the outlines

```bash
skill=.claude/skills/typography-weight-matching   # where the installed copy lives
python3 -m venv .venv && .venv/bin/pip install fonttools brotli   # project root, not $skill
.venv/bin/python $skill/scripts/stem.py FONT.woff2 --weights 300,400,500,700
```

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
same *perceived* size. The target's curve is sampled once and inverted by
interpolation — instancing a variable font is expensive, so a search loop that
re-instances per step is what makes this slow. Expect a few seconds for a woff2
and around twenty for a full variable TTF.

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
  both sides — −5.56% at 400 against −4.94% at 300 and −1.90% at 700. Compute
  per tier rather than scaling one curve three ways.
- **The correction stops at the axis maximum.** Above it, the face is no longer
  corrected — usually the display range, where it matters most, and where the
  face without an axis was never corrected at all.

The full closed form, and how it was verified, is in
[`references/algorithm.md`](references/algorithm.md).

## 5. Port letter-spacing by side space, not one-to-one

Tracking removes an absolute amount per character, but how it *reads* depends on
how much side space was there to begin with.

```bash
.venv/bin/python $skill/scripts/stem.py REFERENCE.woff2 TARGET.woff2 --tracking --at 400,460
```

Pass the **matched** weights — side space shrinks as ink grows, so measuring
both faces at 400 misstates the ratio for a pair that is not weight-matched.

```
Inter    @400   advance 0.5363em   ink 0.4322em   side space 0.1042em   19.4%
Equinor  @460   advance 0.4905em   ink 0.4050em   side space 0.0855em   17.4%
port factor = 0.0855 / 0.1042 = 0.82
```

So the target's tracking ramp is the reference's **scaled by 0.82**. Identical em
tracking would eat a larger share of the target's gap and read too tight — at
32px, −0.047em removes 45% of one face's side space and 55% of the other's.

## 6. Verify

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

Acceptance criteria — the matched-weight path, the uneven-tier check, and the
refusal path when a file cannot be obtained:
[`references/representative-requests.md`](references/representative-requests.md).

## Related

- **`typography-x-height-alignment`** — run first when the pair also differs in
  apparent size; its correction factor is an input here.
- **`typography-scale`** — the size ramp these weights are indexed against.

## Provenance

Derived in the EDS token rework in **`equinor/ids-meetup-oslo-26`**
(Equinor-internal), `eds-tokens-reworked/docs/optical-sizing.md`.
