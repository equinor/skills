# Representative requests

Acceptance criteria for this skill, per the authoring gate in the repo's
`CLAUDE.md`. A change that breaks any of these is a regression, whatever else
it improves.

**1. "Show me how x-height alignment works."** — no fonts named.
→ Run `scripts/xheight.py` with no arguments and walk through the result:
Inter `0.545898`, EB Garamond `0.400000`, correction `1.364746`.
*Prevents:* explaining the technique in the abstract when a runnable
demonstration is sitting in `assets/fonts`.

**2. "Align the x-height of font-a and font-b; font-a is the master."** — files
given. → Measure both, derive the correction, emit the DTCG token with
`derived: {expression, inputs}` and the metrics recorded, then ask whether the
target is CSS-only before emitting `size-adjust` or corrected sizes.
*Prevents:* a bare number in chat with no provenance, and picking a delivery
mechanism before knowing where the type renders.

**3. "Align Helvetica Neue with Inter."** — fonts named, no path given.
→ Look in the working directory and the usual font locations first; ask only if
that turns up nothing. Never answer from remembered or documented metrics.
*Prevents:* both the recalled-metrics failure this skill exists to stop, and a
needless round trip when the files are sitting in the project.

A fourth, for routing rather than behaviour: **"Build me a type scale based on
the EDS scale"** must load `typography-scale`, not this skill. The two share
almost all their vocabulary, which is what the `DO NOT USE FOR:` cues in both
descriptions exist to separate.

