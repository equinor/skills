# Equinor Skills
 
A growing collection of Agent Skills covering design systems, colour, spacing and typography.
 
Skills land here as they are written; the first seven were introduced at the [Into Design Systems](https://luma.com/ids-oslo) meetup, Oslo, on 9 September 2026, with more added over time.
 
## What's here
 
Skills are built to the open [Agent Skills](https://agentskills.io) standard, so they work across Claude Code, Copilot, Cursor, Codex, and other compatible agents – not just one tool.
 
Available now:

- **[typography-scale](skills/typography-scale)** – algorithmic type scales: sizes from one base and one ratio, line-height as a curve rather than a fixed multiple, density as a single number
- **[typography-x-height-alignment](skills/typography-x-height-alignment)** – align two paired fonts by measured x-height, and deliver the correction as a design token
- **[typography-weight-matching](skills/typography-weight-matching)** – match weight and letter-spacing across a font pair, and compensate for a face with no optical-size axis
- **[spacing-ladder](skills/spacing-ladder)** – one spacing sequence read by relationship, inset proportions, and optical padding that lets a control's height emerge instead of being typed
- **[colour-fill-tiers](skills/colour-fill-tiers)** – which fill rung an element gets: emphasis, muted or ghost for things you can press, canvas or surface for things you cannot
- **[design-system-adr](skills/design-system-adr)** – write, check, supersede and index Architecture Decision Records in the EDS team's MADR-based format
- **[css-authoring](skills/css-authoring)** – hand-authored component CSS the EDS way: channel variables, `data-*` variants, modern selectors, browser support verified rather than recalled

Planned areas:

- **Typography** – optical padding, algorithmic tracking for prose
- **Colour** – OKLCH palette generation, contrast (APCA), semantic roles
- **Spacing** – the baseline grid for running text
- **Design systems** – broader EDS-informed practices beyond the ADR skill

## Demo

The demo pages are published at **<https://equinor.github.io/skills/>**, from
the `www` branch that `scripts/publish-www.sh` rebuilds after every change
under `demo/`. The state shown at the meetup is tagged `v0.1.0`.

[`demo/typography/`](demo/typography/) is the page shown at the meetup: an
article set in Inter and Equinor, seven controls labelled with the request you
would type to an agent, and a panel showing the CSS each request produces.
Open `index.html` over HTTP (the fonts load from the EDS CDN), or append
`?on=guides,scale,baseline,swap,xheight,weight,tracking` to arrive with everything on.
`INTENT.md` alongside records why it is built the way it is.

[`demo/typography-scale/`](demo/typography-scale/) is its companion explorer:
one step at a time through the size formula, both line-height curves, the
three densities and the 4px snap.

[`demo/typography-overlay/`](demo/typography-overlay/) overlays one sentence in
two faces on a shared baseline, with sliders that snap to the skills' x-height
and weight numbers.

[`demo/typography-tokens/`](demo/typography-tokens/) is the output of all three
typography skills together: one DTCG file per density with the scale, both
line-height curves, and Equinor's size, weight and letter-spacing matched to
Inter per step, baked for Figma, with the CSS expressions in `$extensions`.

## Browser support

The CSS in these skills targets modern, evergreen browsers. Features are
recommended on the basis that they are Baseline available — not that they are
universally supported — because the products these skills came from run on
centrally managed browsers that update continuously.

If you need to support older browsers, that is your project's call to make.
Every skill that recommends a CSS feature also tells you how to check it against
your own browser matrix first.

## Installing a skill
 
Install a single skill with:
 
```bash
npx skills add equinor/skills --skill typography-scale
```
 
## Try it

A prompt a designer would type to get a whole type system — the scale with both
line-height curves, Equinor sized, weighted and letter-spaced to match Inter
per step, three densities, as DTCG tokens, CSS and Figma variables — is in
[`docs/prompts/typography-system.md`](docs/prompts/typography-system.md), with
the acceptance criteria a correct result meets. The result it produced is
[`demo/typography-tokens/`](demo/typography-tokens/). Prompts that need several
skills at once collect in [`docs/prompts/`](docs/prompts/); each skill's own
requests are in its `references/representative-requests.md`.

## Third-party assets

Some skills bundle files they need in order to run — currently the Inter and
EB Garamond typefaces used by `typography-x-height-alignment` to demonstrate
itself without arguments.

**Bundled assets keep their own licences and are not covered by this
repository's MIT licence.** Both fonts are SIL OFL 1.1; their licence texts and
authorship sit alongside them in
[`skills/typography-x-height-alignment/assets/fonts/`](skills/typography-x-height-alignment/assets/fonts/).

## Status

First release, announced at Into Design Systems Oslo on 9 September 2026. Seven
skills, installable with the command above; three demo pages under
[`demo/`](demo/), each with an `INTENT.md` that records why it is built the way
it is. Skills are versioned by the git history for now — expect the wording to
keep improving, and the emitted numbers to change only when the fonts do or a
measurement is corrected, with the change recorded in the skill's references.
