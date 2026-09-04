# Figma output

Referenced from section 5 of `SKILL.md`. Figma cannot evaluate `round()` or
`pow()`, so it receives **baked values from the same source** as the tokens —
never typed in — as variables, with text styles bound to them.

## What gets created

`scripts/scale.py --format figma --out DIR` writes two Plugin API scripts. Run
them in order; both are idempotent and reuse anything with the same name.

1. **`figma-variables.js`** — a collection `Typography` with one mode per
   density, `comfortable` first so it is the collection's default;
   `FLOAT` variables `font-size/<step>` scoped `FONT_SIZE` and
   `line-height/<step>/<curve>`
   scoped `LINE_HEIGHT`, with the pixel value per mode and the CSS custom
   property as `WEB` code syntax. With `--correction`, `font-size-display/<step>`
   as well.
2. **`figma-text-styles.js`** — `text/<step>` (default curve) and
   `label/<step>` (compressed curve), and `display/<step>` when a correction is
   given, each with `fontSize` and `lineHeight` **bound to the variables** via
   `TextStyle.setBoundVariable`, never set as literals. Switching the
   collection's mode on a frame re-sizes every style in it.

Density as modes is the whole reason to bind rather than bake into styles: a
style holding a literal 14 cannot follow a mode.

A collection's default mode is fixed when it is created and the Plugin API
cannot change it afterwards. The variables script checks the default on every
run and refuses, with a message, if it is not `comfortable` — which is what a
collection built by a version of this emitter before 4 September 2026 looks
like. The remedy is to delete that collection and run the script again; the
styles re-bind to the new variables on the next run of the styles script.

## With a Figma MCP

If the session has a Figma MCP (`use_figma` or equivalent), pass each script's
contents as the `code`, targeting the file the user names. Load the `figma-use`
guidance first; it is a prerequisite of the tool. Ask for the file URL if none
was given — do not create a file unprompted. Return the created and updated IDs
the scripts report.

## Without one

Write the two files next to the tokens and say how to run them: in Figma,
*Plugins → Development → New plugin*, paste a script as `code.js`, run it from
the plugins menu; or use a script-runner plugin. Everything else — tokens and
CSS — is still delivered in full. A user who asked only for CSS is never asked
to set up Figma.

## What the scripts check

- Every family *and style* the styles will use — `--family` / `--style`
  (default Inter Regular) and `--display` / `--display-style` — is present in
  the file, checked as pairs before the loop; a missing one throws before
  anything is created, and names what is missing.
- The variables exist before the styles are bound; running the styles script
  first fails with a message, not a half-built set.

## What is not in Figma

The expressions. Figma gets the resolved numbers per mode; the derivation lives
in the tokens' `$extensions` and in the variables' `WEB` code syntax, which
points back at the CSS custom property that *does* carry the formula.
