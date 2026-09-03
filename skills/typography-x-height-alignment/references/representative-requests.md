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

**5. "There is already a correction in the tokens. Is it right?"** — the audit
case, and the one §5 of the skill argues for without giving a procedure. Do it
in this order: re-measure from the binaries at the token's recorded `instance`
and confirm the `sha256`s still match the files; compare the result against
the committed `$value` *and* against `derived.inputs`; regenerate every
artefact the token feeds (`@font-face`, corrected sizes) and diff the output
byte-for-byte against what is committed; only then run the test, and check it
reaches an assertion. The same order applies to a committed type scale — see
`typography-scale` §6.
*Prevents:* trusting a stale derived value, which is §5's failure mode; and the
quieter one, where the numbers are right but the generated file has been
hand-edited since and nothing reproduces it.

A sixth, for routing rather than behaviour: **"Build me a type scale based on
the EDS scale"** must load `typography-scale`, not this skill. The two share
almost all their vocabulary, which is what the `DO NOT USE FOR:` cues in both
descriptions exist to separate.

