---
name: typography-scale
description: 'Defines, ports and reviews algorithmic typographic scales. USE FOR: building a size ramp from one base and ratio, choosing or indexing line-height curves, adding a density axis, porting the Equinor Design System scale, emitting scale tokens or CSS. DO NOT USE FOR: measuring a font or deriving an x-height correction (use typography-x-height-alignment), optical padding and control heights, choosing which typefaces to pair.'
---

# Typographic scale

A scale is an *algorithm*, not a table of numbers. Ship the formula, derive the
values, and let one constant — the base size — carry density. Every value below
is reproducible from two lines of arithmetic; nothing is authored twice.

## 1. Sizes: one base, one ratio, one snap

```
size(i) = round(base × r^(i / n), snap)
```

- `r = 2`, `n` steps per octave. The scale **doubles every n steps** — that is
  the whole point of an octave-based ratio: `lg` → five steps up is exactly
  `2 × lg`, at every density. Exact in the formula; the snap costs 0.5px on a
  few pairs, enumerated in [`references/positions.md`](references/positions.md).
  Arbitrary ratios (1.25, 1.333) have no such landmark, so the ends drift.
- `i` is the step index, offset so that one named step *is* the base. EDS uses
  ten steps `xs … 6xl` with `lg` at the base, so `i = labelIndex − 3`.
- `snap` is a rounding grid, not a formatting choice — see below.

```css
/* five steps per octave, base at lg, snapped to half a pixel */
--font-size-md: round(calc(var(--_base) * pow(2, -1/5)), 0.03125rem);
--font-size-lg: var(--_base);
--font-size-xl: round(calc(var(--_base) * pow(2,  1/5)), 0.03125rem);
```

**Snap to half a pixel (`0.03125rem`), not to whole pixels.** Whole-pixel
rounding is too coarse at the small end, where steps are closest together: it
misses the intended ratio by up to 38.9% against half-pixel's 12.1%, and puts a
+9.09% step next to a +16.67% one in the range that carries body text. Full
figures in [`references/positions.md`](references/positions.md). Half-pixel keeps the
small end proportional while still landing on values a human can say out loud.
Sub-pixel type renders fine; sub-pixel *layout* is what causes trouble, which
is why line-heights snap differently (section 2).

**State the constants somewhere durable.** `base`, `n`, the step offset, and
the snap are the entire scale. Anyone who has those four numbers can regenerate
every token; anyone who has only the tokens has to reverse-engineer them.

## 2. Line-height: a curve indexed by step, snapped to the grid

Large text needs proportionally *less* leading than small text, so a single
ratio is wrong at one end or the other. Use an ease-out cubic across the scale:

```
multiplier(n) = max − (n / (N−1))³ × drop
line-height   = round(fontSize × multiplier(n), 4px)
```

Two curves, because reading and scanning want different things:

| Curve        | max  | drop | For                                        |
| ------------ | ---- | ---- | ------------------------------------------ |
| `default`    | 1.39 | 0.29 | Read text — prose, meant to be consumed     |
| `compressed` | 1.13 | 0.13 | Scanned text — UI labels; a wrapped label must read as one block |

Keep both. Collapsing to one curve plus a literal ratio at the composition layer
looks equivalent and is not — see [`references/positions.md`](references/positions.md).

**The 4px grid is the invariant; the ratio is the derived value.** Snapping the
*result* means the rendered percentages come out non-monotonic —
`152, 133, 143, 150, 130, 133, 131, 129, 113, 108` — which looks like a bug and
is not. Each line box lands on the layout grid, which is the property that
composes; the ratio is just what that costs at that step. Say so in a comment,
because someone will find the table and file an issue.

Name the second curve for what it does, not for how it looks. `compressed`
describes leading; `squished` is Nathan Curtis's term for a *spacing*
proportion (vertical inset one step below horizontal), and reusing it makes two
unrelated ideas collide inside one expression.

## 3. Density is one number

```
compact 0.875   comfortable 1   relaxed 1.15625
```

Density sets `base`. Everything else — sizes, line-heights, and any measure
derived from a font size — follows without a second table. Ship it as an axis
on the root:

```css
[data-density='compact'] { --_base: 0.875rem; }
```

