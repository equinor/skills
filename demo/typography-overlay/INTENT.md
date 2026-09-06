# Overlay demo — intent

Built 6 September 2026 from a brief relayed from Victor: the missing middle
piece between the scale explorer and the toggle-by-toggle text demo. One
sentence — *sphinx of black quartz judge my vow* — rendered twice and overlaid
on one baseline, the reference face in blue and the other in red, so that the
overlap reads dark and both stay legible (`mix-blend-mode: multiply` on white).
Two sliders bring the second face to the first: size until the x-heights meet,
weight until the stems do. The snap points are the skills' numbers.

## Decisions

- **The snap is a detent, not the end of the slider.** The size slider runs
  0.85 to 1.25 and clicks into the correction for the pairing (× 1.137288 for
  Inter → Equinor); the weight slider runs the target's axis and clicks into
  the matched weight. Watching the thumb land on the number is the point.
- **Rendered at the real size, shown larger.** The pair is set at 14, 32 or
  48px, which is what Inter's `opsz` axis actually sees, and scaled up with a
  transform, which does not change the computed font-size and so leaves the
  optical axis honest. `zoom` would not.
- **One baseline through `text-box: trim-both cap alphabetic`.** The trimmed
  box ends on the baseline, so aligning the two boxes' bottoms aligns the
  baselines; guides mark the baseline and both x-heights, and the two x-height
  lines become one at the snap.
- **Reference face is a choice**: Inter (default, target Equinor), Barlow
  (target Equinor), Equinor (target Inter). **The Barlow claim, verified 6
  September from primary sources**, is narrow and real: the Lc number is
  colour math with no font input, but the font lookup table that turns an Lc
  target into a minimum size and weight — `src/apca-w3.js` and
  `data/LUT-GseriesMay28-2022.js` in Myndex's apca-w3 — is annotated in its
  source "reference font is Barlow". Myndex's prose names Helvetica/Arial as
  exemplars and never Barlow, so the demo cites the source comment, nothing
  stronger, and never says "Lc values made with Barlow". By APCA's own
  x-height-ratio method, 14px Barlow (x-height 7.08px) is 13px Inter; that is
  x-height parity, not optical parity. Their docs call weight matching
  "ongoing research"; the weight slider is a measured answer to it. The
  numbers: Equinor 500 has a thinner stem than Barlow Medium and needs 531.7
  to match; Inter 500 is thicker and needs only 480.4 — measured here with
  `stem.py`, since no stroke measurement exists in APCA's sources.
- **Fonts are not bundled.** Inter and Equinor from the EDS CDN as raw files,
  Barlow from Google Fonts. Equinor's licence permits use in an application
  and forbids redistribution; this repository is public, so the file is
  referenced, never committed.
- **Numbers, measured 6 September 2026** with the two skills' scripts:
  x-height ratios Inter 0.545898, Equinor 0.48, Barlow 0.506; matched Equinor
  weights for Inter 400 / 500 / 600 at opsz 14: 458.5 / 552.7 / 660.0 and at
  opsz 32: 438.0 / 529.8 / 640.8; for Barlow Regular / Medium / SemiBold:
  411.4 / 531.7 / 650.3; Inter for Equinor 400 / 500: 336.0 / 450.8.
- Deep links: `?ref=inter&px=14&tier=500&size=snap&weight=snap`.

## Not done

- Victor's "14px Barlow medium ≈ 13px Inter medium" spatial-frequency idea:
  parked as a stretch, per the brief.
- Matching Inter to an Equinor reference at opsz 32 (only opsz 14 measured).
