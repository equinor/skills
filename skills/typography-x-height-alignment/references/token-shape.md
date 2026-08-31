# Token shape

The full DTCG example for the x-height correction, referenced from section 3 of
`SKILL.md`.

The point of the `$extensions` block is that the committed `$value` is
*checkable*: a build can read `derived.expression` and its `inputs`, recompute,
and fail if they disagree. A number without its derivation is a literal that
happens to be right today.

```json
{
  "typography": {
    "font-family": {
      "text": { "$type": "fontFamily", "$value": ["Inter", "sans-serif"] },
      "display": { "$type": "fontFamily", "$value": ["Equinor", "sans-serif"] }
    },
    "x-height-correction": {
      "text": {
        "$type": "number",
        "$value": 1,
        "$description": "Reference family — corrected against itself.",
        "$extensions": {
          "com.equinor.typography": {
            "metrics": {
              "family": "Inter",
              "unitsPerEm": 2048,
              "xHeight": 1118,
              "capHeight": 1490,
              "extent": 1.209961,
              "source": "https://cdn.example.com/font/InterVariable.woff2",
              "extractedAt": "2026-08-29",
              "method": "OS/2.sxHeight"
            }
          }
        }
      },
      "display": {
        "$type": "number",
        "$value": 1.137288,
        "$description": "Scale Equinor by this to match Inter's x-height.",
        "$extensions": {
          "com.equinor.typography": {
            "derived": {
              "expression": "referenceXRatio / selfXRatio",
              "inputs": {
                "reference": "{typography.font-family.text}",
                "referenceXRatio": 0.545898,
                "selfXRatio": 0.48
              }
            },
            "metrics": {
              "family": "Equinor",
              "unitsPerEm": 1000,
              "xHeight": 480,
              "capHeight": 700,
              "extent": 1.0,
              "source": "https://cdn.example.com/font/EquinorVariable-VF.woff2",
              "extractedAt": "2026-08-29",
              "method": "OS/2.sxHeight"
            }
          }
        }
      }
    }
  }
}
```

## Field notes

**Namespace.** DTCG requires `$extensions` keys to be reverse-DNS. Use the
project's existing namespace if it has one — grep for `"$extensions"` in the
token files — otherwise ask for the organisation's domain rather than inventing
one. `com.equinor.typography` above is the reference implementation's.

**`method`.** `OS/2.sxHeight` and `measured:x-glyph-bounds` are not the same
quality of evidence, and the difference matters when someone re-derives the
number against a newer release of the font. `scripts/xheight.py` emits it — copy
it through rather than deciding it yourself.

**`instance`.** For a variable font, record the axis location the metrics were
read at (`{"wght": 400}`). A correction derived from a font with an `MVAR` table
is only valid at that point; without it, the token cannot be rechecked and a
reader cannot tell whether it applies to the weight they are setting.

**`source` without a URL.** When the font was measured from a local file, record
the path plus the `sha256` the script emits. The checksum pins the exact bytes
measured, which is the property the URL was standing in for.

**The reference family carries `$value: 1` *and* its own metrics.** Both are
deliberate. A consumer that special-cases "the family without a factor" breaks
the first time the reference changes — and the emitter in
[`emit-font-faces.md`](emit-font-faces.md) reads `metrics` for every family, so
omitting the block there makes it throw on the first iteration.

**`metrics.family`** is the name from the font's `name` table, which
`scripts/xheight.py` emits. The emitter uses it rather than the token key, so
the `@font-face` family name matches the binary rather than whatever the token
happened to be called.