Derive companion measures from the step rather than tabulating them: an icon
gap of `round(fontSize × 0.618, 2px)` stays in proportion at every density,
where a flat `8px` only looks right at one.

**Known trade-off, worth deciding explicitly:** if the line-height curve is
indexed by *step label* (`xs` is always `n=0`), then density shifts the size
ramp underneath a fixed curve, and the same rendered px size gets different
leading depending on which label produced it:

```
16px:  compact/xl = 20px    comfortable/lg = 24px    relaxed/md = 24px
```

Indexing by *absolute size* instead makes leading purely a function of size.
Both are defensible. Label-indexing is the incumbent in EDS and was kept
deliberately — changing it moves rendered values in an existing product, which
is a redesign, not a fix. Decide, record the choice, and move on; do not
discover it by accident later.

## 4. Building a scale for a paired family

When a display or mono face sits beside the text face, the two need one scale
each — they cannot share a size ramp, because equal nominal sizes do not look
equal (see `typography-x-height-alignment`, which produces the correction factor
this section consumes).

**Ask before emitting anything:**

> Will this be used in a CSS-only environment, or also in Figma, React Native,
> or other non-CSS targets?

The answer changes the output, not just the packaging.

### CSS only → one scale, corrected in `@font-face`

Emit a single size ramp and let `size-adjust` correct the secondary face.
It corrects continuously, so it also fixes sizes that are not scale steps.

```css
@font-face {
  font-family: 'Equinor';
  src: url('EquinorVariable-VF.woff2') format('woff2-variations');
  size-adjust: 113.7288%; /* generated from the correction token, not typed */
}

:root {
  --_base: 1rem;
  --font-size-md: round(calc(var(--_base) * pow(2, -1/5)), 0.03125rem); /* 14px */
}
```

Both families now use `--font-size-md` and look the same size. Nothing else
changes.

### Also Figma or React Native → one scale per family

`size-adjust` is a CSS `@font-face` descriptor. React Native never parses it and
Figma has no equivalent, so both would render the uncorrected face while CSS
looked right. Emit **two ramps**:

```
step   text (reference)   display (× 1.137288, snapped)   line-height (shared)
md               14px                          16px                       20px
lg               16px                          18px                       24px
xl             18.5px                          21px                       24px
5xl              32px                        36.5px                       36px
```

Four rules make this work:

- **Correct the font size only.** Apply the factor to each step and re-snap to
  the same grid (`round(step × correction, 0.5px)`), so the corrected ramp lands
  on the same half-pixel grid as the reference.
- **Share the line-heights.** Both families use the reference ramp's
  line-heights at the same step. The whole point of x-height alignment is that
  the faces look the same size at that step — so they get the same line box, and
  the 4px rhythm holds across families. Deriving a second line-height ramp from
  the corrected sizes would undo it.
- **Take `size-adjust` out.** Keep both mechanisms and you double-correct.
- **Check the correction survives the snap.** Below half a snap unit at the
  smallest step it is erased there: `× 1.019345` lands as 0.00% at `xs`/`sm` but
  +3.57% at `md`. Figures in [`references/positions.md`](references/positions.md).

Two numbers under one step label is the correct outcome: `display-md = 16`
beside `text-md = 14` means *the same perceived size*, reached from different
nominal values. A designer and a developer both see 16 for a display step, with
no hidden multiplier anywhere. The cost is that off-scale sizes get no
correction — acceptable, since they are already outside the system, and
lintable.

## 5. Emit the formula where it can run

Keep the algorithm legible in the artefact rather than only in the generator:

```css
--font-size-xl: round(calc(var(--_base) * pow(2, 1/5)), 0.03125rem);
```

A reader can see the scale; changing density changes one variable and the
browser recomputes. Platforms that cannot evaluate expressions — Figma
variables, React Native — get **baked values from the same source**, never
hand-transcribed ones.

`round()` and `pow()` are CSS Values 4 math functions. `round()` is Baseline
*newly*, which is a question about the target, not a verdict — **so ask it
rather than deciding for the reader:**

> Does this need to support older browsers, or only evergreen ones?

- **Evergreen only** — a centrally managed or auto-updating fleet, or a
  `browserslist` that says so. Emit the expressions. This is the whole point:
  the scale stays legible and density recomputes in the browser.
