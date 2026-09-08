// Overlay demo — behaviour. Every snap value below was measured by the skills
// from the font files (6–7 September 2026); INTENT.md records the commands.

// x-height ratios (OS/2.sxHeight / unitsPerEm, confirmed against the outlines of
// x v w z). Flat along wght for all three faces; Inter's opsz axis lowers it, so
// Inter carries one ratio per optical size the browser can render — 14 up to 32,
// where the axis clamps. typography-x-height-alignment.
const X = { inter: { 14: 0.545898, 32: 0.515625 }, equinor: 0.48, barlow: 0.506 };
// Matched Equinor weight for a reference tier, by the opsz the browser gives Inter
// at the rendered px (Barlow and Equinor have no optical axis). Stems compared at
// the same perceived size, i.e. with that size's x-height correction applied.
// typography-weight-matching. The target is always Equinor.
const MATCH = {
  inter:   { 400: { 14: 458.5, 32: 458.4 }, 500: { 14: 552.7, 32: 563.1 }, 600: { 14: 660.0, 32: 680.7 } },
  barlow:  { 400: { 14: 411.4, 32: 411.4 }, 500: { 14: 531.7, 32: 531.7 }, 600: { 14: 650.3, 32: 650.3 } },
};
const FAMILY = { inter: 'Inter', equinor: 'Equinor', barlow: 'Barlow' };
const TARGET = 'equinor', TARGET_AXIS = [300, 700];          // the adjusted face is always Equinor
const SIZE_RANGE = [0.85, 1.25], SIZE_TOL = 0.004, WEIGHT_TOL = 2.5;

const $ = (id) => document.getElementById(id);
const overlay = $('overlay'), pair = $('pair'), refEl = $('ref'), targetEl = $('target');
const size = $('size'), weight = $('weight');
// rawScale / rawWeight are the slider positions; scale / weight are what is applied.
// The detent snaps the applied value only, so arrow keys can still leave it.
const state = { ref: 'inter', px: 14, tier: 400, rawScale: 1, rawWeight: 400, scale: 1, weight: 400, snappedSize: false, snappedWeight: false };

const opszKey = () => (state.px >= 32 ? 32 : 14);
const xr = (face) => (typeof X[face] === 'number' ? X[face] : X[face][opszKey()]);
const correction = () => xr(state.ref) / xr(TARGET);
const matched = () => (MATCH[state.ref][state.tier] || {})[opszKey()];
const hasOpsz = () => state.ref !== 'barlow';                 // Inter is in the pair
const opszNote = () => (hasOpsz() ? `Inter @ opsz ${opszKey()}` : 'any size');

function fmt(n, d = 6) { return Number.isInteger(n) ? String(n) : n.toFixed(d).replace(/\.?0+$/, ''); }
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

function snap(value, target, tolerance) {
  return target != null && Math.abs(value - target) <= tolerance ? target : value;
}

