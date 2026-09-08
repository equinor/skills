---
name: spacing-ladder
description: 'Applies the Equinor Design System spacing ladder: one sequence of rungs, the relationship each rung expresses (page, container, cluster, selectable, seat), inset proportions for controls (squished, squared, stretched), optical padding that makes a control''s height emerge from its label, the seat an icon takes in the label''s cap cell, and the icon gap. USE FOR: choosing a gap or padding, sizing a button, chip, input, tab or toolbar without authoring its height, placing or sizing an icon inside a control, porting the ladder to another density, emitting spacing tokens or CSS. DO NOT USE FOR: the type scale or line-heights (typography-scale), aligning running text to the baseline grid (a spacing-baseline-grid skill), colours of the controls (colour-fill-tiers).'
---

# The spacing ladder

EDS spacing is one ladder, and the rule for reading it is a single idea: **the
closer the relationship, the smaller the space.** A page holds sections — 24. A
container holds children — 16. A cluster holds siblings — 12. A selectable
holds its own label — the inset. And the closest relationship in the whole
system, a control and the bar it sits in — 8. Every step down the ladder, one
step closer.

The taxonomy has five levels: **page → container → cluster → selectable →
seat**. The page / container / selectable trichotomy is Eric Singhartinger's —
a selectable is the atom, the thing you can press: a button, a chip, a tab.
Cluster and seat are EDS's additions, between and below.

The second idea follows from the first: **a control's height is never
authored.** It is the label's cap height plus an inset above and below, and the
vertical padding is whatever makes that true. An agent with this skill produces
a 36px-tall comfortable button without ever typing 36.

## 1. One sequence, three densities

```
1  2  4  6  8  12  16  20  24  28  32  36
```

The rung names — `4xs 3xs 2xs xs sm md lg xl 2xl 3xl` — land on this sequence
at an offset set by density: compact starts at 1, comfortable at 2, relaxed at
4. So `md` is 12 / 16 / 20 across densities, `xs` is 6 / 8 / 12, and every rung
scales with density automatically; no rule changes. The top value, 36, is an
extrapolation (the sequence steps by 4 from 20 up) and is flagged as such in
the tokens.

```bash
skill=.claude/skills/spacing-ladder                # where the installed copy lives
python3 $skill/scripts/spacing.py table --density all
```

## 2. Relationships: which rung

| relationship               | rung  | compact / comfortable / relaxed |
| -------------------------- | ----- | ------------------------------- |
| page → sections            | xl    | 20 / 24 / 28                    |
| container → children       | md    | 12 / 16 / 20 (containers also gap `md`) |
| cluster → siblings         | sm    | 8 / 12 / 16                     |
| selectable → its label     | inset | per component, optically corrected (section 4) |
| strip → seated control     | xs    | 6 / 8 / 12, **raw**             |

**Cluster.** Selectables acting as one group — Save/Cancel, a top bar's action
row — are a cluster, and their internal gap sits one rung below their
container's gap. Grouping must read tighter than separation, or it does not
read at all; and boxes that bring their own inset need less air added — two
buttons at gap 16 have roughly 48px between their *labels*, because each
carries its own horizontal padding. The gap measures box to box; the eye
measures ink to ink.

**Selectable.** The atom of the taxonomy — anything you can press. A
selectable's spacing relationship is its **inset**, box edge to label, and it
is the one place optical compensation applies: the padding subtracts the
label's half-leading so the height lands on `inset × 2 + cap` (section 4). Its
heights are the selectable ladder, `sizing/selectable-*` — 20 / 24 / 36 / 44 /
52 / 60 at comfortable for `xs` to `2xl`, each what the recipe in section 4
produces for that size — a target-size floor, never a menu to pick a height
from.

**Seat.** A chrome strip that seats controls — a top bar, a toolbar — pads its
cross axis with the seat rung, and pads it **raw**: no optical compensation.
Text boxes lie about their edges; control boxes don't. Text carries invisible
air above and below its letters, the half-leading, so we subtract that lie
from padding to make text look right. A button or a field is a box whose edges
are real — nothing to subtract. Text gets corrected padding; controls get
honest padding. The consequence: a strip's height is never authored either. It
is the tallest seated control plus a seat of air above and below — 36 / 52 / 68
across densities, and nobody typed any of them.

## 3. Inset proportions: a control's padding, by name

A control's padding is an **inset** from the ladder, named by its horizontal
rung and a proportion for the vertical one:

| proportion   | vertical rung        | comfortable `md` | for                          |
| ------------ | -------------------- | ---------------- | ---------------------------- |
| `squished`   | one below horizontal | 16 / 12          | button                       |
| `squared`    | the same             | 16 / 16          | tab, tooltip                 |
| `stretched`  | one above            | 16 / 20          | input                        |

