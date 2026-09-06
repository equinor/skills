# Positions this skill takes

Each is a measurement rather than a preference, from the EDS token rework.

## 1. One sequence, density as an offset — not three tables

`1 2 4 6 8 12 16 20 24 28 32 36`, with the rung names landing one place
further along per density. Three hand-maintained tables would have the same
numbers today and drift tomorrow; a sequence with an offset cannot. It also
makes the density story true at every level at once: the ladder, the insets
and the optical paddings all move together because they are all read off the
same rungs. The cost is one extrapolated value at the top (36, the sequence
stepping by 4), flagged in the tokens.

## 2. The seat rung is `xs` raw, not half the container gap

Two candidates for the air around a seated control: the ladder's `xs`, or half
the container gap (grid half-gutter logic). They agree at compact and
comfortable (6, 8) and diverge at relaxed, where half of 20 is 10 — off the
ladder, a minted value — and would have resurrected a 64px-tall bar. The `xs`
rung wins on ladder purity: no new tokens, teachable in one breath, and it
gives 36 / 52 / 68 bars that nobody typed (recorded 2026-09-04). It is
**raw** because the compensation exists for text boxes, whose edges lie, and
control boxes' edges do not.

## 3. Padding is off the 4px grid on purpose

`inset − (lineHeight − cap) / 2` gives 10 for the comfortable `md` button and
6 for the small chip. A reviewer rounds them to 12 and 8, and the button
becomes 40px tall, off the grid it was built to land on. The rule is that the
**height** lands, not the padding, and the recipe puts the padding wherever it
must for that to hold. Because line-height and cap are both snapped to 4, the
paddings always sit on a 2px ladder: a finer grid, not no grid.

## 4. The icon gap is derived from the label, snapped to 2px

`round(fontSize × 0.618, 2px)`: the golden-ratio derivation is the principle,
the snap is the concession. It moved from 0.5px to 2px on 2026-08-28 because
designers reported half-pixel offsets rendering icons blurry, and whole values
compose better; the 32 cells where the two snaps disagree are pinned in the
rework's deviation tests. Comfortable `md` lands on 8px, coincidentally the flat
gap the earlier button used — the derivation reaches the same place and keeps
working at the sizes the flat value did not.
