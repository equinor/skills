# Typography tokens — intent

Built 9 September 2026, the morning of the Into Design Systems talk, from
Victor's request: the EDS type scale with both line-height curves, Inter and
Equinor, Equinor's size, weight and letter-spacing matched to Inter, lighter
and bolder variants of every step, three densities, baked so it imports into
Figma, in DTCG format with the CSS `calc()` expressions carried in
`$extensions`, plus CSS. Three token files, one per density, and two
stylesheets read back from them:

```
typography.compact.tokens.json
typography.comfortable.tokens.json
typography.relaxed.tokens.json
typography.css          expressions: comfortable in :root, the others under [data-density]
typography.baked.css    the same custom properties as literals, for a matrix without CSS round()
```

Same token paths in each file, so density is a Figma mode and nothing else
moves. The stylesheets are generated *from* the token files, not alongside
them: `build.py` writes the JSON, reads it back, and emits each custom
property from the token's `$value` or its `$extensions…css` expression, so the
CSS cannot disagree with the tokens.

## The request, as a designer would put it

Written 9 September after the first build, as the representative request this
folder answers; the agent chooses the skills from the acceptance criteria and
the designer never names one.

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

   https://www.figma.com/design/I7325LB6YGBMn6lakfaWFA/EDS-IDS-typography-ladder?node-id=0-1

Rules: measure everything from the font files, don't type numbers from a
spec page or from memory. If a value can't be matched (a weight Equinor's
axis doesn't reach, a browser feature you can't verify), say so in the output
rather than pick something close. Record the commands you ran so the result
can be rebuilt when the fonts change.
```

Three things make it work: it names the materials and the reference, so the
skills' first questions are already answered; it states acceptance criteria
rather than a method; and its closing rules are the skills' own discipline in
plain words — measure rather than recall, refuse rather than approximate,
record the commands.

## What is in each file

| group | per | from |
| --- | --- | --- |
| `font-size.<step>` | 10 steps | `typography-scale`: `round(base × 2^(i/5), 0.03125rem)` |
| `line-height.<step>.default` / `.compressed` | 10 × 2 | `typography-scale`: the two curves, snapped to 4px |
| `x-height-correction.display.<step>` | 10 | `typography-x-height-alignment`: Inter's x-height at the step's `opsz` over Equinor's; `drift` on the group |
| `font-size-display.<step>` | 10 | the text size × that step's correction, re-snapped: Equinor's baked size |
| `font-weight.Inter.<tier>` | lighter 300 · normal 400 · bolder 500 | the chosen tiers on the reference |
| `font-weight.Equinor.<tier>.<step>` | 3 × 10 | `typography-weight-matching`: the weight whose stem matches Inter's at that tier, `opsz` and correction |
| `letter-spacing.Equinor.<tier>.<step>` | 3 × 10 | `typography-weight-matching` §4: Inter's side space at the `opsz` over the correction, minus Equinor's at the matched weight, in Equinor's em |

Every token's `$extensions.com.equinor.typography` carries `derived`
(expression and inputs, aliases where another token is the input), `metrics`
with the axis location it was measured at, and `css`, the expression a
stylesheet would use — `round(calc(var(--_base) * pow(2, 1/5)), 0.03125rem)`,
`round(calc(var(--font-size-5xl) * 1.074219), 0.03125rem)`,
`letter-spacing: -0.014223em;`. `$extensions.com.equinor.figma` names the
collection, the mode and the variable scopes; letter-spacing carries its
percent there, since Figma has no em. The file's own `$extensions` records
both fonts' checksums, the build date and the builder.

## Decisions

- **Baked, and per step.** Figma and React Native cannot evaluate an
  expression, so `font-size-display` carries the number. And the number is per
  step, not one factor: Inter's x-height falls with its `opsz` axis (0.545898
  at opsz 14, 0.515625 at opsz 32), so a 32px Equinor heading takes
  × 1.074219 and a 14px label × 1.137288; the flat factor would set the
  heading 5.9% too large. `x-height-correction.display` is the per-step group
  from the x-height skill's outcome 2, with `drift` recorded (`max` 0.0587).
- **Density changes the optical size, so it changes the corrections.** The
  same step is a different px in each density, hence a different `opsz` and a
  different correction, weight and letter-spacing. Comfortable `md` (14px) and
  compact `lg` (14px) get identical Equinor values; comfortable `2xl` (21px)
  gets × 1.112875 where relaxed `2xl` (24.5px) gets × 1.100667.
- **Tiers are Inter's, chosen; Equinor's are matched.** Lighter 300, normal
  400, bolder 500 on Inter — 500 because it is the bolder tier the EDS token
  rework settled on (Victor, 9 September; the first build used 600), and 700
  is not a tier because Inter 700 has a stem no weight on Equinor's 300–700
  axis reaches. Equinor's matched weights rise with size at the bolder tier
  (552.7 at `xs` to 563.1 at 32px and above) and hold near 458.5 at the
  normal tier, where the thinner stem and the smaller size cancel.
- **Letter-spacing is a compensation for the missing axis, in Equinor's em.**
  Nothing at the text steps (+0.0038em at 14px, bolder), −0.0141em at 32px
  and above; the value is the axis's, not the weight's. Inter carries no
  letter-spacing token: it is the reference. A design system's own tracking
  ramp adds on top.
- **Nothing here is typed.** `build.py` imports the three skills' scripts as
  libraries and runs the per-step derivations the CLIs take one value at a
  time; the token files are its output, committed with their inputs. Rebuild:

  ```bash
  <venv>/bin/python demo/typography-tokens/build.py --equinor <EquinorVariable-VF.woff2>
  ```

  Equinor comes from `cdn.eds.equinor.com/font/EquinorVariable-VF.woff2` and
  is never committed; its licence permits use, not redistribution. Inter is
  the copy bundled with `typography-weight-matching` (checksum in the file).
  A full build instances the fonts a few hundred times and takes about three
  minutes, and writes the two stylesheets last.
- **CSS ships the expressions by default.** `typography.css` carries
  `round(calc(var(--_base) * pow(2, 1/5)), 0.03125rem)` and its kin, so a
  change of `--_base` re-derives the ramp in the browser; the per-step display
  factors, weights and letter-spacing are literals per density block because
  they were measured, not computed. `typography.baked.css` is the same set as
  literals, for a browser matrix without `round()` — a question for the
  project's `browserslist`, as the scale skill says.

## Importing into Figma

The files are standard DTCG, so a token importer (Tokens Studio, or Figma's
own variables import) reads them with one mode per file. `typography-scale`'s
`--format figma` scripts create the `font-size` and `line-height` variables
and the text styles through the Figma MCP; the weights and letter-spacing are
not yet covered by a script and go in through the importer. Bind text styles
to `font-size-display` for Equinor and `font-size` for Inter; both share the
step's `line-height`.

## Not done

- A `--target-opsz` for `stem.py` and a per-step `--correction` for `scale.py`
  would let the skills emit these files directly; `build.py` is the seam
  until then (recorded in `demo/typography/INTENT.md` §8 and the meetup
  repo's issue #48).
- `xheight.py` ran its command-line code on import and could not be used as
  a library; its entry point is guarded in the same change as this folder.
- Inter's own `letter-spacing` ramp for headings, if EDS wants one, is a
  design choice this build does not make; the port factor in
  `typography-weight-matching` §5 is how it would travel to Equinor.