function render() {
  const t = TARGET;
  const [lo, hi] = TARGET_AXIS;
  weight.min = lo; weight.max = hi;

  const corr = correction();
  const m = matched();
  state.rawScale = clamp(state.rawScale, ...SIZE_RANGE);
  state.rawWeight = clamp(state.rawWeight, lo, hi);
  state.scale = snap(state.rawScale, corr, SIZE_TOL);
  state.weight = snap(state.rawWeight, m, WEIGHT_TOL);
  state.snappedSize = state.scale === corr;
  state.snappedWeight = m != null && state.weight === m;
  // the sliders keep their raw position; only a clamp (axis change) moves them
  if (Number(size.value) !== state.rawScale) size.value = state.rawScale;
  if (Number(weight.value) !== state.rawWeight) weight.value = state.rawWeight;
  size.classList.toggle('snapped', state.snappedSize);
  weight.classList.toggle('snapped', state.snappedWeight);

  // the pair renders at the real px so opsz is honest, then is scaled up to be seen
  pair.style.fontSize = `${state.px}px`;
  pair.style.setProperty('--_ref-family', FAMILY[state.ref]);
  pair.style.setProperty('--_target-family', FAMILY[t]);
  pair.style.setProperty('--_weight', state.tier);
  pair.style.setProperty('--_scale', state.scale);
  pair.style.setProperty('--_target-weight', state.weight);
  pair.style.setProperty('--_x-ref', `${xr(state.ref)}em`);
  pair.style.setProperty('--_x-target', `${xr(t) * state.scale}em`);
  requestAnimationFrame(() => {
    // The frame is sized from the reference alone, at the widest the slider can
    // make the target, so the reference stays put while the size slider moves.
    // No lower bound: a narrow viewport scales the pair down instead of clipping.
    const avail = overlay.clientWidth - 2 * 24 - 40;
    const prev = Number(pair.dataset.zoom) || 1;
    const w = (refEl.getBoundingClientRect().width / prev) * SIZE_RANGE[1];
    const h = pair.getBoundingClientRect().height / prev;
    const zoom = Math.min(avail / w, 14);
    pair.dataset.zoom = zoom;
    pair.style.transform = `scale(${zoom})`;
    pair.style.marginTop = `${(zoom - 1) * h}px`;          // room for the scaled glyphs above the baseline
    pair.style.marginLeft = `${Math.max(0, (overlay.clientWidth - 48 - w * zoom) / 2)}px`;
    $('scale-note').textContent = `Rendered at ${state.px}px — what the optical-size axis sees — and shown ${zoom.toFixed(1)}× larger. Reference ${FAMILY[state.ref]} ${state.tier}; ${FAMILY[t]} at ${fmt(state.scale, 3)}× the size, weight ${fmt(state.weight, 1)}.`;
  });

  $('key-ref').textContent = `${FAMILY[state.ref]} — reference, stays put`;
  $('key-target').textContent = `${FAMILY[t]} — adjusted by the sliders`;
  $('size-label').textContent = `Size of ${FAMILY[t]}`;
  $('weight-label').textContent = `Weight of ${FAMILY[t]}`;
  $('size-out').textContent = `× ${fmt(state.scale, 3)}`;
  $('weight-out').textContent = fmt(state.weight, 1);
  $('size-snap').innerHTML = `snaps at <b>× ${fmt(corr)}</b> = ${fmt(xr(state.ref))} / ${fmt(xr(t))} (${opszNote()})`;
  $('weight-snap').innerHTML = m != null ? `snaps at <b>${fmt(m, 1)}</b> for ${FAMILY[state.ref]} ${state.tier} (${opszNote()})` : 'no measured match for this pairing';

  const instance = hasOpsz() ? `wght 400, Inter opsz ${opszKey()}` : 'wght 400';
  const rows = [
    ['x-height', `${FAMILY[state.ref]} ${fmt(xr(state.ref))} · ${FAMILY[t]} ${fmt(xr(t))} — OS/2.sxHeight / unitsPerEm at ${instance}, read from the files; flat along wght for Inter and Equinor and within 1% for Barlow, so one ratio serves every tier`],
    ['correction', `${fmt(xr(state.ref))} / ${fmt(xr(t))} = <b>× ${fmt(corr)}</b> — size the ${FAMILY[t]} text by this and the x-heights coincide${state.snappedSize ? ' ✓' : ''}`],
    ['stem match', m != null
      ? `${FAMILY[state.ref]} ${state.tier} → ${FAMILY[t]} <b>${fmt(m, 1)}</b> (${opszNote()}), measured at the glyph midpoint at the same perceived size${state.snappedWeight ? ' ✓' : ''}`
      : `not measured for this pairing`],
    ['why it moves', state.ref === 'inter'
      ? `Inter's opsz axis lowers its x-height (${fmt(X.inter[14])} → ${fmt(X.inter[32])}) and thins its stems above 14px. The correction falls from × ${fmt(X.inter[14] / X.equinor)} to × ${fmt(X.inter[32] / X.equinor)}, so Equinor is set smaller at 32px: the match goes ${MATCH.inter[state.tier][14]} → ${MATCH.inter[state.tier][32]} between 14px and 32px${MATCH.inter[state.tier][32] > MATCH.inter[state.tier][14] + 1 ? ', so it needs more weight to keep up' : ' — the thinner stem and the smaller size cancel'}`
      : `Barlow has no optical axis, so one match holds at every size. Equinor 500 (stem 0.086em) sits below Barlow Medium (0.096em); Inter 500 (0.107em) sits above it — Equinor needs 531.7 and Inter only 480.4 to match Barlow Medium, measured here from the outlines`],
  ];
  if (state.ref === 'barlow') {
    rows.push(['about Barlow', `The Lc contrast number is colour math with no font in it. The lookup table that turns an Lc target into a minimum size and weight — shipped in apca-w3 (src/apca-w3.js, data/LUT-GseriesMay28-2022.js) — says in its source: "reference font is Barlow". By APCA's own x-height-ratio method, 14px Barlow (x-height 7.08px) is 13px Inter. Its docs call weight matching "ongoing research"; the weight slider is a measured answer.`]);
  }
  $('readout').innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
}

