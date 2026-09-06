---
name: colour-fill-tiers
description: 'Chooses the right fill rung for an interface element in the Equinor Design System colour ladder — emphasis, muted or ghost for things you can press, canvas or surface for things you cannot — and the state steps within a tier. USE FOR: which background a button, chip, row, tab or icon button gets at rest, hover, active and selected; whether an area is interactive or static; why a banner sits on surface and not on muted; the Energy Red rule. DO NOT USE FOR: generating a palette or its lightness ladder (a colour-palette skill), checking contrast (a colour-contrast skill), text or icon ink colours beyond the on-emphasis rule, or dark-mode generation.'
---

# Fill tiers: which rung, and why

The EDS colour ladder gives every family — accent, neutral, info, success,
warning, danger — fifteen steps in stacking order: canvas, surface, three
muted fills, three borders, three emphasis fills, two texts, two texts on
emphasis. This skill answers one question about it: **when an element needs a
background, which rung is it?** The answer turns on a single test.

> **The fill rungs are for things you can press.** Static areas sit on the
> canvas and surface tiers.

This skill **emits no values**: the colours come from the palette; this is the
rule for binding them.

## 1. Is it interactive?

**Ask before emitting anything:**

> Can the user press this — is it a control — or is it an area that holds
> content?

The answer decides the tier family, not a shade within it. A button, a chip, a
menu row, a tab, an icon button, a switch: interactive, so a **fill** tier. A banner strip, a card, a
table body, a dialog body, a page region: static, so **canvas** (the page's
floor) or **surface** (a tinted or raised area on it). This is the test that
resolves the one collision the system had: a tinted static strip that looked
like a muted fill made the ghost button sitting on it disappear, because both
landed on the same step. The strip moved to `surface` and the whole
interactive ladder read correctly above it by construction. A tone variant of
a static area is `bg-{tone}-surface`, with a `border-{tone}-subtle` hairline
where dark mode needs the separation.

## 2. Which fill tier

Three tiers, one per weight of call to action:

| tier | at rest | ink | for |
| --- | --- | --- | --- |
| **emphasis** | filled, steps 9 / 10 / 11 | `text-*-on-emphasis`, `icon-*-on-emphasis` | the primary action; used sparingly — one per view is the norm |
| **muted** | tinted wash, steps 3 / 4 / 5, tone border | `text-*-strong` | a quiet opaque fill: secondary chips, filled selection controls |
| **ghost** | transparent | `text-*-strong`, `icon-*` | the default for icon buttons, menu rows, tabs, table rows — anything that should read as content until touched |

Each tier is a **ladder of states**: `default`, `hover`, `active`, and
`selected` where the component has a selected state. Ghost's ladder starts at
transparent and gains a step on hover (step 3) and active (step 4), which is
what makes a row feel pressable without looking like a button at rest.
`selected` is the tier's step 4 (ghost) or step 5 / 11 (muted / emphasis):
the accent ghost-selected rung is what a selected tab or menu item wears.

Token shape, per family and tier: `bg-{tone}-fill-{emphasis|muted|ghost}-{default|hover|active|selected}`,
with the neutral family also unprefixed as `bg-fill-*`. Ink follows the tier:
on an emphasis fill, `text-{tone}-strong-on-emphasis` and
`icon-{tone}-on-emphasis`; on muted and ghost, the ordinary strong text and
icon inks. Never pick a text colour by eye against a fill; the pair is
predetermined by the tier.

## 3. Disabled, and what a state may change

Disabled is not a fourth tier. It is a set of inks and, for the emphasis tier
only, a grey plate: `bg-fill-emphasis-disabled` with `text-disabled` and
`icon-disabled`. Muted keeps its structure with `border-disabled`; ghost stays
transparent with disabled inks. States state what changes and nothing else — a
hover that also changes the border, or a disabled that changes the size, is a
second component wearing the first one's name.

## 4. Energy Red

Energy Red is the Equinor brand's signature colour, and in branding it reads
as *energetic*. In an application interface a saturated red on an interactive
element reads as *danger* — destructive, stop, something is wrong. The same
pigment carries opposite messages in the two media, so **Energy Red is never
the primary action.** The primary tone is `accent`; red exists in the system
only as the `danger` tone, an explicit opt-in for destructive actions where
"danger" is exactly the message. That is a refusal, not a loss: the brand fact
is recorded, and deliberately not carried into this context.

## 5. Check the result

- **Read the page with the fills hidden.** Everything that still needs a
  background to make sense was static, and belongs on canvas or surface.
- **Count the emphasis fills in view.** More than one is a hierarchy problem,
  not a colour problem.
- **Press everything that looks pressable.** A ghost element must gain a step
  on hover; a static area must not.
- **Contrast is measured, not assumed.** The pairs above are the ones the
  palette guarantees; anything off the tier — a custom fill, an ink from
  another family — is outside the guarantee and needs checking with a
  contrast tool.

## Representative requests

Three acceptance criteria — a component's background at rest and in states,
the static-versus-interactive call for a strip, the red primary button — plus
a routing check: [`references/representative-requests.md`](references/representative-requests.md).

## Positions this skill takes

Three, each with the collision or the confusion observed when it was not held:
static areas never take fill rungs, ghost is the default interactive tier,
and Energy Red is refused for primary actions:
[`references/positions.md`](references/positions.md).

## Related

- **`colour-palette`** (planned) — generates the fifteen-step ladder these
  rungs are chosen from.
- **`colour-contrast`** (planned) — measures the pairs; this skill only binds
  them.
- **`spacing-ladder`** — the other half of a control's recipe: the fill says
  what it looks like, the inset says how big it is.

## Provenance

The tier semantics, the ghost ladder and the static-equals-surface rule come
from the EDS token rework in `equinor/ids-meetup-oslo-26` (Equinor-internal;
`eds-tokens-reworked/DECISIONS.md`, the banner and fill-tier entries, and
`DESIGN.md`'s colour table), and the Energy Red rule from its
`eds-cli/principles/brand.md`. The ladder itself is the public EDS palette
generator in `equinor/design-system`.
