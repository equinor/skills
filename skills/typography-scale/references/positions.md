# Positions

Three places where this skill takes a stance that costs something, with the
evidence for it. Systems under delivery pressure often simplify in the opposite
direction, and these are the arguments for not doing that.

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
behind the line-height curve in section 2. Type designers have compensated for
this for as long as type has had sizes.

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
