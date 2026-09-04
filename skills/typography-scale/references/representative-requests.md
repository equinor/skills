# Representative requests

Acceptance criteria for this skill, per the authoring gate in the repo's
`CLAUDE.md`. A change that breaks any of these is a regression, whatever else
it improves.

**1. "Build a type scale based on the Equinor Design System scale."**
→ Load this skill (not a sibling); ask the two questions in sections 4 and 5
only where they change the output; run `scripts/scale.py` and emit the tokens
first, then CSS in the branch the answer chose; reproduce the comfortable ramp
`10.5 12 14 16 18.5 21 24.5 28 32 37` with read line-heights
`16 16 20 24 24 28 32 36 36 40`.
*Prevents:* a hand-typed table, and CSS as the only artefact.

**2. "Give me the line-heights for that scale, for UI labels rather than
prose."** → The compressed curve, `12 12 16 20 20 24 28 28 32 36` at
comfortable, from the same script and the same token file — not a second scale.
*Prevents:* reaching for a literal ratio at the composition layer, which
section 2 and `positions.md` §2 argue against.

**3. "Build the EDS scale for Inter and Equinor and put it in Figma."**
→ `typography-x-height-alignment` first for the factor; then this skill with
`--correction` for the two-ramp branch and `--format figma` for the variables
and text styles; density as modes; styles bound to variables. If no Figma MCP
is available, write the scripts and say how to run them.
*Prevents:* pushing one ramp and leaving the display face small in Figma, and
text styles with literal sizes that cannot follow a mode.

**4. "There is already a scale in the tokens. Is it right?"** — the audit
case. Reproduce the preset fixture with `--check`; recompute the committed
values from the constants; regenerate the artefacts and diff byte-for-byte;
only then read values and run the test.
*Prevents:* trusting a build that nobody has regenerated since it was hand
edited.

A fifth, for routing rather than behaviour: **"Align the x-height of these two
fonts"** must load `typography-x-height-alignment`, not this skill. The two
share almost all their vocabulary, which is what the `DO NOT USE FOR:` cues in
both descriptions exist to separate.
