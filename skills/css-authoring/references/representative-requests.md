# Representative requests

Acceptance criteria for this skill, per the authoring gate in the repo's
`CLAUDE.md`. A change that breaks any of these is a regression, whatever else
it improves.

**1. "Write the CSS for a button with a primary and a danger variant, and a
hover state."** → Ask which browsers the product ships to (a `browserslist`);
then one root class, the channels declared in the root rule (`--_bg`,
`--_bg-hover`, `--_fg`), every property declared once, `[data-variant='danger']`
overriding the channels, and the hover rule last, assigning `--_bg` from
`--_bg-hover`. The hover is a one-variable diff and works for both variants
without being written twice.
*Prevents:* a `background-color` per variant per state, and a hover rule that
assigns a literal token and flattens the danger variant.

**2. "Review this component CSS before it merges."** — the audit case. Look
for a property declared more than once on the same component; a state rule
that assigns a token rather than a channel; a state rule that sits before a
variant it ties with; modifier classes (`.btn--small`) where `data-*` is the
convention; runtime state mirrored into `data-*`; `#id` or `!important`; a
feature whose support is asserted in a comment rather than checked. Report
each with the rule it breaks and the fix.
*Prevents:* approving CSS that fights itself at the next variant.

**3. "Can I use `:has()` here?"** → Do not answer from memory. Find the
project's matrix (`browserslist`, `.browserslistrc`, build `targets`); fetch
`features-json/css-has.json` and `api.webstatus.dev/v1/features/has`; answer
with the Baseline status and date, the project's floor, and the fallback if
one is needed (`@supports selector(:has(a))`). If the project has no matrix,
say so and propose a `.browserslistrc` rather than substituting a global
percentage.
*Prevents:* a support claim with a shelf life stated as a fact.

**4. "Add a small size to the component."** → `[data-size='small']`
overriding the size channels (`--_font-size`, `--_inset`, `--_gap`), the
default matching the attribute's absence, the geometry properties untouched.
The values themselves come from `typography-scale` and `spacing-ladder`.
*Prevents:* a `.btn--small` block that restates `padding`, `font-size` and
`line-height`, and a default that stops working when the attribute is omitted.

A fifth, for routing: **"what should `--_inset` be for a medium button"** is
`spacing-ladder`, **"which fill does a ghost button get"** is
`colour-fill-tiers`, and **"what line-height goes with 14px"** is
`typography-scale`; this skill shapes the CSS that consumes those values and
never chooses them.
