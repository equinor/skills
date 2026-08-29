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
  --_bg-hover: var(--color-fill-hover);
  --_fg: var(--color-text-strong);

  color: var(--_fg);
  background-color: var(--_bg); /* the only background-color in the file */
}

.btn--danger {
  --_bg: var(--color-fill-danger);
  --_bg-hover: var(--color-fill-danger-hover);
}

.btn:not(:disabled):hover {
  --_bg: var(--_bg-hover); /* hover is a one-variable diff */
}
```

**A state rule assigns *from* a channel; it never assigns a literal token.**
The state selector always out-specifies the variant — `.btn:not(:disabled):hover`
is `(0,3,0)` against `.btn--danger`'s `(0,1,0)`, because `:not()` takes the
specificity of its argument — so a hover rule that assigned
`var(--color-fill-hover)` directly would flatten every variant it touched. By
assigning `var(--_bg-hover)`, the rule still wins the cascade, but what it
resolves to is a channel each variant owns.

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
  state, not an error: `outline-color: var(--_outline, transparent);`
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
  the stylesheet instead of baking their results. `round()` is Baseline *newly*
  — it needs a fallback under section 3, unlike the rest of this list. Note: `calc()` rejects
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
using a feature you have not verified in this session, check it.

**Find the project's own matrix first.** It overrides every global figure:
`browserslist` in `package.json`, a `.browserslistrc`, or a `targets` field in
the build config. A product with a declared support floor makes "95% global"
both too strict and too lax.

- Canonical machine-readable data, always current:
  `https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/<slug>.json`
  — read `usage_perc_y` (global support %) and `stats` per browser.
  Slugs match caniuse URLs — for the features this skill recommends:
  `css-has`, `css-nesting`, `css-cascade-layers`, `css-focus-visible`,
  `css-logical-props`, `css-matches-pseudo` (`:is()`), `css-math-functions`
  (`min()`/`max()`/`clamp()`).
- Human view: `https://caniuse.com/<slug>` or `https://caniuse.com/?search=<term>`.
- Baseline status, and the fallback when caniuse has no feature at all:
  `https://api.webstatus.dev/v1/features/<id>`, searchable with
  `?q=<term>`. caniuse does not track `:where()` or `round()`; webstatus does,
  as `where` and `round-mod-rem`.

**If the fetch misses, do not fall back on memory** — that is the failure this
section exists to prevent. A guessed slug returns GitHub's 404 page, not JSON.
Only caniuse's own features live under `features-json/`, so an `mdn-*`
identifier always misses, and caniuse's coverage is not exhaustive — newer
features may exist only on webstatus.dev. Search
`https://caniuse.com/?search=<term>`, then
`https://api.webstatus.dev/v1/features?q=<term>`; if both come up empty, say in
your answer that you could not verify rather than asserting from memory.

Rules of thumb:

- Widely available — **Baseline Widely available** governs: use freely.
  `usage_perc_y` is context, not a second gate. The two measure different
  things — Baseline counts ~30 months of interop across a core browser set,
  `usage_perc_y` is market-share weighted and lags it — so a feature can be
  Baseline widely and still sit below 95%. `:has()` (94%) and nesting (91%)
  both do, and both are safe. Treat a low usage figure as a prompt to check
  the project's matrix, not as a veto.
- Newly available — Baseline newly, or not yet Baseline: ship a graceful
  fallback and say so in the commit or PR.
  Pick the fallback mechanism that matches the feature: `@supports selector(…)`
  for selectors (`:has()`, `:where()`, `:focus-visible`), `@supports (prop: val)`
  for properties and values, and a preceding declaration the older engine can
  parse for an unsupported *value* — `var()`'s fallback only covers an unset
  custom property, not a value that failed to parse. Nesting and `@layer` are
  not reliably detectable; author the flat form instead.
- Not interoperable yet: don't build the component's core mechanism on it.

## 4. Specificity discipline

- One class on the component root (`.btn`), element-free selectors inside.
- Variants are modifier classes (`.btn--danger`), not data-attributes —
  reserve attribute selectors for genuine attribute state (ARIA, form state)
  and for ancestor mode scopes (`[data-theme]`-style subtree switches).
- No `#id` selectors, no `!important` — if you need either, the layer order
  or the channel design is wrong; fix that instead.
- Keep specificity flat and let `@layer` decide precedence between concerns.
