# Representative requests

Acceptance criteria for this skill, per the authoring gate in the repo's
`CLAUDE.md`. A change that breaks any of these is a regression, whatever else
it improves.

**1. "Build a medium button. How tall is it and what's the padding?"**
→ Ask CSS-only or also Figma/RN; then `spacing.py control --size md
--proportion squished --label md`: inset 16 / 12, label 14px on a 16px
compressed line box, cap 12, padding 16 / 10, height 36 at comfortable — and
24 / 44 at compact / relaxed from the same recipe. The height is read back,
never typed; the padding stays 10 and is not rounded to 12.
*Prevents:* `height: 36px` and `padding: 12px 16px`, which are right today and
wrong at the next density.

**2. "Two buttons side by side, Save and Cancel — what gap?"**
→ `sm`: they are a cluster, one rung below the container's `md`. Say why: the
gap measures box to box, the eye measures ink to ink, and each button brings
its own inset.
*Prevents:* the container gap between siblings, which reads too far apart even
though it is on the ladder.

**3. "A toolbar with a search field in it — how tall?"**
→ Never authored: the field's emergent height plus the `xs` seat rung raw above
and below (`spacing.py strip --control 36`): 52 at comfortable, 36 / 68 at
compact / relaxed. Raw because controls carry no half-leading.
*Prevents:* an authored 56px bar, and optical compensation applied to a box
whose edges are real.

**4. "Port these spacing tokens to compact density."**
→ Same sequence, offset one rung down: every rung and every inset moves
together, no rule changes; `spacing.py tokens --out …` emits all three
densities from the one source. Check that `3xl` at relaxed is flagged
extrapolated.
*Prevents:* a second hand-made table that drifts from the first.

A fifth, for routing: **"what line-height goes with 14px?"** is
`typography-scale`, and **"align the paragraphs to the baseline grid"** is the
baseline-grid skill; this skill spaces boxes, not text.