Sizes `xs`–`xl`. The proportion words are Nathan Curtis's, from *Space in
Design Systems*; the "one rung" reading of them is EDS's. Because they are
rungs, density moves them together with everything else.

## 4. Optical padding: the height emerges

**Ask before emitting anything:**

> Will this run in CSS only, or also in Figma or React Native?
> And does it need to support older browsers, or only evergreen ones?

CSS gets the expression and recomputes at every density; Figma and React
Native get the resolved value per density from the same source, never a typed
number. The expressions use CSS `round()`, Baseline *newly* since 2024-05-17
(checked 2026-09-06 at `https://api.webstatus.dev/v1/features/round-mod-rem`);
where an older matrix is in scope, `spacing.py css --css baked` writes every
optical value as a literal per density with the expression in a comment. Both
answers change the artefact, not its packaging, and the default is the
expression: this is a question for the project's `browserslist`, not a hedge.

The vertical inset is what the eye should see between the control's edge and
the label's cap height. But a text box is taller than its letters: its line
box carries half-leading above and below the cap. So the padding that
*renders* as the inset is the inset with that half-leading taken off:

```
cap        = round(fontSize × capRatio, 4px)            capRatio: Inter 0.727539
halfLead   = (lineHeight − cap) / 2                      lineHeight: the compressed curve
paddingV   = inset − halfLead
height     = inset × 2 + cap                             — whatever the line-height is
```

The line-height cancels out of the height, which is why a wrapped label does
not break the control: it adapts. Comfortable `md` squished with an `md` label
(14px on a 16px compressed line box, cap 10.19 → 12):

```
paddingV = 12 − (16 − 12) / 2 = 10px          height = 12 × 2 + 12 = 36px
```

```bash
python3 $skill/scripts/spacing.py control --size md --proportion squished --label md
```

**Padding values are deliberately off the 4px grid. Never round them to a
multiple of 4.** `10px` looks wrong and is correct; rounding it to 12 pushes
the control to 40px, off the grid it was supposed to land on. The values
always sit on a 2px ladder, because line-height and cap are both snapped to 4.
Across densities the same recipe gives 24 / 36 / 44 for the button, 24 for the
small chip, 20 / 24 / 36 for the tooltip; every one of them emerges.

Icon-only controls carry no half-leading, so the correction drops out, and
the horizontal inset collapses to the vertical one: padding equals the raw
inset on all sides and the control is a square with the labelled control's
height — `spacing.py control --size md --icon-only` gives 36 × 36 at
comfortable — so the round icon button is a circle by construction, with no
pixel to fudge. The glyph inside it takes the seat described next, read from
the step the control *would* have labelled:
`control --size md --icon-only --label md --icon md`.

## 5. The glyph seat: an icon sits in the label's cap cell

An icon beside a label is a glyph, and it is laid out like one. Its layout
**footprint is the label's cap cell** — the cap-rounded height from the recipe
above, 12px for a comfortable `md` label — never the icon's own box. The ink
overflows that footprint the way ascenders and descenders overflow the cap,
by the same amount on every side:

```
glyph   = sizing-icon step, the ink size                     md: 18 / 20 / 24 across densities
margin  = (cap − glyph) / 2                                  comfortable md: (12 − 20) / 2 = −4px
```

The margin is negative by construction. Because the margin box is then exactly
the cap, the control's `align-items: center` puts the glyph's centre where the
label's cap centre sits, which is the control's centre: nothing to nudge. (The
cap is centred in Inter's line box to within half a pixel; measure it for
another label face.) The icon sizes are a second sequence read with the same
density offset as the ladder (`14 16 18 20 24 28 32 37 42 48 56 64`), so a
glyph steps with its density like everything else.

The seat is on every side, so the same overhang applies on the inline axis:
**the icon gap and the leading inset are measured to the cap cell, not to the
ink.** At comfortable `md` the 8px gap and the 16px inset leave 4px and 12px
of visible space beside the glyph, and that is the intended optical result —
a round glyph wants to overhang, as the label's own side bearings do. Measure
the gap between the cap cell and the label; a measurement to the ink that
comes up short is the seat working, not a gap to widen.

**The glyph is one element.** The `<svg class="icon">` is its own cell: it
carries the size and the margin itself, and the flex or inline layout of the
control does the centring. Everything a wrapper would do, the margin already
does; a wrapper belongs to Figma, where it is mask-and-tint machinery, and has
no counterpart in CSS. There, the wrapper *is* the cap cell: a frame
`cap-rounded-<step>` square with the `sizing-icon` glyph centred in it. React
Native takes the margin recipe unchanged, negative margins included.

```css
.button .icon {
  inline-size: var(--sizing-icon-md);
  block-size: var(--sizing-icon-md);
  margin: var(--glyph-margin-md);   /* (cap-rounded-md − sizing-icon-md) / 2 */
}
```