- **Older browsers in scope** — emit baked values everywhere and keep the
  expression in a comment, so the derivation survives even though the browser
  never sees it.

Defaulting to baked values "to be safe" is not neutral. It discards the
readable artefact for a constraint the project may not have, and it does so
silently. If no matrix is declared and nobody answers, say which way you went
and why. Verify current status against
`https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/<slug>.json`
or `https://api.webstatus.dev/v1/features/<id>` rather than recalling it — and
note that caniuse has no feature for `round()`; webstatus calls it
`round-mod-rem`. See the `css-authoring` skill.

## 6. Verification discipline

A scale is a claim that N numbers all follow from four constants. Test it:

- **Every emitted value equals what the engine computes from the expression.**
  Read back computed styles from a real browser, not from the generator that
  produced them — otherwise the test only proves the generator agrees with
  itself.
- **Every deviation from a previous build is enumerated and named.** Anything
  not on the list fails the harness. Silence is never a pass.
- **Extrapolated values are flagged where they live** — in the token, in the
  CSS, in the harness output. A scale that has been extended past its evidence
  should say so at the point of use.
- **No off-scale sizes.** A hard-coded `20px` is outside the system and gets
  none of its guarantees — not the grid, not the paired line-height, and not
  any correction applied to the steps.

## The EDS preset

When asked for a scale "based on the Equinor Design System", these are the
constants. They are the whole specification — everything else derives.

| Constant | Value |
| --- | --- |
| Ratio | `2` (octave) over `5` steps — `2^(1/5)` ≈ 1.1487 |
| Steps | `xs sm md lg xl 2xl 3xl 4xl 5xl 6xl` (ten), `lg` at the base → `i = labelIndex − 3` |
| Size snap | `0.03125rem` (0.5px) |
| Line-height curve, read | `max 1.39`, `drop 0.29` |
| Line-height curve, scanned | `max 1.13`, `drop 0.13` |
| Line-height snap | `4px` |
| Density (base) | `compact 0.875rem`, `comfortable 1rem`, `relaxed 1.15625rem` |

Comfortable, for checking an implementation — `size / line-height (read)`:

```
xs 10.5/16   sm 12/16   md 14/20   lg 16/24   xl 18.5/24
2xl 21/28   3xl 24.5/32   4xl 28/36   5xl 32/36   6xl 37/40
```

Reproduce these exactly before shipping a port. If a value is off by 0.5px the
snap is wrong; if it is off by 4px the curve is being indexed differently
(section 3).

## Positions this skill takes

Four choices here cost something, and a system under delivery pressure will be
tempted to simplify each of them: half-pixel snapping, the second line-height
curve, deriving weight and tracking per step, and keeping ten close steps rather
than six wide ones — this is a scale for an application interface, not a page.
Each is a measurement rather than a preference: the deviation table, the
wrapped-label failure, what Inter's `opsz` axis does and stops doing above 32px,
and the heading ramp you get by sub-selecting rather than widening the ratio.
That file also records two limits where the snapped output does not deliver what
the formula promises: [`references/positions.md`](references/positions.md).

If you simplify any of them, do it knowing the cost and write down why.

## Related

- **`typography-x-height-alignment`** — run it *first* when two families are
  involved: it measures the fonts and produces the correction factor that
  section 4 consumes.
- **`css-authoring`** — verifying browser support before shipping `round()`
  and `pow()`, and the channel-variable pattern for `--_base`.

## Provenance

The formulas and constants above come from the EDS token rework in
**`equinor/ids-meetup-oslo-26`** (Equinor-internal), prepared for the Into
Design Systems Oslo meetup, 9 September 2026:

| Path | What it establishes |
| --- | --- |
| `eds-tokens-reworked/src/formulas.ts` | The algorithms — scale, line-height curves, density |
| `eds-tokens-reworked/DECISIONS.md` | Decision 1 — indexing the line-height curve by step label, and why it was kept |
| `eds-tokens-reworked/build/css/typography.css` | The emitted scale with formulas intact |
| `eds-tokens-reworked/test/deviations.ts` | The enumerated-deviation discipline in section 6 |

Optical padding — cap height, half-leading, and landing a control on the 4px
grid while keeping an honest line-height — derives from these values but is a
spacing concern, and is out of scope here.
