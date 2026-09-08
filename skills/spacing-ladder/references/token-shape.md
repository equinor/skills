# Token shape

The DTCG output of `scripts/spacing.py tokens`, referenced from section 7 of
`SKILL.md`. One file per density — `spacing.compact.tokens.json`,
`spacing.comfortable.tokens.json`, `spacing.relaxed.tokens.json` — with the
same paths in each, so density is a mode and nothing else changes.

Five groups: the **ladder** (a value per rung, with the sequence and the
density's offset as inputs), the **insets** (aliases of ladder rungs: the
vertical rung is one below, the same as, or one above the horizontal), the
**optical paddings** (a value with its derivation and the height it produces,
for a label whose step equals the inset size — other pairings come from
`spacing.py control`), the **icon gaps** (derived from the label's size), and
the **icon sizes** (a second sequence read with the ladder's density offset).
The `md` rung, the `md` inset, the `md` squished padding, the `md` icon gap and
the `md` icon size at comfortable density, exactly as emitted:

```json
{
  "spacing": {
    "ladder": {
      "md": {
        "$type": "dimension",
        "$value": {
          "value": 16,
          "unit": "px"
        },
        "$extensions": {
          "com.equinor.spacing": {
            "derived": {
              "expression": "SEQUENCE[index(rung) + offset(density)]",
              "inputs": {
                "sequence": [
                  1,
                  2,
                  4,
                  6,
                  8,
                  12,
                  16,
                  20,
                  24,
                  28,
                  32,
                  36
                ],
                "rung": "md",
                "offset": 1
              }
            },
            "density": "comfortable"
          },
          "com.equinor.figma": {
            "collection": "Spacing",
            "mode": "comfortable",
            "scopes": [
              "GAP",
              "WIDTH_HEIGHT"
            ]
          }
        }
      }
    },
    "inset": {
      "md": {
        "horizontal": {
          "$type": "dimension",
          "$value": "{spacing.ladder.md}"
        },
        "vertical-squished": {
          "$type": "dimension",
          "$value": "{spacing.ladder.sm}"
        },
        "vertical-squared": {
          "$type": "dimension",
          "$value": "{spacing.ladder.md}"
        },
        "vertical-stretched": {
          "$type": "dimension",
          "$value": "{spacing.ladder.lg}"
        }
      }
    },
    "optical-padding": {
      "md-squished": {
        "$type": "dimension",
        "$value": {
          "value": 10,
          "unit": "px"
        },
        "$extensions": {
          "com.equinor.spacing": {
            "derived": {
              "expression": "inset - (lineHeight - round(fontSize * capRatio, 4px)) / 2",
              "inputs": {
                "inset": "{spacing.inset.md.vertical-squished}",
                "label": "md",
                "lineHeight": 16,
                "fontSize": 14.0,
                "capRatio": 0.727539
              }
            },
            "height": 36,
            "density": "comfortable",
            "note": "deliberately off the 4px grid; never round it \u2014 the height is what lands"
          },
          "com.equinor.figma": {
            "collection": "Spacing",
            "mode": "comfortable",
            "scopes": [
              "GAP"
            ]
          }
        }
      }
    },
    "icon-gap": {
      "md": {
        "$type": "dimension",
        "$value": {
          "value": 8,
          "unit": "px"
        },
        "$extensions": {
          "com.equinor.spacing": {
            "derived": {
              "expression": "round(fontSize * 0.618, 2px)",
              "inputs": {
                "fontSize": 14.0,
                "label": "md"
              }
            },
            "density": "comfortable",
            "note": "inside the atom only: glyph to label, never between siblings"
          },
          "com.equinor.figma": {
            "collection": "Spacing",
            "mode": "comfortable",
            "scopes": [
              "GAP"
            ]
          }
        }
      }
    },
    "sizing-icon": {
      "md": {
        "$type": "dimension",
        "$value": {
          "value": 20,
          "unit": "px"
        },
        "$extensions": {
          "com.equinor.spacing": {
            "derived": {
              "expression": "ICON_SEQUENCE[index(size) + offset(density)]",
              "inputs": {
                "sequence": [
                  14,
                  16,
                  18,
                  20,
                  24,
                  28,
                  32,
                  37,
                  42,
                  48,
                  56,
                  64
                ],
                "size": "md",
                "offset": 1
              }
            },
            "density": "comfortable",
            "note": "the glyph's ink size only; its footprint is the label's cap cell, margin (cap - glyph) / 2"
          },
          "com.equinor.figma": {
            "collection": "Spacing",
            "mode": "comfortable",
            "scopes": [
              "WIDTH_HEIGHT"
            ]
          }
        }
      }
    }
  }
}
```

## Field notes

**The ladder's `derived.inputs` is the whole sequence and one offset.** That is
the entire spacing system: anyone with the twelve numbers and the three
offsets regenerates every rung at every density. The extrapolated top value
carries `extrapolated: true`.

**Insets are aliases, not values.** `{spacing.ladder.sm}` is the DTCG alias
syntax; a consumer that resolves aliases gets the number, and the relationship
(vertical is one rung below horizontal for `squished`) survives in the file
instead of being a coincidence of two equal numbers.

**Optical padding records what made it.** `inset` is an alias, `label` names
the step whose line-height and cap were used, `fontSize` and `lineHeight` are
the resolved pixels, `capRatio` is the label face's `capHeight / unitsPerEm`
(Inter 0.727539). `height` is what the padding produces, and is the number the
control is allowed to be checked against; the padding itself is deliberately
off the 4px grid, and `note` says so where the number is.

**Icon sizes are ink, not layout.** `sizing-icon` is the glyph's drawn size and
nothing else; the `note` says so where the number is. The glyph's footprint is
the label's cap cell, and the seat — `margin: (cap − glyph) / 2`, negative by
construction — is a component-level pairing of a label step with an icon step,
so it is not a token. `spacing.py glyph --label md --icon md` gives it, and the
CSS output carries `--glyph-margin-<step>` for the label-equals-icon pairing
only; `--glyph-margin-sm` is −5 and the small button's `sm`/`xs` seat is −4.
The `icon-gap` is measured to the cap cell, so the visible ink-to-text distance
is `gap + margin`.
Relaxed `6xl` is flagged `extrapolated` like the ladder's top rung. Upstream
the same values live in the typography build (`sizing-icon-*` beside the type
scale); they are emitted here, under `spacing`, because the glyph seat that
consumes them is a spacing recipe and `typography-scale` does not emit them.
A consumer applying both should alias one to the other rather than keep two.

**Figma** gets `optical-padding` per density mode, named from the token path
(`spacing/optical-padding/<size>-<proportion>`), bound to `paddingTop` /
`paddingBottom`; the control's `min-height` is a second variable,
`inset × 2 + cap`. It cannot evaluate the expression, so it carries the
resolved number and the tokens carry the derivation.

**Namespace.** Reverse-DNS, in code spelling — `com.equinor.spacing` here. Use
the project's existing namespace if it has one.