The emitted `--glyph-margin-<step>` pairs a label step with the icon step of
the same name, for every step that has an icon size, `xs` to `6xl`. A mixed
pairing takes its seat from `spacing.py glyph` and writes the `calc()` out
with both steps named.

```bash
python3 $skill/scripts/spacing.py glyph --label md --icon md
python3 $skill/scripts/spacing.py control --size md --proportion squished --label md --icon md
```

The component chooses the icon step for its label — the `md` button pairs `md`
with `md`, the small button pairs an `sm` label with an `xs` glyph (cap 8,
glyph 16, margin −4, where `--glyph-margin-sm` would give −5) — and the recipe
gives the seat for any pairing.

## 6. Inside an atom: the icon gap

One rung lives below all of these, inside components themselves: the gap
between a glyph and its label. It is derived from the label, not from the
ladder — `round(fontSize × 0.618, 2px)`, 8px at comfortable `md` — and it
belongs to the atom's anatomy, not to layout. It separates the glyph's cap cell
from the label, so with the seat of section 5 the visible ink-to-text distance
is `gap + margin`, 4px at comfortable `md`; do not add the margin back. Never
use icon-gap tokens between siblings, and never use the ladder rungs inside an
atom. The
`icon-gap` tokens this skill emits are the ones `typography-scale` mentions
in passing; this is where they are defined.

## 7. Emit: tokens first, then CSS

```bash
python3 $skill/scripts/spacing.py tokens --out tokens    # one DTCG file per density
python3 $skill/scripts/spacing.py css                     # expressions (or --css baked)
python3 $skill/scripts/spacing.py glyph --label md --icon md  # an icon's seat, per density
python3 $skill/scripts/spacing.py check                   # the fixtures still hold
python3 $skill/scripts/spacing.py --cap-ratio 0.70 tokens --out tokens   # another label face
```

The ladder, the insets as aliases of ladder rungs, the optical paddings with
their derivation — the inset, the label's size and line-height, the cap ratio
— and the height they produce, the icon gaps, and the icon sizes:
[`references/token-shape.md`](references/token-shape.md). The emitted
paddings assume the label step equals the inset size; another pairing comes
from `control --size … --label …`. The cap ratio is the label face's and is a
global option, so a different face re-derives every padding in one run. Figma
gets the resolved padding per density mode as `spacing/optical-padding/<size>-<proportion>`
and the control's `min-height` bound to `inset × 2 + cap`; it cannot evaluate
the expression, so the tokens carry the number and the derivation both.

## 8. Verify

- **Read heights back, never author them.** A control whose height is a literal
  has lost the recipe; the next density breaks it.
- **Check the gaps against the relationships**, not against each other: a gap
  of 16 between two buttons in a cluster is the container's rung on the wrong
  relationship, and reads too far apart even though it is on the ladder.
- **Re-derive on font changes.** The cap ratio is the label face's; a different
  face, or a corrected display size, moves every padding and every glyph seat.
- **Measure the glyph's centre against the label's cap centre.** Read both back
  from the rendered control; they coincide when the icon is one element with
  the cap-cell margin, and the difference is the finding when they do not.

## Representative requests

Six acceptance criteria — the button that emerges at 36, the cluster gap, the
seated strip, the density port, auditing spacing already committed, and the
button's leading icon — plus a routing check:
[`references/representative-requests.md`](references/representative-requests.md).

## Positions this skill takes

Five, each with the measurement behind it: one sequence rather than per-density
tables, the seat rung raw rather than half the container gap, padding off the
4px grid on purpose, the icon gap derived from the label, and the glyph as one
element in the label's cap cell:
[`references/positions.md`](references/positions.md).

## Related

- **`typography-scale`** — the sizes and the compressed line-height curve the
  recipe consumes.
- **`typography-x-height-alignment`** — a corrected display face is set larger,
  so its cap and padding move with it.
- **`colour-fill-tiers`** — the other half of a control: the inset says how
  big, the fill says what it looks like.

## Provenance

The ladder text and the cluster and seat rungs are from the EDS token rework in
`equinor/ids-meetup-oslo-26` (Equinor-internal): `eds-cli/principles/spacing.md`,
`eds-tokens-reworked/DECISIONS.md` ("Two spacing rungs", 2026-09-04; "Gap snap",
2026-08-28; the optical-padding recipe) and its internal optical-padding skill,
generated from the tokens' `$extensions`. The glyph seat is the `.icon` rule
in `eds-contracts/build/*.css` and the one-element glyph rule in its
`AGENTS.md`; the icon sizes are `sizing-icon-*` in
`eds-tokens-reworked/build/css/typography.css`.
