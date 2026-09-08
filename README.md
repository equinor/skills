# Equinor Skills
 
A growing collection of Agent Skills covering design systems, colour, spacing and typography.
 
This repository is just getting started. Skills land here as they are written, ahead of being introduced at the [Into Design Systems](https://luma.com/ids-oslo) meetup, Oslo, on 9 September 2026, with more added over time.
 
## What's here
 
Skills are built to the open [Agent Skills](https://agentskills.io) standard, so they work across Claude Code, Copilot, Cursor, Codex, and other compatible agents – not just one tool.
 
Available now:

- **[typography-scale](skills/typography-scale)** – algorithmic type scales: sizes from one base and one ratio, line-height as a curve rather than a fixed multiple, density as a single number
- **[typography-x-height-alignment](skills/typography-x-height-alignment)** – align two paired fonts by measured x-height, and deliver the correction as a design token
- **[typography-weight-matching](skills/typography-weight-matching)** – match weight and letter-spacing across a font pair, and compensate for a face with no optical-size axis
- **[spacing-ladder](skills/spacing-ladder)** – one spacing sequence read by relationship, inset proportions, and optical padding that lets a control's height emerge instead of being typed
- **[colour-fill-tiers](skills/colour-fill-tiers)** – which fill rung an element gets: emphasis, muted or ghost for things you can press, canvas or surface for things you cannot

Planned areas:

- **Typography** – optical padding, algorithmic tracking for prose
- **Colour** – OKLCH palette generation, contrast (APCA), semantic roles
- **Spacing** – the baseline grid for running text
- **Design systems** – broader EDS-informed practices

## Demo

[`demo/typography/`](demo/typography/) is the page shown at the meetup: an
article set in Inter and Equinor, six controls labelled with the request you
would type to an agent, and a panel showing the CSS each request produces.
Open `index.html` over HTTP (the fonts load from the EDS CDN), or append
`?on=guides,scale,baseline,swap,xheight,weight` to arrive with everything on.
`INTENT.md` alongside records why it is built the way it is.

[`demo/typography-scale/`](demo/typography-scale/) is its companion explorer:
one step at a time through the size formula, both line-height curves, the
three densities and the 4px snap.

[`demo/typography-overlay/`](demo/typography-overlay/) overlays one sentence in
two faces on a shared baseline, with sliders that snap to the skills' x-height
and weight numbers.

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
 
## Third-party assets

Some skills bundle files they need in order to run — currently the Inter and
EB Garamond typefaces used by `typography-x-height-alignment` to demonstrate
itself without arguments.

**Bundled assets keep their own licences and are not covered by this
repository's MIT licence.** Both fonts are SIL OFL 1.1; their licence texts and
authorship sit alongside them in
[`skills/typography-x-height-alignment/assets/fonts/`](skills/typography-x-height-alignment/assets/fonts/).

## Status
 
🚧 Pre-release. Nothing here has been announced, and anything may change without warning until the meetup.
