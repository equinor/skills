# Positions this skill takes

Each is a rule the EDS component emitter enforces on generated CSS, or a
measurement made while writing this skill, rather than a preference.

## 1. Channels over restated properties

Every property a component paints with is declared once, from a `--_` channel;
variants and states override the channel. The alternative — a `background-color`
per variant per state — is what the emitter's harness was built to reject:
with three variants, two sizes and four states the restated form is 24
declarations of one property, and a new state is a new declaration in every
variant. In the channel form a new state is one assignment. The cost is one
indirection to read; the `--_` block at the top of the root rule is the
component's whole API.

## 2. State rules come last; they are not heavier

The first draft of this skill claimed the state selector "always out-specifies
the variant", true under BEM (`.btn--danger` is `(0,1,0)`) and false under
`data-*`, where attributes stack: `.btn[data-variant='danger'][data-size='small']`
is `(0,3,0)`, a tie with `.btn:not(:disabled):hover`, and a third axis wins
outright. Found in review of this skill's own example, corrected 2026-09-08.
The rule the pattern actually depends on is ordering — state rules at the end
of the component's rules or in a later `@layer` — so that is what the skill
states.

## 3. `data-*` for what the author chose; the platform for what the element is

Variants, sizes and boolean options are `data-*` attributes named after their
axis (ADR-0006 rule 3 in `equinor/design-system`, accepted 2026-06-29). Runtime
state — hover, disabled, selected, expanded — is styled from the pseudo-class
or the ARIA attribute the platform already sets, never mirrored into a second
attribute: a mirror is a value that can drift from the truth it copies, and
the headless libraries make the same split (Radix exposes the state the
*component computes* as `data-state`). Semantic descendants are targeted by
element under `>`, so consumer content inside the component cannot collide
with a class the component happens to use.

## 4. Support is verified live, and Baseline governs

Global usage and Baseline measure different things and disagree in the
direction that matters. Fetched 2026-09-08: `:has()` is Baseline widely since
2023-12-19 at 94.07% global usage; CSS nesting widely since 2023-12-11 at
90.66%; `round()` Baseline newly since 2024-05-17 and absent from caniuse
altogether. A rule "95% or nothing" would veto two widely available features
and say nothing about the third. So the skill fetches, reads Baseline first,
treats the percentage as context, and refuses to answer from memory when the
fetch misses — the one instruction in the skill that its own author had to be
held to (the first draft recalled `round()`'s status inside this section).

## 5. The matrix lives in a `browserslist`, not in prose

A support policy written in a README is read by people and goes stale
silently; a `.browserslistrc` is read by the build and can be checked. So the
skill describes the *shape* of the target (evergreen, centrally updated, iOS
Safari, Firefox best-effort) and tells a reader to find or declare their own;
when a project has none, that absence is the finding, and the proposal is a
file, not a sentence.
