---
name: css-authoring
description: Use when writing or reviewing hand-authored CSS — component styles, demos, prototypes. Channel variables (pseudo-private custom properties) for state and variant changes, modern selectors, and verified (never recalled) browser support.
---

# CSS authoring

How to write CSS that stays legible as it grows: every colour, size, and
state change flows through a small set of named channels, selectors say what
they mean, and browser support is checked, not remembered.

## 1. Channel variables — the core pattern

Declare each *channel* a component paints with as a pseudo-private custom
property (prefixed `--_`), declare every CSS **property exactly once**, and
make every variant, size, and state override **the variable, never the
property**.

```css
.btn {
  --_bg: var(--color-fill-default);
  --_fg: var(--color-text-strong);

  color: var(--_fg);
  background-color: var(--_bg); /* the only background-color in the file */
}

.btn--danger {
  --_bg: var(--color-fill-danger);
}

.btn:not(:disabled):hover {
  --_bg: var(--color-fill-hover); /* hover is a one-variable diff */
}
```

Why this wins:

- **A state change is a diff, not a restatement.** Hover changes one value;
  it cannot accidentally change the property, a shorthand, or the cascade.
- **The cascade stays legible.** With one `background-color` declaration
  there is nothing to out-specify; overrides compose instead of competing.
- **Channels are the component's API.** Reading the `--_` block at the top of
  the root rule tells you everything the component can vary.

Conventions:

- `--_` prefix marks the variable as private to the component — set it inside
  the component's rules only, never from outside.
- Optional channels get a fallback at the use site, so absence is a valid
  state, not an error: `outline-color: var(--_border, transparent);`
  `box-shadow: var(--_elevation, none);`
- Size parameters are channels too (`--_font-size`, `--_inset`, `--_gap`):
  a size modifier overrides the parameters; the geometry properties that
  consume them are written once.

## 2. Modern CSS, deliberately

Prefer the modern feature when it says the intent better — and verify support
first (section 3).

- **Nesting** for component-scoped part rules (`& .icon { … }`).
- **`:where()`** to add grouping or hooks at zero specificity — utilities and
  resets that must never win a fight.
- **`:has()`** for real parent/sibling state (`label:has(> input:disabled)`)
  instead of mirroring state onto extra classes with JS.
- **`:not()` with selector lists**: `:not(:disabled, [aria-selected='true'])`
  — one honest guard instead of stacked negations.
- **Logical properties** (`inline-size`, `padding-block`, `margin-inline`)
  unless a physical direction is genuinely meant.
- **`@layer`** to make ordering explicit (`@layer reset, tokens, components`):
  a later layer wins without specificity games.
- **`:focus-visible`**, never bare `:focus`, for focus rings.
- **Math functions** (`calc()`, `round()`, `clamp()`) to keep derivations in
  the stylesheet instead of baking their results. Note: `calc()` rejects
  unitless `0` in addition/subtraction — write `0px` for a semantic zero.

Two traps worth naming:

- **`box-sizing`**: `min-height`/`min-width` resolve against the *content*
  box by default. Buttons get `border-box` from the UA stylesheet; a `<div>`
  with the same padding measures larger. Set `box-sizing: border-box`
  explicitly wherever geometry matters.
- **State selectors**: ARIA states are attributes, not classes — style
  `[aria-selected='true']`, `[aria-expanded='true']` directly, and gate
  interactive states with `:not(:disabled)`.

## 3. Verify support — never recall it

Your knowledge of browser support has a cutoff; the web does not. Before
using a feature you have not verified in this session, check it against the
project's browser matrix:

- Canonical machine-readable data, always current:
  `https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/<slug>.json`
  — read `usage_perc_y` (global support %) and `stats` per browser.
  Slugs match caniuse URLs: `css-has`, `css-nesting`, `css-cascade-layers`,
  `css-when-else`, `mdn-css_types_round`.
- Human view: `https://caniuse.com/<slug>` or `https://caniuse.com/?search=<term>`.
- Baseline status: `https://webstatus.dev/features/<id>`.

Rules of thumb:

- Widely available (Baseline, ≳95% global): use freely.
- Newly available: use with a graceful fallback (`@supports`, or a fallback
  value in the property/`var()`), and say so in the commit or PR.
- Not interoperable yet: don't build the component's core mechanism on it.

## 4. Specificity discipline

- One class on the component root (`.btn`), element-free selectors inside.
- Variants are modifier classes (`.btn--danger`), not data-attributes —
  reserve attribute selectors for genuine attribute state (ARIA, form state)
  and for ancestor mode scopes (`[data-theme]`-style subtree switches).
- No `#id` selectors, no `!important` — if you need either, the layer order
  or the channel design is wrong; fix that instead.
- Keep specificity flat and let `@layer` decide precedence between concerns.
