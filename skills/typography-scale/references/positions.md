# Positions

Five places where this skill takes a stance that costs something, with the
evidence for it. Systems under delivery pressure often simplify in the opposite
direction, and these are the arguments for not doing that.

Then two limits of the snap grid, recorded where someone hitting them can find
them.

None of this is a matter of taste. Each has a measurement behind it.

## 1. Snap sizes to half a pixel, not whole pixels

**The simplification:** round every step to a whole pixel, so the scale reads
`11, 12, 14, 16, 18, 21` instead of `10.5, 12, 14, 16, 18.5, 21`.

**Why it costs more than it looks.** The formula asks for a constant
**+14.87%** per step. Rounding is what you pay to land on usable numbers, so the
question is how much distortion each grid buys:

```
                step ratios                       worst deviation from intent
half-pixel      +14.29  +16.67  +14.29  +15.62         12.1%
whole-pixel     + 9.09  +16.67  +14.29  +12.50         38.9%
                  ↑ the bottom of the ramp
```

Whole-pixel rounding misses by up to **38.9%** against half-pixel's 12.1% — and
the error concentrates at the small end, where the steps are closest together
and a misjudged one is most visible. `11 → 12` is a +9.09% step sitting next to
a +16.67% step: nearly a 2× swing between neighbours in the range that carries
body text, labels and captions.

Half a pixel is not sub-pixel precision for its own sake. It is the coarsest
grid that keeps the small end proportional.

## 2. Keep a second, compressed line-height curve

**The simplification:** ship one line-height curve and let a ratio (commonly
1.5) cover reading text, dropping the tighter curve used for UI labels.

**Why it costs more than it looks.** The two curves answer different questions.
Reading text wants leading that separates lines so the eye returns to the right
one. A UI label wants the opposite: when a label wraps to two lines it must read
as **one object**, not two stacked lines, or the control's hit area and visual
weight stop matching its meaning.

The failure is invisible in a specimen and obvious in a product — it shows up in
wrapped buttons, chips, table headers and tabs, at narrow widths, on the surfaces
where labels wrap most. There is field evidence from a shipped mobile
application where removing the compressed curve produced exactly this.

One curve plus a literal ratio at the composition layer is not equivalent: it
moves a typographic decision out of the scale and into whichever stylesheet
happens to set it, where nothing checks it and nothing records why.

## 3. Derive font-weight and letter-spacing per step

**The simplification:** one weight per role, one tracking value, applied at every
size.

**Why it costs more than it looks.** Large text needs proportionally *less*
weight and *tighter* tracking than small text — the same optical principle
behind the line-height curve in [`SKILL.md`](../SKILL.md) section 2. Type
designers have compensated for this for as long as type has had sizes.

Variable fonts make it mechanical rather than manual, and one measurement shows
how far a typeface will carry you on its own. Inter ships an `opsz` axis
(14–32); Chrome applies it automatically, because `font-optical-sizing: auto` is
the initial value. Measured by rendering and comparing advance widths:

```
font-size   auto == font-variation-settings: 'opsz' <font-size>
16px        76.438 == 76.438
20px        95.547 == 95.547
24px       114.656 == 114.656
28px       133.766 == 133.766
```

So `opsz` tracks the font size in **px**, continuously — no steps — and clamps
at the axis ends. Two consequences:

- **Above the axis maximum, correction stops.** Inter's ends at 32. Every step
  above that — the display sizes, where optical compensation matters *most* —
  renders at the same optical size as a 32px heading.
- **A face without an `opsz` axis gets nothing at all.** Checked directly:
  Inter has `opsz`; the Equinor and CommitMono variable fonts have only `wght`
  (plus `ital` on CommitMono). Pair a face that self-corrects with one that
  cannot and the mismatch grows with size, on top of any x-height correction.

A derived per-step weight and tracking ramp is how you get that refinement on
faces the foundry did not build it into, and above the range where the ones that
did stop helping. It is the same move as the line-height curve: encode the
optical adjustment in the scale instead of hoping each consumer applies it.

---

## 4. Ten close steps, not six wide ones

**The simplification:** widen the ratio — 1.25 or 1.333 — so the ramp has fewer,
more obviously distinct steps, and drop from ten labels to six.

**Why it costs more than it looks.** The target is an **application interface**:
UI chrome, form labels, table cells, captions and dense data, where several
sizes must coexist within a few pixels of each other and still read as
deliberate. `2^(1/5)` ≈ 1.1487 gives that. A page-oriented scale wants the
opposite — fewer, wider steps and a much larger display end — and judged as one,
this ramp looks indecisive. It is not a compromise between the two; it is fitted
to one of them, and the skill should be read that way.

The tightness also costs nothing at the point of use, because **a hierarchy
sub-selects steps rather than walking them.** Taking every second step from
`2xl` gives a heading ramp at comfortable density:

```
2xl 21px   4xl 28px   6xl 37px        (skipping 3xl 24.5 and 5xl 32)
```

Every second step is `2^(2/5)` ≈ 1.3195 — a conventional heading ratio, obtained
free from the same constants, with the skipped steps still available for the
cases that need them. Widening the ratio to get that spacing throws away the
intermediate sizes the interface needs; sub-selecting keeps both.

