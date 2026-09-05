// Typography demo — behaviour. Six controls, three of them gated on another,
// one code panel showing the CSS the last request produced. Nothing here
// computes a typographic value: the numbers were emitted by the skills and
// are quoted, with the request that produced them.

const article = document.getElementById('article');
const codeEl = document.getElementById('code');
const titleEl = document.getElementById('code-title');
const stateEl = document.getElementById('code-state');
const inputs = Object.fromEntries(
  [...document.querySelectorAll('[data-control]')].map((el) => [el.dataset.control, el]),
);
const state = { guides: false, swap: false, xheight: false, weight: false, scale: false, baseline: false };

// Dependencies: a toggle is disabled until what it needs is on.
const needs = { xheight: ['swap'], weight: ['swap'], baseline: ['scale'] };

// The weight the headings are set at, and what typography-weight-matching
// returns for Equinor at that tier. 700 is outside Equinor's axis (300–700):
// the skill reports null and the value is held at the axis maximum.
const matched = { 400: 458.5, 700: null };

const CODE = {
  before: {
    title: 'Before: browser defaults',
    state: 'nothing applied',
    css: `<span class="c">/* No stylesheet beyond the @font-face rules. Body is Inter
   at 16px; the headings are whatever the browser does when
   nobody decides. */</span>
h1 { font-size: 2em;    font-weight: bold; line-height: normal; }
h2 { font-size: 1.5em;  font-weight: bold; line-height: normal; }
h3 { font-size: 1.17em; font-weight: bold; line-height: normal; }`,
  },
  guides: {
    title: 'Show the 4px layout grid',
    state: 'pure CSS, on the surface',
    css: `<span class="c">/* Drawn on the container, inset by its padding, so grid and
   text share an origin. The padding is a multiple of 4. */</span>
.surface::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image: repeating-linear-gradient(
    to bottom, var(--guide) 0, var(--guide) 1px, transparent 1px, transparent 4px);
}`,
  },
  swap: {
    title: 'Set the headings in Equinor',
    state: 'the problem',
    css: `<span class="c">/* The raw font file. No size-adjust, no weight correction:
   the same nominal size and weight as Inter, and it reads
   smaller and thinner. */</span>
@font-face {
  font-family: Equinor;
  src: url(…/EquinorVariable-VF.woff2) format("woff2-variations");
  font-weight: 1 999;
}
h1, h2, h3 { font-family: Equinor; }`,
  },
  xheight: {
    title: 'Align the x-height of Equinor and Inter, Inter is the master',
    state: 'typography-x-height-alignment',
    css: `<span class="c">/* Measured from the two files, not from a spec page:
   Inter   xRatio 0.545898  (sxHeight 1118 / upm 2048) @ wght 400
   Equinor xRatio 0.480000  (sxHeight  480 / upm 1000) @ wght 400
   correction = 0.545898 / 0.48 = <span class="n">1.137288</span> */</span>
<span class="k">"x-height-correction"</span>: { <span class="k">"display"</span>: {
  <span class="k">"$type"</span>: "number", <span class="k">"$value"</span>: <span class="n">1.137288</span>,
  <span class="k">"$extensions"</span>: { <span class="k">"com.equinor.typography"</span>: { <span class="k">"derived"</span>: {
    <span class="k">"expression"</span>: "referenceXRatio / selfXRatio",
    <span class="k">"inputs"</span>: { <span class="k">"referenceXRatio"</span>: <span class="n">0.545898</span>,
                <span class="k">"selfXRatio"</span>: <span class="n">0.48</span> } } } } } }
<span class="c">/* CSS-only target → one ramp, corrected in @font-face */</span>
@font-face {
  font-family: "Equinor Aligned";
  src: url(…/EquinorVariable-VF.woff2) format("woff2-variations");
  size-adjust: <span class="n">113.7288%</span>; <span class="c">/* generated from the token, not typed */</span>
}
<span class="c">/* The motion you saw is a simulation: size-adjust cannot
   animate, so the demo animates a scaled font-size, then
   rests on this face. */</span>`,
  },
  weight: {
    title: 'Equinor looks lighter than Inter at the same weight. What should it be?',
    state: 'typography-weight-matching',
    css: `<span class="c">/* Stem width at the glyph midpoint, from the outlines, at the
   same perceived size (× 1.137288). font-weight is a coordinate;
   this is a measurement. */</span>
<span class="k">"font-weight"</span>: { <span class="k">"Equinor"</span>: {
  <span class="k">"300"</span>: { <span class="k">"$type"</span>: "fontWeight", <span class="k">"$value"</span>: <span class="n">376.2</span> },
  <span class="k">"400"</span>: { <span class="k">"$type"</span>: "fontWeight", <span class="k">"$value"</span>: <span class="n">458.5</span> },
  <span class="k">"500"</span>: { <span class="k">"$type"</span>: "fontWeight", <span class="k">"$value"</span>: <span class="n">552.7</span> } } }
h1, h2, h3 { font-weight: <span class="n">458.5</span>; }  <span class="c">/* Inter 400 → Equinor */</span>`,
    cssClamped: `<span class="c">/* Stem width at the glyph midpoint, from the outlines. The headings are
   at the browser's bold, 700. Inter 700 has a stem of 0.1464em; Equinor's
   axis stops at 700 with 0.1180em, so no weight on its axis matches:
   warning: tier 700 falls outside the target's weight axis (null)
   Held at the axis maximum. Apply the scale first: EDS headings are set at
   the normal tier, 400, where the match is 458.5. */</span>
h1, h2, h3 { font-weight: <span class="n">700</span>; } <span class="c">/* clamped — nothing changes */</span>`,
  },
  scale: {
    title: 'Build a type scale based on the EDS scale',
    state: 'typography-scale · comfortable',
    css: `<span class="c">/* One base, one ratio, one snap. Sizes double every five steps. */</span>
:root { --_base: 1rem; }
--font-size-lg:  var(--_base);                                         <span class="c">/* 16px  */</span>
--font-size-xl:  round(calc(var(--_base) * pow(2, 1/5)), 0.03125rem);  <span class="c">/* 18.5px */</span>
--font-size-2xl: round(calc(var(--_base) * pow(2, 2/5)), 0.03125rem);  <span class="c">/* 21px  */</span>
--font-size-3xl: round(calc(var(--_base) * pow(2, 3/5)), 0.03125rem);  <span class="c">/* 24.5px */</span>
--font-size-5xl: round(calc(var(--_base) * pow(2, 5/5)), 0.03125rem);  <span class="c">/* 32px  */</span>
<span class="c">/* Line-height is a curve indexed by step, snapped to the 4px grid. */</span>
--line-height-lg:  round(calc(var(--font-size-lg)  * (1.39 - pow(3/9, 3) * 0.29)), 4px);  <span class="c">/* 24px */</span>
--line-height-xl:  round(calc(var(--font-size-xl)  * (1.39 - pow(4/9, 3) * 0.29)), 4px);  <span class="c">/* 24px */</span>
--line-height-2xl: round(calc(var(--font-size-2xl) * (1.39 - pow(5/9, 3) * 0.29)), 4px);  <span class="c">/* 28px */</span>
--line-height-3xl: round(calc(var(--font-size-3xl) * (1.39 - pow(6/9, 3) * 0.29)), 4px);  <span class="c">/* 32px */</span>
--line-height-5xl: round(calc(var(--font-size-5xl) * (1.39 - pow(8/9, 3) * 0.29)), 4px);  <span class="c">/* 36px */</span>
p  { font-size: var(--font-size-lg);  line-height: var(--line-height-lg); }
h1 { font-size: var(--font-size-5xl); line-height: var(--line-height-5xl); font-weight: 400; }
h2 { font-size: var(--font-size-3xl); line-height: var(--line-height-3xl); font-weight: 400; }
h3 { font-size: var(--font-size-2xl); line-height: var(--line-height-2xl); font-weight: 400; }
<span class="c">/* Density is one number: [data-density='compact'] { --_base: 0.875rem; } */</span>`,
  },
  baseline: {
    title: 'Align the text to the baseline grid',
    state: 'text in flow snaps, headings included',
    css: `<span class="c">/* Trim the box to x-height and baseline, then pad the top up
   to the cap height rounded to 4px. The block ends on its last
   baseline, the first baseline sits a multiple of 4 from the
   top, and the flow margins are multiples of 4 — so every
   baseline lands on the grid, in both faces. */</span>
:root { --padding-top-baseline: calc(round(1cap, 4px) - 1ex); }
@supports (text-box: trim-both ex alphabetic) {
  :is(h1, h2, h3, p) {
    text-box: trim-both ex alphabetic;
    padding-top: var(--padding-top-baseline);
    padding-bottom: 0;
  }
}
<span class="c">/* 1cap and 1ex are the current font's, so this recomputes when the heading
   face swaps and when its size grows after the x-height correction. */</span>`,
  },
};

