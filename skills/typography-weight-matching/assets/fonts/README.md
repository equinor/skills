# Bundled fixture font

One typeface so `typography-weight-matching` runs with no arguments, and so its
selftest can assert the numbers the skill documents. It is here to be
**measured**, not recommended.

| Font | Author(s) | Licence | Role |
| --- | --- | --- | --- |
| Inter | Rasmus Andersson and the Inter Project Authors | [SIL OFL 1.1](Inter-OFL.txt) | Reference face: has both a `wght` and an `opsz` axis |

Fetched from the [Google Fonts repository](https://github.com/google/fonts)
(`ofl/inter/Inter[opsz,wght].ttf`) on 2026-08-30 and recompressed to woff2 with
`fontTools`, lossless, no subsetting; the same bytes
`typography-x-height-alignment` bundles. Google is the distributor; the
copyright is the authors'.

**Not covered by this repository's MIT licence.** The OFL text is alongside.
`SHA256SUMS` pins the bytes every documented number was measured from:

```bash
shasum -a 256 -c SHA256SUMS
```

## What it demonstrates

- `--weights 300,400,500,700` → stems `0.066082 0.087891 0.107402 0.146423` em:
  the axis is not evenly spaced (+33.0% then +22.2%).
- The `opsz` axis thins the stem by −4.93% at 300, −5.56% at 400, −1.89% at
  700 between its ends: the correction peaks at the default weight.
- Side space at 400: `0.104154em`, 19.4% of the advance — the denominator of a
  tracking port factor.

The second face of a pairing is not bundled. Equinor is proprietary; for a
public pair, fetch one from the test-pairings table in `SKILL.md`.