Ten steps is a palette, not a sequence.

---

# Limits of the snap grid

Neither of these is a reason to change the grid. Both are reasons to state the
limit, because in each case the formula promises something the rounded output
does not always deliver — and the gap is small enough to read as a bug.

## 5. Snap the corrected size to half a pixel, not to a scale step

**The simplification:** the x-height correction for the pair measured here is
`× 1.137288` and one step of the scale is `× 1.1487`, so a corrected display
size lands almost one step above its text size. Read that as "one step up,
exactly" and reuse the text ramp for the display face: fewer distinct values,
and a Figma display style can share the text variable one step up.

**Why it costs more than it looks.** Compared with the true correction at
comfortable density (2026-09-04):

```
step   text   exact    half-px   error    on-step   error
sm     12     13.65    13.5      -1.1%    14        +2.6%
lg     16     18.20    18        -1.1%    18.5      +1.7%
2xl    21     23.88    24        +0.5%    24.5      +2.6%
5xl    32     36.39    36.5      +0.3%    37        +1.7%
```

Five steps (`xs md xl 3xl 4xl`) agree under both rules, and `6xl` has no step
above it to snap to unless the ramp is extended (which gives 42, agreeing).
Half-pixel keeps the alignment error under 1.1% everywhere; on-step reaches
2.6%, where a size difference starts to read, and does so at the small steps
that carry interface text. The saving is not worth a 2.6% miss on the alignment
the correction exists to deliver. Section 4 of `SKILL.md` therefore re-snaps to
the *same grid* as the text ramp, the emitter and the shipped build agree
(`12 / 13.5 / 16 / 18` for `xs`–`lg` at comfortable), and `scale.py --check`
holds the four rows above as a fixture.

## 6. The octave doubling is exact in the formula, not always in the output

Section 1 of [`SKILL.md`](../SKILL.md) leans on the octave landmark: five steps
up doubles the size. That is what makes it safe to sub-select steps for a
hierarchy, because any step you land on keeps a nameable relation to body
text.

The formula doubles exactly. The **snapped output** does not, because 0.5px is
coarse relative to the gap between steps at the small end. Across the three EDS
densities, 5 of the 15 pairs miss by half a pixel:

```
compact      xs   9    -> 2xl 18.5     2x =  18
compact      md   12   -> 4xl 24.5     2x =  24
comfortable  sm   12   -> 3xl 24.5     2x =  24
relaxed      xs   12   -> 2xl 24.5     2x =  24
relaxed      xl   21.5 -> 6xl 42.5     2x =  43
```

The `lg → 5xl` pair — the one the scale is anchored on, where body text sits —
holds at **every** density, which is why the claim survives in the form that
section states it. The rest is worth enumerating rather than discovering: a
reader who takes "doubles every n steps" literally will eventually find a
0.5px discrepancy and file it.

Treat the list as a fixture. A sixth deviation means the constants or the snap
moved, and should fail a build rather than pass quietly.

## 7. A correction smaller than the snap grid does not survive it

Section 4 of [`SKILL.md`](../SKILL.md) applies `round(step × correction,
0.5px)`. When the correction is small, the grid is coarser than the correction
itself, and the *effective* per-step correction stops being constant.

Open Sans paired with Montserrat gives `× 1.019345` — an intended **+1.93%**.
After snapping, at comfortable density:

```
step    text  display   effective
xs      10.5     10.5      0.00%   <- erased
sm      12       12        0.00%   <- erased
md      14       14.5     +3.57%   <- nearly double the intent
lg      16       16.5     +3.13%
xl      18.5     19       +2.70%
3xl     24.5     25       +2.04%
6xl     37       37.5     +1.35%
```

At 12px one snap unit is **4.2%**, so a 1.93% correction cannot be represented
on that grid at all: it rounds to nothing or to twice its intended size. The
error is largest exactly where most interface text lives.

This is specific to the baked two-ramp mechanism. `size-adjust` corrects
continuously and has no such floor, so the CSS-only path is unaffected — which
is easy to miss, because that section's worked example uses `× 1.137288`
(+13.7%), comfortably above the grid at every step.

**What to do.** Compute the effective ratio per step before shipping, and if the
correction is below roughly one snap unit at the smallest step, choose
deliberately between: accepting the unevenness; dropping the correction, since a
well-matched pair may be better served by none than by an uneven one; or giving
the display ramp a finer grid, at the cost of leaving the shared half-pixel one.
Do not let rounding make that choice silently.

## 8. One correction per ramp is a limit of the script, not of the method

`scale.py --correction` takes a single factor and writes it into every display
step. That is exact only when the reference face's x-height does not move
along the ramp. Inter's does: its `opsz` axis lowers `sxHeight` from 0.545898
at opsz 14 to 0.515625 at opsz 32, so the correction against Equinor falls
from 1.137288 to 1.074219 and a flat factor sets a 32px heading 5.9% too large
(measured 2026-09-07; the table is in
`typography-x-height-alignment/references/optical-size.md`). Outcome 2 there
asks for a correction per step. Until `scale.py` accepts one — a per-step
`--correction` map, or the per-step token group as input — bake the display
ramp by running the derivation once per step, and say so in the tokens'
`derived.inputs`, as `demo/typography/` does.
