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

2. **Drift exceeds tolerance, non-CSS target in play** — you are already in the
   two-ramp branch of `typography-scale`, baking a corrected size per step. Bake
   each step with *its own* correction, sampled at that step's `opsz` — but
   only where the difference clears half the snap unit at that step. On the
   0.5px grid that is 0.25px: about 1.6% at 16px and 0.7% at 37px. Below it
   the snap erases the per-step value, and for the pair above the per-step
   table comes out identical to the flat one at every step (10.5, 16.0, 37.5
   either way). Check this before building the table, or you will diff two
   identical files and not know whether the method or the arithmetic failed.
   `typography-scale` records the same limit among its positions.

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
