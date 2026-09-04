# Live run: typography-scale Figma emitter against a real file

**Date:** 2026-09-04. **Skill:** `typography-scale` as merged in #27.
**Task:** "Build the EDS scale for Inter and Equinor and put it in Figma" —
representative request 3 — against a scratch file Victor created for it,
through the Figma MCP (`use_figma`), with `--correction 1.137288 --display
Equinor`. Run by the author of the emitter, not a fresh session; the
fresh-session test is still owed (#22).

## What held

- The variables script created a `Typography` collection with three modes and
  40 `FLOAT` variables: `font-size/<step>`, `line-height/<step>/default`,
  `line-height/<step>/compressed`, `font-size-display/<step>`; scopes
  `FONT_SIZE` / `LINE_HEIGHT`; `WEB` code syntax `var(--font-size-md)` and so
  on. Values per mode read back as the documented ramp — `font-size/md`
  12 / 14 / 16, `line-height/md/default` 16 / 20 / 24,
  `font-size-display/md` 13.5 / 16 / 18.
- The styles script created 30 text styles — `text/<step>`, `label/<step>` in
  Inter Regular and `display/<step>` in Equinor Regular — each with `fontSize`
  and `lineHeight` **bound** to the variables (`boundVariables` confirmed on
  read-back), and a description carrying the CSS custom properties.
- The font pre-flight passed for both families; nothing was created before it
  ran.
- A second run of the styles script created nothing and updated everything.

## What did not

**The collection's default mode was `compact`.** The script renamed Figma's
first mode to the first density in its list, and `DENSITIES` is ordered
`compact, comfortable, relaxed`. Every text style therefore resolved to the
compact values on any frame without an explicit mode: `text/md` read 12 / 16
instead of 14 / 20. Nothing in the selftest could see it, because the defect is
in what Figma does with the order, not in the order itself. The Plugin API has
no setter for a collection's default mode, so the fix is the order at creation
(#28); after deleting the collection and re-running, `text/md` resolves to
14 / 20, `label/md` to 14 / 16 and `display/md` to 16 / 20 at the default
mode.

**A collection built by the old emitter cannot be repaired by re-running** —
the review of #28 caught that the fix only reached new collections while the
reference promised idempotent re-runs. The script now reads
`col.defaultModeId` on every run and refuses with a message when it is not
`comfortable`; `figma.md` says to delete and re-run.

## Worth noting

- The run took three `use_figma` calls (variables, styles, read-back). The
  scripts are under the size the `figma-use` guidance considers safe, but a
  ten-step scale with two curves and a display ramp is already 40 variables and
  30 styles in one call each; a second family would double the styles.
- Reading back `boundVariables` on a `TextStyle` is what proved binding; a
  screenshot would not have. The next live run should also read
  `col.defaultModeId`, which the script now returns as `defaultMode`.
