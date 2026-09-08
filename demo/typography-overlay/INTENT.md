# Overlay demo — intent

Built 6 September 2026 from a brief relayed from Victor: the missing middle
piece between the scale explorer and the toggle-by-toggle text demo. One
sentence — *sphinx of black quartz judge my vow* — rendered twice and overlaid
on one baseline, the reference face in pale grey-blue (`#B5C7C9`) and the
other in deep red (`#7D0023`, both Victor's, 8 September, and confirmed by him
after the review measured the reference at 1.75:1 on white — the one-face
toggle is the mitigation), so that the
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
  lines become one at the snap. The trim is the mechanism, not a refinement,
  so it is a hard requirement rather than a gated enhancement: Chrome 133,
  Safari 18.2 and Firefox 154 (18 August 2026) trim, and an older browser is
  shown a notice (`@supports not`) instead of two boxes that are not on one
  baseline under a line labelled "baseline".
- **Inter's x-height is one number per optical size, not per family** (7
  September, from the bot's review of #33). Inter's `opsz` axis lowers its
  x-height as the size grows — `OS/2.sxHeight` 0.545898 at opsz 14, 0.515625
  at opsz 32, confirmed against the outlines of x v w z and against Chrome's
  `measureText` at 14 / 32 / 48px — so the correction for a heading is
  × 1.074219, not × 1.137288. The demo carries both and picks by the rendered
  px, and the weight matches at opsz 32 were re-measured with that size's own
  correction. Equinor's x-height is flat along `wght` (0.48 at 400 and 600,
  outlines checked; its `MVAR` table does not move it) and Barlow's moves 1%
  between Regular and SemiBold (0.506 / 0.509 / 0.511), so one ratio serves
  every tier and the readout names the instance it holds at.
- **Reference face is a choice**: Inter (default) or Barlow; the adjusted
  face is always Equinor. A third pairing, Equinor as the reference with
  Inter adjusted, was built and removed on 8 September at Victor's request:
  the talk's story runs one way, the text face is the master. The numbers it
  used are kept below as a record. **The Barlow claim, verified 6
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
  referenced, never committed. Barlow is the first face in these demos served
  from outside the EDS CDN, so its arrival is checked (`document.fonts.check`)
  and a notice replaces a silently wrong reference when it is blocked; the
  fallback stack ends in Inter.
- **The frame does not move with the slider** (8 September, review). The
  zoom is sized from the reference's width at the widest the size slider can
  make the target, so the reference stays put while the target grows into the
  room; a narrow viewport scales the pair down rather than clipping it.
- **Numbers, measured 6–7 September 2026** with the two skills' scripts, in
  the `skills-test` venv (fontTools 4.64), against `InterVariable.woff2` from
  the EDS CDN (the copy bundled with `typography-weight-matching`, sha256
  `87a69aea…`), `EquinorVariable-VF.woff2` from the CDN (sha256 `e04fc3f7…`)
  and Barlow 400 / 500 / 600 static TTFs from Google Fonts (v13):
  - x-height ratios: `xheight.py FONT --location wght=400[,opsz=N]` — Inter
    0.545898 (opsz 14) / 0.515625 (opsz 32), Equinor 0.48, Barlow 0.506.
  - Inter → Equinor: `stem.py Inter.woff2 Equinor.woff2 --match 400,500,600
    --opsz 14 --correction 1.137288` → 458.5 / 552.7 / 660.0; `--opsz 32
    --correction 1.074219` → 458.4 / 563.1 / 680.7.
  - Barlow → Equinor: `stem.py Barlow-<Weight>.ttf Equinor.woff2 --match <w>
    --correction 1.054167` → 411.4 / 531.7 / 650.3 (Barlow has no axes, so one
    file per tier); Barlow → Inter 500 → 480.4.
  - Equinor → Inter (no longer shown): `stem.py Equinor.woff2 Inter.woff2
    --match 400,500 --opsz 14 --correction 0.879284` → 336.0 / 450.8.
    `stem.py` pins `--opsz` on the reference, and here the axis was the
    target's, so the opsz-32 values (334.7 / 446.4, correction 0.930909) were
    taken with the same functions and Inter's `opsz` pinned to 32 on the
    target; a `--target-opsz` flag for `stem.py` is the follow-up.
- **Sliders snap the applied value, not the control** (7 September). The
  detent used to write the snapped value back into the range input, so an
  arrow key moved one step into the tolerance and was pulled straight back —
  a keyboard trap at the exact state the deep links land on. The slider keeps
  its raw position; the applied size and weight snap; four arrow steps walk
  through the band and out.
- **One face at a time** (8 September, Victor). The two key entries above
  the overlay are checkboxes; unticking one hides that face and its x-height
  guide with `visibility: hidden`, so the hidden face keeps its box — the
  reference gives the pair its width and its baseline — and nothing shifts
  when it comes back. Both can be off; the baseline guide stays.
- Deep links: `?ref=inter&px=14&tier=500&size=snap&weight=snap`, plus
  `&show=ref` or `&show=target` for one face alone and `&guides=off`. Numeric
  `size` and `weight` are validated and clamped to the slider's range and the
  target's axis; anything else is ignored.

## Not done

- Victor's "14px Barlow medium ≈ 13px Inter medium" spatial-frequency idea:
  parked as a stretch, per the brief.
- The guides are drawn from the same constants the snap uses, so their meeting
  at the snap is arithmetic, not a measurement of the rendered glyphs. The
  measurement that backs them is the `measureText` check above; a live probe
  in the page would be the honest upgrade.
- `demo/typography/` and the weight-matching skill's per-step table still use
  the flat × 1.137288 at every heading size. With the drift measured here, the
  per-step corrections are 1.130 (16px) … 1.103 (24px) … 1.074 (32px+); whether
  the main demo moves to per-step corrections is an open decision, recorded
  there, not here.
