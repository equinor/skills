# When a font has an optical-size axis

`opsz` breaks the "pin the instance" rule in `SKILL.md` §1, because it is the
one axis you do not set. `font-optical-sizing: auto` is the initial value in
CSS, and with it the engine sets `opsz` per element from the rendered
font-size, clamped to the axis range. So a variable font with `opsz` and an
`MVAR` table has a different x-height at every step of the ramp, and a single
correction is only exact at the size it was measured at.

This holds whichever side of the pairing carries the axis. When the
**reference** has `opsz`, the target moves; when the **secondary** has it, the
thing being corrected moves. Both drift.

## Measure the drift, then decide

Sample the correction at each step of the ramp you will actually ship, with
`opsz` set to the step's pixel size:

```bash
for px in 10.5 12 14 16 18.5 21 24.5 28 32 37; do
  .venv/bin/python $skill/scripts/xheight.py --location opsz=$px,wght=400 REF.ttf SEC.ttf
done
```

Literata (reference, `opsz` 7–72, `MVAR` present) against Work Sans (no `opsz`,
x-height 0.500 throughout), measured 2026-09-03 at **`wght` 400** from the
Google Fonts variable files, `Literata[opsz,wght].ttf` sha256 `b41138c9…f274440`
and `WorkSans[wght].ttf` sha256 `f50f61f2…62a9f63` — re-measure rather than
trust these if either file differs:

| opsz (px) | Literata xRatio | correction | vs. flat 1.014 |
| --- | --- | --- | --- |
| 7 (axis floor) | 0.519 | 1.038 | +2.4% |
| 10.5 | 0.511 | 1.022 | +0.8% |
| 12 – 16 | 0.507 | 1.014 | 0 |
| 18.5 – 28 | 0.508 | 1.016 | +0.2% |
| 32 – 37 | 0.509 | 1.018 | +0.4% |
| 72 (axis ceiling) | 0.513 | 1.026 | +1.2% |

Here a flat scalar measured at the text step is within 0.8% everywhere on the
ramp. That is a property of this pair, not of the method: at the axis floor the
error is 2.4%, and another face can easily drift more. The number to publish is
the bound, not the assumption that it is small.

