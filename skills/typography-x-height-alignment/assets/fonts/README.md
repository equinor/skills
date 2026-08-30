# Bundled demo fonts

Two typefaces so `typography-x-height-alignment` runs with no arguments. They
are here to be **measured**, not to be used as a design recommendation.

## What these are, and who made them

| Font | Author(s) | Licence | Role in the demo |
| --- | --- | --- | --- |
| Inter | Rasmus Andersson and the Inter Project Authors | [SIL OFL 1.1](Inter-OFL.txt) | Reference family |
| EB Garamond | Georg Duffner, Octavio Pardo and the EB Garamond Project Authors | [SIL OFL 1.1](EBGaramond-OFL.txt) | Corrected family |

Both were fetched from the [Google Fonts repository](https://github.com/google/fonts)
on 2026-08-30, which is a *distributor* — the copyright belongs to the authors
above, not to Google.

```
ofl/inter/Inter[opsz,wght].ttf          → Inter.woff2
ofl/ebgaramond/EBGaramond[wght].ttf     → EBGaramond.woff2
```

The variable TTFs were converted to woff2 with `fontTools` (lossless
recompression, no subsetting or modification). `unitsPerEm`, `sxHeight` and
`sCapHeight` were verified byte-identical before and after, so the demo measures
the same numbers the originals do. The files are unmodified in every sense the
OFL cares about — no Reserved Font Name issue arises.

## Licence

**These fonts are not covered by this repository's MIT licence.** They are
distributed under the SIL Open Font License 1.1, which requires that font
software remain entirely under the OFL. The full licence text sits beside each
font, and each binary additionally carries its copyright, licence and licence
URL in its `name` table.

Practical consequences if you copy this directory: keep the `OFL.txt` files with
the fonts, do not sell the fonts on their own, and do not rename a modified
version to a Reserved Font Name.

## Verifying

```bash
shasum -a 256 -c SHA256SUMS
python3 xheight.py            # no arguments → measures this pair
```

Expected:

```
Inter        upm 2048   xHeight 1118   xRatio 0.545898   (reference)
EB Garamond  upm 1000   xHeight  400   xRatio 0.400000   correction 1.364746
```

If those numbers change, the fonts were updated upstream — which is exactly the
event the skill exists to catch. Re-derive; do not edit the expected values to
match.
