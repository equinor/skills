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

A fourth, for routing: **"these two fonts look like different sizes"** must load
`typography-x-height-alignment`, not this skill. Size and weight are different
complaints with different fixes, and the descriptions carry `DO NOT USE FOR:`
cues to separate them.