function render(key) {
  const entry = CODE[key];
  let css = entry.css;
  if (key === 'weight' && !state.scale) css = entry.cssClamped;
  titleEl.textContent = entry.title;
  stateEl.textContent = entry.state;
  codeEl.innerHTML = `<code>${css}</code>`;
}

function applyWeight() {
  const tier = state.scale ? 400 : 700;
  const value = matched[tier] ?? tier;   // null → held at the axis maximum
  article.style.setProperty('--_h-weight-matched', String(value));
}

function refreshGates() {
  for (const [key, deps] of Object.entries(needs)) {
    const ok = deps.every((d) => state[d]);
    inputs[key].disabled = !ok;
    if (!ok && state[key]) {             // a dependency went off: release the dependant too
      state[key] = false;
      inputs[key].checked = false;
      article.dataset[key] = 'off';
    }
  }
}

function setXHeight(on) {
  if (on) {
    article.dataset.xheight = 'on';      // animates --_xh 1 → 1.137288
    const h = article.querySelector('h1');
    const rest = (e) => {
      if (e.propertyName !== '--_xh') return;
      h.removeEventListener('transitionend', rest);
      if (state.xheight) article.dataset.xheight = 'rest';   // swap to the size-adjusted face; geometrically equal
    };
    h.addEventListener('transitionend', rest);
  } else {
    article.dataset.xheight = 'off';
  }
}

