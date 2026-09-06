# Representative requests

Acceptance criteria for this skill, per the authoring gate in the repo's
`CLAUDE.md`. A change that breaks any of these is a regression, whatever else
it improves.

**1. "What background does the icon button get?"**
→ Ghost: transparent at rest, `bg-{tone}-fill-ghost-hover` (step 3) on hover,
`-active` (step 4) on active, ordinary `icon-{tone}` ink. Not muted, not a
custom tint. If asked for a filled icon button, that is a different component
(the round ghost icon button is the only icon-only shape in the system).
*Prevents:* an icon button that reads as a button at rest and competes with
the primary action.

**2. "The banner should use the muted fill so it looks tinted."**
→ No: a banner is static, so it sits on `bg-{tone}-surface` with a
`border-{tone}-subtle` hairline; muted is an interactive rung, and a ghost
dismiss button inside the banner would vanish on hover against it. Say why.
*Prevents:* the ghost-on-muted collision the system already hit once.

**3. "Make the primary button red, it's our brand colour."**
→ Decline for the primary action and say why in one line: Energy Red reads
as danger in an interface; the primary tone is `accent`; red is the `danger`
tone for destructive actions. Offer the danger variant if the action is
destructive.
*Prevents:* brand colour used as a call to action.

**4. "Here is our table row's CSS — background muted-default at rest, hover
muted-hover. Are the tiers right?"** — the audit case. Walk the bindings in
the order of sections 1 to 3: is the element interactive at all (a row you can
select is; a row that only displays is not, and belongs on surface); is the
tier the right weight for the intent (a row reads as content until touched, so
ghost, not muted); does the ink follow the tier (`-on-emphasis` only on an
emphasis fill); does each state change only the fill; is disabled inks plus
the emphasis plate rather than a fourth tier. Then count the emphasis fills in
view. Report what to rebind and why, not a new palette.
*Prevents:* approving bindings that are on the ladder but on the wrong tier,
which is how a table of buttons happens.

A fifth, for routing: **"generate a palette from #007079"** and **"does this
text pass contrast?"** are not this skill; they belong to the palette and
contrast skills. This skill chooses rungs on a ladder that already exists.
