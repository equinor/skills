# Equinor Skills
 
A growing collection of Agent Skills covering design systems, colour, spacing and typography.
 
This repository is just getting started. Skills land here as they are written, ahead of being introduced at the [Into Design Systems](https://luma.com/ids-oslo) meetup, Oslo, on 9 September 2026, with more added over time.
 
## What's here
 
Skills are built to the open [Agent Skills](https://agentskills.io) standard, so they work across Claude Code, Copilot, Cursor, Codex, and other compatible agents – not just one tool.
 
Available now:

- **[typography-scale](skills/typography-scale)** – algorithmic type scales: sizes from one base and one ratio, line-height as a curve rather than a fixed multiple, density as a single number
- **[typography-x-height-alignment](skills/typography-x-height-alignment)** – align two paired fonts by measured x-height, and deliver the correction as a design token
- **[typography-weight-matching](skills/typography-weight-matching)** – match weight and letter-spacing across a font pair, and compensate for a face with no optical-size axis

Planned areas:

- **Typography** – optical padding, algorithmic tracking for prose
- **Colour** – OKLCH palettes, contrast (APCA)
- **Spacing** – ratio-based spacing scales, inset proportions
- **Design systems** – broader EDS-informed practices

## Browser support

The CSS in these skills targets modern, evergreen browsers. Features are
recommended on the basis that they are Baseline available — not that they are
universally supported — because the products these skills came from run on
centrally managed browsers that update continuously.

If you need to support older browsers, that is your project's call to make.
Every skill that recommends a CSS feature also tells you how to check it against
your own browser matrix first.

## Installing a skill
 
Once skills are published, install a single one with:
 
```bash
npx skills add equinor/skills --skill <skill-name>
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
