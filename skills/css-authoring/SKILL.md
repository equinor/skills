---
name: css-authoring
description: 'Guides hand-authored CSS toward channel variables, modern selectors and verified browser support. USE FOR: writing or reviewing component CSS, styling states and variants, choosing between modern selectors, checking whether a CSS feature is safe to ship, keeping specificity flat. DO NOT USE FOR: generated or compiled CSS output, authoring design tokens, framework styling systems such as Tailwind or CSS-in-JS, choosing the values themselves.'
---

# CSS authoring

How to write CSS that stays legible as it grows: every colour, size, and
state change flows through a small set of named channels, selectors say what
they mean, and browser support is checked, not remembered.

This skill **emits no values**: the sizes, colours and weights come from the
token skills (see Related). This is the shape the CSS that consumes them
takes.

**This skill targets modern, evergreen browsers.** It recommends features on
the basis that they are Baseline available, not that they are universally
supported. Backward compatibility with older browsers is the consuming
project's responsibility — section 3 is how you find out what your own target
actually allows before you write the rule.

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

.btn[data-variant='danger'] {
  --_bg: var(--color-fill-danger);
  --_bg-hover: var(--color-fill-danger-hover);
}

.btn:not(:disabled):hover {
  --_bg: var(--_bg-hover); /* hover is a one-variable diff */
}
```

**A state rule assigns *from* a channel; it never assigns a literal token.**
A hover rule that assigned `var(--color-fill-hover)` directly would flatten
every variant it touched. Assigning `var(--_bg-hover)` instead means what the
rule resolves to is a channel each variant owns.

**State rules come last.** Variant attributes stack, so
`.btn[data-variant='danger'][data-size='small']` is `(0,3,0)` — a tie with
`.btn:not(:disabled):hover` (class and attribute selectors weigh the same, and
`:not()` takes the specificity of its argument) — and a third axis would
out-specify it. Ties resolve by source order, so keep the state rules at the
end of the component's rules, or in a later `@layer`; never rely on the state
selector being heavier.

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
  `[data-size='small']` overrides the parameters; the geometry properties
  that consume them are written once.

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
  the stylesheet instead of baking their results. `round()` landed later than
  the rest of this list; look it up before use (section 3, `round-mod-rem`)
  rather than assume. `calc()` rejects unitless `0` in addition and
  subtraction — write `0px` for a semantic zero.

One trap worth naming: **`box-sizing`**. `min-height`/`min-width` resolve
against the *content* box by default. Buttons get `border-box` from the UA
stylesheet; a `<div>` with the same padding measures larger. Set
`box-sizing: border-box` explicitly wherever geometry matters. (Runtime state
is section 4's third bullet.)

## 3. Verify support — never recall it

Your knowledge of browser support has a cutoff; the web does not. Before
using a feature you have not verified in this session, check it.

**Ask before you emit a rule that leans on a feature's support:**

> Which browsers does this product ship to — is there a `browserslist`?

**Find the project's own matrix first.** It overrides every global figure:
`browserslist` in `package.json`, a `.browserslistrc`, or a `targets` field in
the build config. A product with a declared support floor makes "95% global"
both too strict and too lax.

**If the project declares no matrix, that is the finding.** Say so, and propose
one rather than quietly substituting global usage figures — those answer a
question about the whole web, not about the people who use this product.
`browserslist` is the form to propose: every build tool already reads it, so it
turns a support policy from prose somebody remembers into a value a tool can
check.

```
# .browserslistrc — the browsers this product actually ships to
last 2 versions
not dead
```

- Canonical machine-readable data, always current:
  `https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/<slug>.json`
  — read `usage_perc_y` (global support %) and `stats` per browser.
  Slugs match caniuse URLs — for the features this skill recommends:
  `css-has`, `css-nesting`, `css-cascade-layers`, `css-focus-visible`,
  `css-logical-props`, `css-matches-pseudo` (`:is()`), `css-not-sel-list`
  (`:not()` with a list), `css-math-functions` (`min()`/`max()`/`clamp()`
  only), `calc`. All nine returned JSON on 2026-09-08.
- Human view: `https://caniuse.com/<slug>` or
  `https://caniuse.com/?search=<term>`.
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
  Baseline widely and still sit below 95%. `:has()` and nesting both do, and
  both are safe. Treat a low usage figure as a prompt to check the project's
  matrix, not as a veto.
