# Token shape

The DTCG output of `scripts/stem.py --format tokens`, referenced from section 7
of `SKILL.md`. Two token kinds: a **matched weight** per tier for the target
family, and the **letter-spacing port factor** that scales the reference's
tracking ramp for it. Both carry the derivation and the exact bytes they were
measured from.

The example below is the bundled Inter matched against itself at tier 400 —
the one pair the selftest can run without a second font — exactly as emitted.
A real pair reads the same way with two different `sha256`s and a
`correctionValue` other than 1; Inter against Equinor at ×1.137288 gave
`376.2 / 458.5 / 552.7` for tiers 300 / 400 / 500 on 2026-09-01, which is what
the `--match` example in section 3 reproduces.

```json
{
  "typography": {
    "font-weight": {
      "Inter": {
        "400": {
          "$type": "fontWeight",
          "$value": 400.1,
          "$extensions": {
            "com.equinor.typography": {
              "derived": {
                "expression": "stem(target, w) = stem(reference, tier) / correction",
                "inputs": {
                  "tier": 400,
                  "correction": 1.0,
                  "correctionValue": 1.0,
                  "instance": {
                    "wght": 400
                  }
                }
              },
              "metrics": {
                "reference": {
                  "path": "assets/fonts/Inter.woff2",
                  "sha256": "87a69aeae6290d8f4fc68e89eaca9a605defc155a3ea2bcb1f756fded1359722"
                },
                "target": {
                  "path": "assets/fonts/Inter.woff2",
                  "sha256": "87a69aeae6290d8f4fc68e89eaca9a605defc155a3ea2bcb1f756fded1359722"
                },
                "glyph": "l",
                "method": "outline:mid-height-stem"
              },
              "family": "Inter"
            },
            "com.equinor.figma": {
              "collection": "Typography",
              "scopes": [
                "FONT_WEIGHT"
              ]
            }
          }
        }
      }
    },
    "letter-spacing-port-factor": {
      "Inter": {
        "$type": "number",
        "$value": 1.0,
        "$extensions": {
          "com.equinor.typography": {
            "derived": {
              "expression": "target.sideSpaceEm / reference.sideSpaceEm",
              "inputs": {
                "reference": {
                  "advanceEm": 0.536339,
                  "inkEm": 0.432185,
                  "sideSpaceEm": 0.104154,
                  "sideSpaceShare": 0.194194,
                  "weight": 400.0
                },
                "target": {
                  "advanceEm": 0.536339,
                  "inkEm": 0.432185,
                  "sideSpaceEm": 0.104154,
                  "sideSpaceShare": 0.194194,
                  "weight": 400.0
                }
              }
            },
            "metrics": {
              "reference": {
                "path": "assets/fonts/Inter.woff2",
                "sha256": "87a69aeae6290d8f4fc68e89eaca9a605defc155a3ea2bcb1f756fded1359722"
              },
              "target": {
                "path": "assets/fonts/Inter.woff2",
                "sha256": "87a69aeae6290d8f4fc68e89eaca9a605defc155a3ea2bcb1f756fded1359722"
              },
              "glyphs": "a-z",
              "method": "outline:advance-minus-ink"
            },
            "family": "Inter"
          }
        }
      }
    }
  }
}
```

## Field notes

**`$value` is a plain number**, not a `100`–`900` keyword. CSS accepts any
weight in 1–1000 including fractions, and a variable font renders it.
Platforms that cannot — React Native rounds to hundreds — are the reason
section 7 asks about the target before emitting: on those, snap and record the
residual rather than pretend 458.5 was 500 all along.

**`derived.inputs.correction`** is the DTCG alias of the x-height correction
token when `--correction-token` names it, and the bare factor otherwise;
`correctionValue` is always the resolved number. Pass the alias: a matched
weight depends on the perceived size the pair is set at, and the alias is what
lets an audit follow that dependency back to the fonts.

**`metrics.method`.** `outline:mid-height-stem` means the widest ink run
across the glyph at its vertical midpoint, from the outline, not a rendered
bitmap and not the bounding box — the two diverge at axis extremes (section 1).
`glyph` is the letter measured; `l` is the default because it is a single
straight stem in almost every Latin design.

**`instance`** records the reference's axis location the tier was measured at.
With `--opsz` the optical size is pinned too, which is how the per-size table
in section 4 is produced; without it the reference's default `opsz` applies and
the token says so by omission.

**The port factor's inputs are both side-space records**, including the
weights they were measured at. Section 5 insists these are the *matched*
weights; a factor computed with both faces at 400 is a different number, and
the token shows which one you have.

**Namespace.** Reverse-DNS, in code spelling. Use the project's existing one if
it has one — grep for `"$extensions"` in the token files — otherwise ask for the
organisation's domain rather than inventing one.
