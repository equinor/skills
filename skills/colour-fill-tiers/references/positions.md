# Positions this skill takes

## 1. Static areas never take fill rungs

The fill tiers are for things you can press; static areas sit on canvas and
surface. **Observed:** a tinted static strip placed on the muted tier landed
on the same step as a ghost button's hover, and the banner's own dismiss
button disappeared against it on hover (measured 2026-08-31). Moving the strip
to `surface` (step 2) fixed it without touching the button, because the whole
interactive ladder sits above surface by construction. The simplification —
"tinted means muted" — costs exactly this collision, and it recurs with every
tinted container.

## 2. Ghost is the default interactive tier

An element that should read as content until touched — an icon button, a menu
row, a tab, a table row — is transparent at rest and gains a step on hover and
active. Making such elements muted by default turns every row into a button
and leaves nothing for the actual button to stand out against; making them
emphasis turns a toolbar into a wall of calls to action. The ghost ladder was
added as its own intent-named tier for this reason, rather than reusing muted.

## 3. Energy Red is refused for primary actions

The brand's signature colour reads as *energetic* in branding and as *danger*
in an interface. Refusing it for the primary action is recorded as a refusal
in the contract-ledger sense: the brand fact is not lost or diluted, it is
deliberately not carried into this context, and the reason is written down.
Red remains available as the `danger` tone, where "danger" is the message.
