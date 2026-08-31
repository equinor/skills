# Feedback: `typography-scale`

From building the Open Sans + Montserrat scale on 2026-08-30 (EDS preset,
Figma/RN target, two-ramp output). Reproducible via `scripts/test-scale.mjs`
and `scripts/verify-in-browser.mjs` in this directory.

## What worked

- **The EDS check values are the single most useful thing in the skill.** Being
  able to assert `10.5 12 14 16 18.5 21 24.5 28 32 37` / `16 16 20 24 24 28 32
  36 36 40` turned "I implemented the formula" into "the implementation is
  proven". Both curves and the snap were right first try *because* there was
  something to check against. Every skill that ships an algorithm should ship
  its expected output like this.
- **The §3 density trade-off note paid off immediately.** The label-indexing
  consequence reproduced exactly as documented (`16px` → `compact/xl` 20px,
  `comfortable/lg` 24px, `relaxed/md` 24px), so it went straight into
  DECISIONS.md as a kept choice rather than being discovered later as a bug.
- **§6's "read back from a real browser, not the generator"** caught nothing,
  but only because it forced building the check — which now proves the eventual
  switch from baked values to live `round()`/`pow()` is value-neutral.
- **§5's instruction to verify browser support rather than recall it** was
  correct to insist on: `caniuse/css-math-functions` covers only min/max/clamp,
  so the obvious lookup gives a misleading pass. `round()` turns out to be
  Baseline *newly*, not widely — which changed the output shape.

## 1. The "doubles every n steps" claim is true of the formula, false of the output

§1 states the octave property as unconditional:

> `lg` → five steps up is exactly `2 × lg`, **at every density, forever**.

The `lg → 5xl` example does hold at all three densities. But the general claim
does not survive the 0.5px snap — **5 of 15 pairs miss**:

```
compact      xs   9   -> 2xl 18.5   (2x = 18)
compact      md   12  -> 4xl 24.5   (2x = 24)
comfortable  sm   12  -> 3xl 24.5   (2x = 24)
relaxed      xs   12  -> 2xl 24.5   (2x = 24)
relaxed      xl   21.5 -> 6xl 42.5  (2x = 43)
```

This matters because the octave landmark is the stated justification for the
ratio, and it is what makes sub-selecting steps (headings at 2xl/4xl/6xl) safe.
A reader who takes "forever" literally will eventually find a 0.5px discrepancy
and file it as a snap bug.

**Suggested fix:** keep the claim, qualify it — the property is exact in the
formula and holds for `lg` at every density; elsewhere the snap can cost 0.5px
at the small end. Consider shipping the exception list the way §6 ships
enumerated deviations, so implementations assert it rather than discover it.

## 2. §4 doesn't warn that a small correction can be swallowed by the size snap

The two-ramp path applies `round(step × correction, 0.5px)`. When the correction
is small, the snap grid is coarser than the correction itself and the *effective*
per-step correction becomes wildly non-uniform. With Montserrat's `1.019345`
(+1.93% intended):

```
xs, sm   0.00%   correction lost entirely
md, lg  +3.57%   nearly double the intended value
6xl     +1.35%
```

At 12px one snap unit is 4.2%, so a 1.93% correction **cannot be represented on
that grid at all**. The CSS-only path has no such problem — `size-adjust`
corrects continuously — so this is a defect specific to the mechanism §4
recommends for Figma/RN, and it is invisible unless you compute the effective
ratio per step.

The skill's own worked example (`× 1.137288`, ~14%) is large enough that the
issue never shows. Well-matched pairs are common, and they are exactly the case
where the two-ramp machinery quietly stops earning its keep.

**Suggested fix:** in §4, after "re-snap to the same grid", note that if the
correction is smaller than roughly one snap unit at the smallest step, the
correction will not survive rounding at the small end — and give the guidance
for that case (accept, drop the correction, or finer grid for the display ramp).
A one-line diagnostic in the worked example would make it concrete.

## 3. State that this is a scale for an application interface

The constants only make sense for app UI — ten tightly-spaced steps, a density
axis, a 4px grid, and a `compressed` curve for scanned labels. A web/editorial
page wants fewer and wider steps, a much larger display end, and probably fluid
sizing. Nothing in the skill says which it is, so the tight ratio reads as a
questionable choice rather than a deliberate fit, and invites exactly the
"shouldn't this be 1.25?" objection the skill otherwise pre-empts well.

**Suggested fix:** one sentence near the top. It would also reinforce §6's "no
off-scale sizes" rule, which is far easier to hold in an interface than on a
page.

## 4. Small: the ramp is a palette, and the skill never says so

Ten steps invites the assumption that a hierarchy walks them. It doesn't —
headings sub-select, e.g. every second step from `2xl` (`21 / 28 / 37` at
comfortable), which is `2^(2/5)` ≈ 1.3195, a conventional heading ratio obtained
free from the same constants. Worth a line, because it dissolves the "too tight"
objection without changing anything.
