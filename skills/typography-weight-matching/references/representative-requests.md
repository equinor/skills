# Representative requests

Acceptance criteria for this skill, per the authoring gate in the repo's
`CLAUDE.md`. A change that breaks any of these is a regression, whatever else
it improves.

**1. "These two fonts don't look the same weight — what should the display face be?"**
→ Measure both with `scripts/stem.py`, ask whether an x-height correction is in
play, and return the matched weight per tier with the offsets shown.
*Prevents:* answering with a nominal weight ("use 500") when the question is
about rendered stem width, and forgetting that a size-corrected face needs
*less* weight because it is set larger.

**2. "Is 300 / 400 / 500 an even progression in this font?"**
→ Measure stem growth between the tiers and report it, then read `avar` and
`gvar` to explain the shape.
*Prevents:* assuming a `wght` axis is a perceptual scale. It is a coordinate
system, and uneven spacing is common and deliberate — the answer should say
which, not just that the numbers differ.

**3. "Match Helvetica Neue to Inter."** — a font is named but no file is
available. → Look in the working directory and the usual font locations first;
ask only if that turns up nothing.
*Prevents:* answering from remembered or documented metrics, which is the
failure this skill exists to stop.

**4. "The weights for the display face are already in the tokens. Are they still
right?"** — the audit case. Re-measure both files at the tokens' recorded
`instance` and confirm the `sha256`s match; compare against `$value` *and*
`derived.inputs`, including which correction the weights assumed; regenerate
the table from the algorithm and diff it byte for byte against what is
committed; only then run the test.
*Prevents:* a weight that was right for the previous release of the font, and
a table someone hand-edited after it was generated.

**5. "The Equinor headings look loose next to Inter at 32px, even after the
weight match."** → Section 4's spacing half: measure both faces' side space at
that size — `stem.py Inter.woff2 Equinor.woff2 --letter-spacing --at 500,563.1
--opsz 32 --correction 1.074219 --px 32` → −0.0141em, about −0.48px on the
34.5px heading — and emit a `letter-spacing` token per step beside the
weights. Say why it is zero at the text sizes: Inter's `opsz` axis tightens
its spacing as it grows and Equinor has no axis, so the gap opens with size.
*Prevents:* one flat heading tracking typed from taste, and tracking applied
to the body text where the two faces already agree.

A sixth, for routing: **"these two fonts look like different sizes"** must load
`typography-x-height-alignment`, not this skill. Size and weight are different
complaints with different fixes, and the descriptions carry `DO NOT USE FOR:`
cues to separate them.