for (const [key, el] of Object.entries(inputs)) {
  el.addEventListener('change', () => {
    state[key] = el.checked;
    if (key === 'xheight') setXHeight(el.checked);
    else article.dataset[key] = el.checked ? 'on' : 'off';
    if (key === 'scale' || key === 'weight') applyWeight();
    refreshGates();
    render(el.checked ? key : 'before');
  });
}
applyWeight();
render('before');

// Deep links for the talk: ?on=swap,scale,xheight,weight,baseline,guides
// applies the controls in that order (dependencies must come first).
const params = new URLSearchParams(location.search);
if (params.has('on')) {
  for (const key of params.get('on').split(',')) {
    const el = inputs[key];
    if (!el || el.disabled) continue;
    el.checked = true;
    el.dispatchEvent(new Event('change'));
  }
}

// ?measure: prove the rest state equals the animated state. Disables the
// transitions, applies swap + x-height, and reports the boxes of every text
// block under the scaled-font-size simulation and under size-adjust.
if (params.has('measure')) {
  document.fonts.ready.then(() => {
    document.querySelectorAll('.surface h1, .surface h2, .surface h3').forEach((h) => (h.style.transition = 'none'));
    const rows = [];
    const snap = (label) => {
      article.querySelectorAll('h1, h2, h3, p').forEach((el, i) => {
        const r = el.getBoundingClientRect();
        rows.push([label, el.tagName + i, r.top.toFixed(2), r.height.toFixed(2), r.width.toFixed(2)].join('\t'));
      });
    };
    for (const k of ['swap', 'scale']) { inputs[k].checked = true; inputs[k].dispatchEvent(new Event('change')); }
    article.dataset.xheight = 'on'; snap('simulation');
    article.dataset.xheight = 'rest'; snap('size-adjust');
    // Baselines: a zero-size inline-block sits on the baseline of the first line.
    // Report its offset from the surface's content edge, modulo 4, with the
    // baseline toggle off and on. On the grid means every remainder is 0.
    const probe = (label) => {
      const top = article.getBoundingClientRect().top + parseFloat(getComputedStyle(article).paddingTop);
      article.querySelectorAll('h1, h2, h3, p').forEach((el, i) => {
        const s = document.createElement('span');
        s.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
        el.prepend(s);
        const b = s.getBoundingClientRect().bottom - top;
        s.remove();
        rows.push([label, el.tagName + i, 'baseline', b.toFixed(2), 'mod4=' + (((b % 4) + 4) % 4).toFixed(2)].join('\t'));
      });
    };
    probe('baseline-off');
    inputs.baseline.checked = true; inputs.baseline.dispatchEvent(new Event('change'));
    probe('baseline-on');
    const pre = document.createElement('pre'); pre.id = 'measure';
    pre.textContent = 'MEASURE\n' + rows.join('\n');
    document.body.append(pre);
  });
}
