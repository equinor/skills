# Equinor Skills
 
A growing collection of Agent Skills covering design systems, colour, spacing and typography.
 
This repository is just getting started. Skills land here as they are written, ahead of being introduced at the [Into Design Systems](https://luma.com/ids-oslo) meetup, Oslo, on 9 September 2026, with more added over time.
 
## What's here
 
Skills are built to the open [Agent Skills](https://agentskills.io) standard, so they work across Claude Code, Copilot, Cursor, Codex, and other compatible agents – not just one tool.
 
Available now:

- **[typography-scale](skills/typography-scale)** – algorithmic type scales: sizes from one base and one ratio, line-height as a curve rather than a fixed multiple, density as a single number
- **[typography-x-height-alignment](skills/typography-x-height-alignment)** – align two paired fonts by measured x-height, and deliver the correction as a design token

Planned areas:

- **Typography** – font-weight and letter-spacing derived per scale step, optical padding
- **Colour** – OKLCH palettes, contrast (APCA)
- **Spacing** – ratio-based spacing scales, inset proportions
- **Design systems** – broader EDS-informed practices

## Installing a skill
 
Once skills are published, install a single one with:
 
```bash
npx skills add equinor/skills --skill <skill-name>
```
 
## Status
 
🚧 Pre-release. Nothing here has been announced, and anything may change without warning until the meetup.
