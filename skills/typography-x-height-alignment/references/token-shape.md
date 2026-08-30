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
        "$description": "Reference family — corrected against itself."
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
number against a newer release of the font.

**The reference family carries `$value: 1`.** Emitting it is deliberate — a
consumer that special-cases "the family without a factor" breaks the first time
the reference changes.
