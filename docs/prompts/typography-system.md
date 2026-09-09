# Set up the typography for a design system

A prompt that spans three skills — `typography-scale`,
`typography-x-height-alignment`, `typography-weight-matching` — and a Figma
target. Written 9 September 2026 for the Into Design Systems talk; the result
it describes is committed in [`demo/typography-tokens/`](../../demo/typography-tokens/).

The designer names the materials and the reference, states what the result
must satisfy, and never names a skill: the agent chooses those from the
acceptance criteria.

## The prompt

```
I'm setting up the typography for our design system. Our text face is Inter
and our display face is Equinor; both are variable fonts on our CDN:

  https://cdn.eds.equinor.com/font/InterVariable.woff2
  https://cdn.eds.equinor.com/font/EquinorVariable-VF.woff2

Inter is the reference. Equinor has to look the same size and weight as
Inter when they sit next to each other, at every size we use.

Build me the full type system and deliver it three ways:

1. Design tokens in DTCG format, one file per density (compact, comfortable,
   relaxed), same token names in each so density is a mode:
   - the type scale, ten steps, and both line-height curves (default for
     reading, compressed for UI) for every step
   - Equinor's size per step, baked as a number, so it imports into Figma —
     and measured at the size it will actually render at, since Inter's
     optical-size axis changes its x-height as it grows
   - three weight tiers, lighter / normal / bolder = Inter 300 / 400 / 500,
     with Equinor's matched weight for every tier and step
   - Equinor's letter-spacing per tier and step, so the gaps between letters
     match Inter's too
   - every token carries how it was derived in $extensions, including the
     CSS calc() expression a stylesheet would use for it
2. CSS custom properties generated from those tokens: the expressions, with
   comfortable as the root and the other densities as a data attribute, plus
   a baked version with literals.
3. Figma: push the tokens into this file as variables (one collection, the
   three densities as modes) and bind text styles to them for every step and
   tier, Inter and Equinor. Then add a preview page that shows the ladder —
   each step in both faces, all three tiers, at each density — so I can see
   the pairing on one canvas:

   <your Figma file URL>

Rules: measure everything from the font files, don't type numbers from a
spec page or from memory. If a value can't be matched (a weight Equinor's
axis doesn't reach, a browser feature you can't verify), say so in the output
rather than pick something close. Record the commands you ran so the result
can be rebuilt when the fonts change.
```

## What a correct result looks like

Acceptance criteria, in the shape the skills' own representative requests use.
A run that misses one of these has not answered the prompt.

- **Three token files, same paths.** `typography.compact|comfortable|relaxed.tokens.json`;
  every path present in all three, so a Figma importer reads them as modes.
- **The scale is derived, not typed.** `font-size.<step>` is
  `round(base × 2^(i/5), 0.03125rem)` with the base per density; both
  line-height curves per step, snapped to 4px. Comfortable `md` is 14px on a
  20px default and 16px compressed line box.
- **Equinor's size is per step and baked.** `x-height-correction.display.<step>`
  is Inter's x-height *at that step's optical size* over Equinor's: 1.137288
  at 14px, 1.074219 at 32px and above, with `drift` on the group. The flat
  factor would set a 32px heading 5.9% too large; a run that emits one factor
  for every step has not measured the axis.
- **Weights are matched by stem, per tier and step, and rise with size at the
  bolder tier.** Inter 300 / 400 / 500 → Equinor about 376 / 458 / 553 at the
  text steps; 563.1 at 32px for the bolder tier. Inter 700 is not a tier,
  because no Equinor weight reaches its stem, and the run says so if asked.
- **Letter-spacing is a compensation, in Equinor's em.** Within a tenth of a
  pixel of zero at the text steps, about −0.014em at 32px, the same for the
  normal and bolder tiers. Figma receives it in px at the step's display size,
  because a bound letter-spacing variable is applied in pixels only.
- **Every token explains itself.** `derived` with expression and inputs,
  `metrics` with the axis location it was measured at, `css` with the
  expression, both fonts' checksums in the file.
- **The CSS is read back from the tokens**, not computed a second time:
  expressions in `:root` for comfortable and under `[data-density]` for the
  others, and a baked twin with literals.
- **Figma has one collection with three modes**, text styles bound to the
  variables for every step and tier in both faces, and a preview page with
  the ladder. The Equinor font is used from the CDN and never committed.
- **The commands are recorded**, so the whole thing can be rebuilt when either
  font changes.

## Related prompts

Each skill's own prompts are its
[`references/representative-requests.md`](../../skills/typography-scale/references/representative-requests.md);
this folder is for requests that need several skills at once.
