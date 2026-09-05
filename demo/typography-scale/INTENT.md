# Scale explorer — intent

A recreation of the interactive scale demo used in a 2025 talk, rebuilt on
5 September 2026 in the same style as `demo/typography/` so the two can be
shown side by side. Where that page shows what three skills do to a page of
text, this one explains how one number in the scale is computed.

## What it is

A slider across the ten steps; radios for the two line-height curves and the
three densities; three toggles for the 4px grid: snap the line-heights, align
the baselines, show the guides. A preview paragraph at the chosen size. Three
tiles (size, line-height, multiplier), the arithmetic written out for the
chosen step, and the whole scale as a table. Deep links:
`index.html?step=8&curve=compressed&density=compact&snap=0&baseline=1&guides=1`.

## Decisions

- **The names are the skill's.** The second curve is `compressed`, not
  "squished" (Nathan Curtis's spacing term, reserved for the inset ladder).
  The curve is written the way the CSS emits it, `1.39 − 0.29 × (step/9)³`,
  not as an ease-out in a reversed progress variable; same maths, one name.
- **The constants are the skill's, and the selftest checks that.**
  `explorer.js` carries `STEPS_PER_OCTAVE`, both snaps, both curves and the
  three densities verbatim, and `typography-scale/scripts/selftest.sh` greps
  for them when this checkout has the demo, so the third copy of the
  arithmetic cannot drift from `scale.py` unnoticed.
- **Snapping is a toggle, on by default.** Off, the table shows the raw curve:
  smooth, monotonic percentages and off-grid line boxes. On is the moment the
  ratios go non-monotonic and the boxes land, which is the argument for the
  snap made visible.
- **Baselines are a second toggle, gated on the snap**, using the same trim
  recipe as `demo/typography/`; the arithmetic panel measures the first
  baseline's distance from the surface edge and reports whether it is on the
  grid, rather than asserting it.
- Fonts from the EDS CDN, never bundled. Same palette and spacing tokens as
  the other demo.