The EDS pair drifts more. Inter (reference, `opsz` 14–32, `MVAR` present)
against Equinor (no `opsz`, x-height 0.480 at every weight), measured
2026-09-07 at `wght` 400 from this skill's neighbour's bundled copy of Inter,
`typography-weight-matching/assets/fonts/Inter.woff2` sha256 `87a69aea…1359722`
(the EDS CDN's `InterVariable.woff2`), and `EquinorVariable-VF.woff2` sha256
`e04fc3f7…0603953`, and confirmed on
the outlines of x v w z and in Chrome's `measureText`:

| opsz (px) | Inter xRatio | correction | vs. flat 1.137288 |
| --- | --- | --- | --- |
| 14 (axis floor; 10.5 and 12 clamp here) | 0.545898 | 1.137288 | 0 |
| 16 | 0.542480 | 1.130167 | −0.6% |
| 18.5 | 0.538574 | 1.122029 | −1.3% |
| 21 | 0.534180 | 1.112875 | −2.1% |
| 24.5 | 0.528320 | 1.100667 | −3.2% |
| 28 | 0.522461 | 1.088460 | −4.3% |
| 32 (axis ceiling; 37 clamps here) | 0.515625 | 1.074219 | −5.5% |

A flat 1.137288 sets a 32px Equinor heading 5.9% too large by x-height
parity (36.393 / 34.375), and on the 0.5px grid the per-step table differs
from the flat one at every step from `2xl` up: 23.5 / 27 / 30.5 / 34.5 / 39.5
against 24 / 28 / 32 / 36.5 / 42. At `xl` the two land 0.28px apart and still
snap to the same 21px — the test is whether the *snapped* values differ, not
whether the raw gap clears half a unit. This pair takes outcome 2 below.

**Tolerance.** A size difference below about 1% does not read at text sizes;
above 2% it does. State the bound you accept, and record it.

## Three outcomes

1. **Drift within tolerance** — emit the flat correction measured at the text
   step, and record what was sampled so the claim is checkable:

   `drift` sits beside `derived` and `metrics` in the shape from
   [`token-shape.md`](token-shape.md); `instance` stays inside `metrics`, where
   the emitter reads it:

   ```json
   "com.equinor.typography": {
     "derived": { "…": "as in token-shape.md" },
     "metrics": { "…": "as in token-shape.md", "instance": { "opsz": 16, "wght": 400 } },
     "drift": {
       "axis": "opsz",
       "sampledAt": [10.5, 12, 14, 16, 18.5, 21, 24.5, 28, 32, 37],
       "range": [1.014, 1.022],
       "max": 0.0079
     }
   }
   ```

   `sampledAt` lists every step's px, clamped ends included; `range` is the
   lowest and highest correction found; `max` is `high / low − 1`. A build
   can recompute all three from the fonts and fail on disagreement.

2. **Drift exceeds tolerance, non-CSS target in play** — you are already in the
   two-ramp branch of `typography-scale`, baking a corrected size per step. Bake
   each step with *its own* correction, sampled at that step's `opsz`, and
   keep only the steps whose *snapped* display size differs from the flat
   one. On the 0.5px grid a difference under 0.25px never survives, and one
   over it may still not (Inter/Equinor `xl` above). Below it the snap erases
   the per-step value, and for the Literata pair above the per-step table
   comes out identical to the flat one at every step (10.5, 16.0, 37.5 either
   way). Check this before building the table, or you will diff two identical
   files and not know whether the method or the arithmetic failed.
   `typography-scale` records the snap limit among its positions.

   The token is then a **group, one correction per step**, in place of the
   single `display` token: the flat value has no step it is true for. Each
   entry carries the same `derived` and `metrics` as the flat token, with
   `metrics.instance.opsz` set to the step's px, and the group carries the
   `drift` block. `typography-weight-matching` names the step's token in
   `--correction-token`, so its `correctionValue` and this `$value` agree.

   ```json
   "x-height-correction": { "display": {
     "$extensions": { "com.equinor.typography": { "drift": {
       "axis": "opsz", "sampledAt": [10.5, 12, 14, 16, 18.5, 21, 24.5, 28, 32, 37],
       "range": [1.074219, 1.137288], "max": 0.0587 } } },
     "2xl": { "$type": "number", "$value": 1.112875, "$extensions": { "com.equinor.typography": {
       "derived": { "expression": "referenceXRatio / selfXRatio",
                    "inputs": { "referenceXRatio": 0.534180, "selfXRatio": 0.48 } },
       "metrics": { "…": "as in token-shape.md", "instance": { "opsz": 21, "wght": 400 } } } } },
     "5xl": { "$type": "number", "$value": 1.074219, "$extensions": { "com.equinor.typography": {
       "derived": { "…": "referenceXRatio 0.515625" },
       "metrics": { "…": "instance opsz 32, wght 400" } } } }
   } }
   ```

   `xheight.py` emits the flat token today and the per-step group is built by
   running it once per step; `scale.py` takes one `--correction`, so the
   display ramp is baked per step by hand until both grow the option.
   `typography-scale` records that limit among its positions.

3. **Drift exceeds tolerance, CSS only** — `size-adjust` is one number per
   `@font-face`, and `@font-face` has no size-range descriptor, so the flat
   scalar cannot be made exact. Either accept it and publish the bound, or move
   to the baked branch. Pinning `opsz` (`font-optical-sizing: none`, or
   `font-variation-settings: "opsz" 14`) makes the scalar exact at the cost of
   the optical sizing itself — which is usually the wrong trade, and if taken
   must be recorded in the token as the instance the correction holds at.

## What is not settled

How an engine picks `opsz` for a face that also carries `size-adjust` — the
nominal font-size or the adjusted one — was not measured for this note. If a
pairing depends on it, read the rendered result back from the browser rather
than assuming either.

## Related

`typography-weight-matching` treats the same axis from the other side: what
`opsz` does to stem weight and spacing, and how to compensate a face that has
no such axis.
