# The closed form

Worked for one pair — Inter as reference, Equinor as target. The *shape* is
general; every constant is specific to those two faces and must be re-measured
for any other pair.

## Reference face: stem as a function of weight and optical size

Both relationships are piecewise linear with a knee at **400**, which is the
reference face's own default instance. Two breaks in the same place is the
font's construction showing through twice.

```
inter_stem14(w)   = 0.08789 + (w − 400) × (0.0002181 if w < 400 else 0.0001951)
optical_delta(w)  = −0.00488 + (w − 400) × (−0.0000162 if w < 400 else 0.00000703)
inter_stem(w, px) = inter_stem14(w) + optical_delta(w) × (clamp(px,14,32) − 14) / 18
```

`optical_delta` is the *total* stem change from the axis minimum to its maximum
at that weight. It is not constant across weights — measured:

```
wght     300     350     400     450     500     550     600     700
thinning -4.94%  -5.28%  -5.56%  -4.64%  -3.89%  -3.27%  -2.74%  -1.90%
```

It peaks at the default weight and falls away both ways. Within any single
weight the slope is exactly constant, so this is structure, not noise.

## Target face: stem as a function of weight

Masters at the axis extremes, default in the middle, and an `avar` table that
remaps normalised −0.5 to −0.42:

```
n = (w − 500) / 200
avar(n) piecewise linear through (−1,−1) (−0.5,−0.42) (0,0) (1,1)

equinor_stem(w) = S500 + |avar(n)| × (S300 − S500)    for n < 0
                = S500 +  avar(n)  × (S700 − S500)    for n ≥ 0
                  S300 = 0.03600   S500 = 0.08600   S700 = 0.11475
```

This reproduces every measured stem to five decimal places.

## Matching

```
weight(tier, px) = equinor_stem⁻¹( inter_stem(tier, px) / xHeightCorrection )
```

Monotonic, so bisection is sufficient.

## Verification

Worst deviation against directly measured values: **4.11 weight units**.

| | as % of stem width |
| --- | --- |
| Worst deviation | 1.08% |
| One 5-unit rounding step | 1.35% |
| The entire optical ramp | 5.0% |
| One weight tier, 400 → 500 | 32% |

Below a rounding step and far below anything visible. Cells that round to
different multiples of 5 are landing either side of a boundary, not disagreeing.

**Generate the table from the algorithm and commit the generated values** — the
derivation stays the source, the numbers stay inspectable, and a font update
re-derives instead of silently invalidating.