- Newly available — Baseline newly, or not yet Baseline: the project's matrix
  decides. On a managed, auto-updating fleet a Baseline-newly feature is
  usually fine; where there is a long tail of older browsers, ship a graceful
  fallback and say so in the commit or PR. Not Baseline at all usually means
  one engine: an evergreen target is still two engines, Chromium and WebKit
  (iOS is WebKit in practice), so read the Safari and iOS Safari columns
  before relying on it, and treat Gecko as best-effort — a note and a
  fallback, not a veto.
  Pick the fallback mechanism that matches the feature:
  `@supports selector(…)` for selectors (`:has()`, `:where()`,
  `:focus-visible`), `@supports (prop: val)` for properties and values, and a
  preceding declaration the older engine can parse for an unsupported
  *value* — `var()`'s fallback only covers an unset custom property, not a
  value that failed to parse. Nesting is detectable with
  `@supports selector(&)`; `@layer` is not detectable at all — where either is
  outside the matrix, author the flat form.
- Not interoperable yet: don't build the component's core mechanism on it.

## 4. Selector discipline

- **One class on the component root** (`.btn`); nothing else about the
  component needs a class of its own unless the element is ambiguous.
- **Variants, sizes, and boolean options are `data-*` attributes, never
  modifier classes** — [ADR-0006 rule 3][adr6] (Accepted 2026-06-29; link
  checked 2026-09-08): `.btn[data-variant='danger'][data-size='small']`.
  Name the attribute after the axis, so the markup says *which* axis each
  value belongs to. Let the default value also match the attribute's
  absence (`:is([data-size='md'], :not([data-size]))`), so resting markup
  stays bare. Booleans are valueless presence attributes (`data-readonly`),
  exactly like the platform's own `disabled`.
- **Attributes carry design-time configuration; pseudo-classes and ARIA
  carry runtime state.** Style `:hover`, `:disabled`, `[aria-selected='true']`,
  `[aria-pressed='true']` directly — never mirror them into `data-*`. (The
  same split the headless libraries expose: Radix's [styling guide][radix]
  says "when components are stateful, their state will be exposed in a
  `data-state` attribute" — state the *element* computes; the variants an
  *author* chooses are a different kind of information.)
- **Semantic descendants are targeted by element, scoped with `>`**
  (`& > details > summary`, `& > :is(input, select, textarea)`, `& th, & td`)
  so consumer content inside the component can never collide. Inner classes
  only where the element alone is ambiguous (two icon slots).
- Ancestor mode scopes (`[data-theme]`/`[data-density]`-style subtree
  switches) belong to the token layer, not to components — a component
  selector should never mention them.
- No `#id` selectors, no `!important` — if you need either, the layer order
  or the channel design is wrong; fix that instead.
- Keep specificity flat (class and attribute both weigh `(0,1,0)`) and let
  `@layer` decide precedence between concerns.

A note on lint configs: `stylelint-config-standard` accepts all of the above
as-is. A `selector-class-pattern` that demands BEM (`block__element--modifier`)
contradicts ADR-0006 — do not copy one from an older repo without checking
what it enforces.

[adr6]: https://github.com/equinor/design-system/blob/main/documentation/adr/0006-flat-class-names-for-eds-2-components.md
[radix]: https://www.radix-ui.com/primitives/docs/guides/styling

## Representative requests

Four acceptance criteria — the button with variants and a hover, the review
of committed component CSS, "can I use `:has()` here", and adding a size —
plus a routing check:
[`references/representative-requests.md`](references/representative-requests.md).

## Positions this skill takes

Five, each with what backs it: channels over restated properties, state rules
last rather than heavier, `data-*` for configuration and the platform for
state, support verified live with Baseline governing, and the matrix in a
`browserslist` rather than in prose:
[`references/positions.md`](references/positions.md).

## Related

- **`typography-scale`**, **`spacing-ladder`**, **`colour-fill-tiers`** — where
  the values a channel is set to come from: the size and line-height, the
  inset and padding, the fill rung. This skill says how the CSS that consumes
  them is shaped, not what they are.
- **`typography-weight-matching`** — its matched weights and letter-spacing
  are channel values too (`--_weight`, `--_tracking`).

## Provenance

The channel-variable pattern and the selector rules are the ones the EDS
component emitter in `equinor/ids-meetup-oslo-26` (Equinor-internal) enforces
on every generated stylesheet and checks in its harness; this skill is how
they travel to CSS written by hand. `data-*` over modifier classes is
ADR-0006 in `equinor/design-system` (MIT, public). The support-verification
endpoints are caniuse's `features-json` and webstatus.dev, both checked live
on 2026-09-08.
