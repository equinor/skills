# Positions this skill takes

Each of these costs something, and a system under delivery pressure will be
tempted to simplify it. Each rests on a measurement, quoted with the files it
came from; re-measure rather than reuse when the fonts change.

## 1. Match by measured stem, not by nominal weight

`font-weight: 400` names a coordinate on an axis whose mapping the designer
chose. Measured at the `l` midpoint, from the outlines (2026-09-01, CDN
variable files):

```
Inter    400  0.087891 em        Equinor  400  0.065001 em   (−26%)
Inter    500  0.107402 em        Equinor  500  0.086000 em   (−20%)
```

Two faces at "the same weight" differ by a quarter of a stem. The simplification
is to ship the same nominal weight for both and call it consistent; the cost is
a display face that reads lighter than the body text it sits above, at every
size. The matched values (`376.2 / 458.5 / 552.7` for tiers 300 / 400 / 500 at
the ×1.137288 size correction, re-measured 2026-09-04) are what "the same
weight" actually means; 460 in the tables below is 458.5 rounded for a tier.

**A consequence, not a justification.** APCA's readability tables assume the
stroke of a reference font, Barlow. Barlow 400 measures 0.071 em; Equinor 400
is 8% *below* that row's assumption, Inter 400 is 24% above it, and Equinor at
the Inter-matched 460 is 9% above. Matching to Inter therefore moves the
display face from under APCA's assumed stroke to over it. That is a real
accessibility gain, but it is not why the weights are matched — the pairing has
to look right — and Inter is itself heavier than the reference, so "match Inter"
overshoots "match APCA" by the same margin. When a contrast table is written,
assign a face's row by measured stem against Barlow, not by the number in its
name.

## 2. Choose tiers; do not inherit the axis

A `wght` axis is a coordinate system, not a perceptual scale:

```
Equinor   300 → 400  +80.6%      400 → 500  +32.3%      stem growth
Inter     300 → 400  +33.0%      400 → 500  +22.2%
```

The Equinor shape comes from an `avar` table remapping normalised −0.5 to
−0.42 over masters placed only at the extremes — deliberate work so that the
variable 400 reproduces an earlier static Regular, not a defect. Without the
`avar` the increments would be exactly equal. The simplification is to name
`lighter / normal / bolder` at 300 / 400 / 500 and assume three even steps; the
cost is a near-doubling followed by a third of one. Choose values that progress
evenly by measured stem, and record them as chosen.

## 3. Port letter-spacing by side space, not one-to-one

Tracking subtracts an absolute amount per character; how much that *reads*
depends on the side space it eats into. At the matched weights:

```
Inter    @400   advance 0.5363em   ink 0.4322em   side space 0.1042em   19.4%
Equinor  @460   advance 0.4905em   ink 0.4050em   side space 0.0855em   17.4%
port factor = 0.0855 / 0.1042 = 0.82
```

Identical em tracking removes 45% of one face's side space and 55% of the
other's at 32px. The simplification is one tracking ramp for both; the cost is
a display face that reads too tight exactly where tracking is most negative.

## 4. Compensate a missing optical-size axis per tier, and stop at the ceiling

Inter's `opsz` axis thins its stem as the size grows. Measured between the axis
ends, at weights 300 / 400 / 700: −4.93% / −5.56% / −1.89%. The correction
peaks at the default weight and falls away on both sides, so one curve scaled
three ways is wrong on two of them. Above the axis maximum (32px for Inter) the
reference is no longer corrected either, so a face without the axis should be
held flat there rather than extrapolated — an earlier draft extrapolated and
made 37px tighter than the value already flagged as too tight.

**The axis moves spacing as much as weight** (measured 2026-09-08). Inter's
mean side space over a–z at 500 is 0.0967em at opsz 14 and 0.0718em at opsz
32 — a 26% cut the browser applies for free — while Equinor at its matched
weight holds 0.081em. At 32px, with Equinor set at × 1.074219, Inter's gap is
2.30px and Equinor's 2.78px: Equinor reads 20% looser at the same weight and
perceived size, which is what a viewer of the overlay demo saw before any
number was taken. The compensation, `sideSpace(ref, opsz) / correction −
sideSpace(target)`, is −0.0187 / −0.0139 / −0.0141em at tiers 300 / 400 / 500
(lighter / normal / bolder, re-measured 2026-09-09 for the tiers the EDS
rework uses): the normal and bolder tiers agree to 0.0002em and the light one
needs more, because Inter's axis tightens its light weight most. At 14px every
tier is within +0.010em of zero, so the text steps need none. The alternative — one flat tracking value
for headings — is what section 5's port factor scales, and it cannot produce
a value that is zero at 14px and −0.014em at 32px from the same face.

## 5. Generate the table; commit the generated values

A weight or a factor stored as a literal, away from the metrics, goes stale
silently when the foundry revises the font. The closed form in
[`algorithm.md`](algorithm.md) reproduces every measured stem to five
decimals and every matched weight within 4.11 units (1.08% of a stem, under
one rounding step); the table is regenerated from it and the generated values
are committed with their inputs. The simplification is to type the numbers in;
the cost is that nobody can tell, a year later, which font the 458 was for.