document.querySelectorAll('input[name="ref"]').forEach((r) => r.addEventListener('change', () => { state.ref = r.value; render(); }));
document.querySelectorAll('input[name="px"]').forEach((r) => r.addEventListener('change', () => { state.px = Number(r.value); render(); }));
document.querySelectorAll('input[name="tier"]').forEach((r) => r.addEventListener('change', () => { state.tier = Number(r.value); render(); }));
size.addEventListener('input', () => { state.rawScale = Number(size.value); render(); });
weight.addEventListener('input', () => { state.rawWeight = Number(weight.value); render(); });
$('guides').addEventListener('change', (e) => { overlay.dataset.guides = e.target.checked ? 'on' : 'off'; });
// one face at a time: the key entries are checkboxes; a hidden face keeps its box
$('show-ref').addEventListener('change', (e) => { overlay.dataset.showRef = e.target.checked ? 'on' : 'off'; });
$('show-target').addEventListener('change', (e) => { overlay.dataset.showTarget = e.target.checked ? 'on' : 'off'; });
window.addEventListener('resize', render);

// Deep links: ?ref=inter&px=14&tier=400&size=1.137288&weight=458.5 (or size=snap&weight=snap)
// &show=ref | target shows one face alone; &guides=off hides the guides
const q = new URLSearchParams(location.search);
const num = (v) => (v != null && v !== '' && Number.isFinite(Number(v)) ? Number(v) : null);
if (MATCH[q.get('ref')]) { state.ref = q.get('ref'); document.querySelector(`input[name="ref"][value="${state.ref}"]`).checked = true; }
if ([14, 32, 48].includes(Number(q.get('px')))) { state.px = Number(q.get('px')); document.querySelector(`input[name="px"][value="${state.px}"]`).checked = true; }
if ([400, 500, 600].includes(Number(q.get('tier')))) { state.tier = Number(q.get('tier')); document.querySelector(`input[name="tier"][value="${state.tier}"]`).checked = true; }
if (q.get('size') === 'snap') state.rawScale = correction();
else if (num(q.get('size')) != null) state.rawScale = clamp(num(q.get('size')), ...SIZE_RANGE);
if (q.get('weight') === 'snap') state.rawWeight = matched() ?? state.rawWeight;
else if (num(q.get('weight')) != null) state.rawWeight = clamp(num(q.get('weight')), ...TARGET_AXIS);
size.value = state.rawScale; weight.value = state.rawWeight;
if (['ref', 'target'].includes(q.get('show'))) {
  const other = q.get('show') === 'ref' ? 'target' : 'ref';
  $(`show-${other}`).checked = false; $(`show-${other}`).dispatchEvent(new Event('change'));
}
if (q.get('guides') === 'off') { $('guides').checked = false; $('guides').dispatchEvent(new Event('change')); }
// Barlow is the one face not served from the EDS CDN. If Google Fonts is blocked
// the reference would render in a fallback while the readout still quoted Barlow's
// numbers, so say so instead — the same treatment as the text-box notice.
const fontWarn = document.createElement('p');
fontWarn.className = 'overlay__warn'; fontWarn.hidden = true;
fontWarn.textContent = 'Barlow did not load from Google Fonts. The reference below is a fallback face, and the numbers in the readout do not describe it.';
pair.before(fontWarn);
function checkFonts() { fontWarn.hidden = !(state.ref === 'barlow' && !document.fonts.check(`${state.tier} ${state.px}px Barlow`)); }
document.querySelectorAll('input[name="ref"], input[name="tier"], input[name="px"]').forEach((r) => r.addEventListener('change', () => document.fonts.ready.then(checkFonts)));
document.fonts.ready.then(() => { render(); checkFonts(); });
render();
