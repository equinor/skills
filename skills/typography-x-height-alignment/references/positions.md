# Positions

## Never let platforms disagree about a value; do let them differ in fidelity

This skill says to bake the x-height correction into font-size tokens rather
than ship `size-adjust`, because Figma and React Native never see a CSS
`@font-face` descriptor. Read carelessly, that sounds like a general rule that
the least capable platform decides what everyone gets. It is not, and the
distinction is worth stating because the same question comes up for text-box
trimming, `@supports` features, and anything else CSS can do that other runtimes
cannot.

The line is between a **value** and a **capability**.

**A value must be the same everywhere.** `size-adjust` is a multiplier applied
in one platform and invisible to the others, so CSS, Figma and React Native end
up disagreeing about what `md` *is*. A designer says the header is 16px, a
developer finds 14px, and reconciling them requires knowing an invisible
descriptor exists. That is drift, and drift is a correctness problem: the
platforms are describing the same token differently. Fix it by moving the number
somewhere all three can read.

**A capability may differ.** Text-box trimming lets CSS sit text precisely on a
grid. React Native cannot do it. Nothing about the token values disagrees — both
platforms use the same sizes and the same line-heights, and one renders them
with a refinement the other lacks. That is graceful degradation, and it is the
normal condition of building for more than one runtime.

Removing a capability from the platform that has it does not make the platforms
agree. It makes them equally worse, and it gives up the thing the more capable
platform was chosen for. The web is not improved by rendering as though it were
React Native, any more than a variable font is improved by shipping only its
default instance.

So, when a platform cannot do something:

- **If it changes what a token means** — bake it, move it, or otherwise make the
  value legible to every target. Never leave one platform silently transforming
  a shared number.
- **If it only changes how well a token renders** — let it differ, and say so.
  Record which platforms get the refinement, so the difference is a documented
  choice rather than a bug someone finds later.

The test is a single question: *after this change, do the platforms disagree
about a value?* If yes, that is drift and must be fixed at the source. If no, it
is fidelity, and levelling it down buys nothing.
