# Token shape

The DTCG output of `scripts/scale.py`, referenced from section 5 of
`SKILL.md`. One file per density — `scale.compact.tokens.json`,
`scale.comfortable.tokens.json`, `scale.relaxed.tokens.json` — with the same
token paths in each, so a consumer treats density as a mode and nothing else
changes between the files.

The point of the `$extensions` block is that every `$value` is *checkable*: a
build can read `derived.expression` and its `inputs`, recompute, and fail if
they disagree. A size without its constants is a literal that happens to be
right today. The `md` step at comfortable density, exactly as emitted:

```json
{
  "typography": {
    "font-size": {
      "md": {
        "$type": "dimension",
        "$value": {
          "value": 0.875,
          "unit": "rem"
        },
        "$extensions": {
          "com.equinor.typography": {
            "derived": {
              "expression": "round(base * pow(2, step / 5), 0.03125rem)",
              "inputs": {
                "base": {
                  "value": 1,
                  "unit": "rem"
                },
                "step": -1
              }
            },
            "step": "md",
            "density": "comfortable"
          },
          "com.equinor.figma": {
            "collection": "Typography",
            "mode": "comfortable",
            "scopes": [
              "FONT_SIZE"
            ]
          }
        }
      }
    },
    "line-height": {
      "md": {
        "default": {
          "$type": "dimension",
          "$value": {
            "value": 20,
            "unit": "px"
          },
          "$extensions": {
            "com.equinor.typography": {
              "derived": {
                "expression": "round(fontSize * (max - pow(n / (N - 1), 3) * drop), 4px)",
                "inputs": {
                  "fontSize": "{typography.font-size.md}",
                  "n": 2,
                  "N": 10,
                  "max": 1.39,
                  "drop": 0.29
                }
              },
              "step": "md",
              "curve": "default",
              "density": "comfortable"
            },
            "com.equinor.figma": {
              "collection": "Typography",
              "mode": "comfortable",
              "scopes": [
                "LINE_HEIGHT"
              ]
            }
          }
        }
      }
    }
  }
}
```

## Field notes

**`$value` is a DTCG dimension**, `{ value, unit }`. Sizes are in `rem`
because density is a `rem` base and the snap is `0.03125rem`; line-heights are
in `px` because the 4px grid is a pixel grid. Consumers that want pixels
multiply by the root size, which the Figma emitter does at 16.

**`derived.expression`** is the formula in the skill's own notation, not CSS;
`inputs` names every free variable in it. `step` is the offset from the base
step (`lg` = 0), `n` and `N` index the line-height curve by label, per the
trade-off recorded in section 3. `{typography.font-size.md}` is a DTCG alias:
the line-height's input *is* the size token, so changing one cannot orphan the
other.

**`com.equinor.figma`** carries what the Figma emitter needs and nothing else:
the collection, the mode (the density), and the variable scopes. It says
nothing about text styles; those are derived from the curve name
(`default` → `text/<step>`, `compressed` → `label/<step>`). See
[`figma.md`](figma.md).

**Two families.** With `--correction`, a third group `font-size-display`
appears, each token deriving from its text-size sibling times the factor and
pointing at the *shared* line-height, per section 4's rule that both families
take the same line box. Its `inputs` carry `correctionValue`, the resolved
factor, and `correction`, which is the DTCG alias of the token
`typography-x-height-alignment` emitted when `--correction-token` names it
(for example `{typography.x-height-correction.display}`) and the bare factor
otherwise. Pass the alias: it is what lets an audit follow the number back to
the fonts it was measured from.

**Namespace.** Reverse-DNS, in code spelling. Use the project's existing
namespace if it has one — grep for `"$extensions"` in the token files — and
otherwise ask for the organisation's domain rather than inventing one.
