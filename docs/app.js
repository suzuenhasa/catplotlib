'use strict';

const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => [...root.querySelectorAll(s)];
const NS = 'http://www.w3.org/2000/svg';
const palettes = [
  { name: 'Milk tea', colours: ['#b49ad2', '#81b4cf', '#a8bb86', '#ef9dac', '#f0ba72'], ink: '#9876b8' },
  { name: 'Strawberry', colours: ['#e88cac', '#f5b4bd', '#c8a2d6', '#efa27d', '#adc7aa'], ink: '#d379a0' },
  { name: 'Blueberry', colours: ['#8d9bd2', '#9cc6d6', '#b2a2d5', '#8bbdb4', '#e0c0d6'], ink: '#7b87bd' },
  { name: 'Matcha', colours: ['#9eaf7e', '#c3cba1', '#ddb781', '#89b9a7', '#c5a7bb'], ink: '#7f985e' }
];
const cats = [
  { name: 'Mochi', coat: '#a4a19d', shade: '#73716e', muzzle: '#fff8e8', description: 'Senior nap analyst. Strong opinions on boxes.' },
  { name: 'Beans', coat: '#55515b', shade: '#34313a', muzzle: '#eeece4', description: 'Tiny void. Unreasonably large zoomies.' },
  { name: 'Nugget', coat: '#f0bc6d', shade: '#d7924e', muzzle: '#fff1ca', description: 'Head of treats. Zero thoughts, excellent vibes.' },
  { name: 'Tofu', coat: '#fffaf0', shade: '#e3d5c8', muzzle: '#fffaf0', description: 'Soft as a cloud. Secretly in charge of everything.' }
];
const defaults = {
  line: [2, 3.7, 6.4, 5.2, 8.8, 9.8],
  bar: [16, 7, 15, 11],
  scatter: [[1, 6.8], [1.8, 1.9], [2.4, 4.7], [3, 8.6], [4, 6.9], [4.1, 2.7], [5.6, 5.3], [6.7, 3.8], [7.8, 6]],
  pie: [30, 25, 20, 15, 10], bins: 8, warmth: 50
};
const state = { ...structuredClone(defaults), palette: 0, marker: 'cats', cuteness: 65, grid: true, treats: 0, view: 'playground', cat: 0, mood: 'happy', blush: true, scarf: true, code: 'python', activeChart: null };
const specs = [
  { id: 'line', method: 'plot()', title: 'The mood throughout the day', label: 'Mood over naps', hint: 'Drag a cat. Change the mood.', colour: 0 },
  { id: 'bar', method: 'bar()', title: 'Hard work. Well-earned snacks.', label: 'Treats earned', hint: 'Every good cat deserves a treat.', colour: 1 },
  { id: 'scatter', method: 'scatter()', title: 'A very scientific study of zoomies', label: 'Chaos vs. zoomies', hint: 'Grab a paw. Cause a little chaos.', colour: 2 },
  { id: 'pie', method: 'pie()', title: 'A full schedule of doing absolutely nothing', label: 'A day in the life', hint: 'A balanced diet of naps and naps.', colour: 4 },
  { id: 'hist', method: 'hist()', title: 'If I fits, I sits. The distribution.', label: 'The perfect box', hint: 'Some very important box research.', colour: 0 },
  { id: 'heat', method: 'imshow()', title: 'The temperature of a happy little cat', label: 'Maximum coziness', hint: 'Warning: extremely warm and fuzzy.', colour: 1 }
];
let uid = 0;
let toastTimer;
let drag = null;
const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const colours = () => palettes[state.palette].colours;

function catArt(index = 0, options = {}) {
  const c = cats[index % cats.length];
  const mood = options.mood || 'happy';
  const blush = options.blush !== false;
  const full = options.full || false;
  const scarf = options.scarf || false;
  const stroke = '#49423f';
  let eyes = mood === 'sleepy'
    ? '<path d="M29 50q5 5 10 0m23 0q5 5 10 0" fill="none" stroke-width="2.6"/>'
    : mood === 'surprised'
      ? '<ellipse cx="34" cy="50" rx="4.2" ry="6"/><ellipse cx="67" cy="50" rx="4.2" ry="6"/><circle cx="35" cy="48" r="1.3" fill="#fff" stroke="none"/><circle cx="68" cy="48" r="1.3" fill="#fff" stroke="none"/>'
      : '<g class="cat-eyes"><path d="M30 51q4-6 8 0m25 0q4-6 8 0" fill="none" stroke-width="3"/></g>';
  const mouth = mood === 'surprised'
    ? '<ellipse cx="50" cy="68" rx="3.1" ry="4.3" fill="#b97578" stroke-width="1.7"/>'
    : `<path d="M50 61v4m0-1q-4 7-9 1m9-1q4 7 9 1" fill="none" stroke-width="2.1"/>${mood === 'happy' ? '<path d="M46 70q4 8 8 0" fill="#e79698" stroke-width="1.5"/>' : ''}`;
  const stripes = index === 3 ? '' : '<path d="m39 24 4 9m7-11 1 10m10-8-3 9M18 46l9 3m-10 7 8 1m49-8 9-3m-8 12 9-2" fill="none" stroke="' + c.shade + '" stroke-width="4.5" opacity=".8"/>';
  let head = `<g class="cat-face" fill="${c.coat}" stroke="${stroke}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
    <path d="M15 39 16 11q1-6 6-2l18 16q11-4 22 0L80 10q5-4 6 3l1 28q7 12 4 23-5 20-39 21Q20 86 11 69q-8-14 4-30Z"/>
    <path d="m21 31 1-16 12 12m34 1 12-12 1 17" fill="#e9a8a0" stroke="${c.shade}" stroke-width="1.4"/>
    <path d="M27 72q4-9 13-14l10-10 9 10q11 3 17 15-7 10-25 10-17 0-24-11" fill="${c.muzzle}" stroke="none"/>
    ${stripes}<g fill="${stroke}" stroke="${stroke}">${eyes}</g>
    ${blush ? '<ellipse cx="24" cy="61" rx="6.5" ry="4" fill="#ed9b9a" stroke="none" opacity=".74"/><ellipse cx="77" cy="61" rx="6.5" ry="4" fill="#ed9b9a" stroke="none" opacity=".74"/>' : ''}
    <path d="M46 58q4-2 8 0l-4 4Z" fill="#bb7a7a" stroke-width="1"/>${mouth}
    <path d="m18 61-13-3m13 9L4 68m78-7 13-3m-13 9 14 1" fill="none" stroke-width="1.7"/>
  </g>`;
  if (!full) return head;
  return `<g stroke="${stroke}" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
    <ellipse cx="75" cy="145" rx="57" ry="6" fill="#d9ccb9" stroke="none" opacity=".48"/>
    <path class="cat-tail" d="M97 131q37 15 35-13-1-10 5-10 13 2 6 25-8 24-47 8" fill="${c.coat}"/>
    <path d="M57 69q-24 22-25 57-2 18 22 19h48q22-1 17-19-7-34-29-52" fill="${c.coat}"/>
    <path d="M61 85q-15 17-10 45 1 12 23 13 27-2 27-15-1-25-17-44" fill="${c.muzzle}" stroke="none"/>
    ${index !== 3 ? `<path d="m38 108 10 3m-12 8 10 3m56-20-9 6m14 5-10 5m13 5-11 3" stroke="${c.shade}" stroke-width="5"/>` : ''}
    <path d="M57 112q-2 11-1 22m25-22 3 22" fill="none"/>
    <path d="M53 130q-16-1-17 8-1 10 19 7 9-2 9-7-1-7-11-8m35 0q-14 0-14 8-1 10 18 7 9-2 9-7-1-7-13-8" fill="${c.coat}"/>
    <path d="M45 139v5m6-5v6m33-6v6m6-6v5" fill="none" stroke-width="1.4"/>
    <g transform="translate(21 0) scale(1.04)">${head}</g>
    ${scarf ? '<path d="M52 84q19 9 39 0l-11 14-8-8-12 13-5-17Z" fill="' + colours()[0] + '" stroke-width="1.7"/>' : ''}
    ${mood === 'sleepy' ? '<g stroke="none"><text class="cat-sleep-z" x="119" y="48">z</text><text class="cat-sleep-z" x="130" y="32">z</text></g>' : ''}
  </g>`;
}
function catSVG(index = 0, options = {}) { return `<svg xmlns="${NS}" viewBox="${options.full ? '0 0 155 155' : '0 0 100 94'}" role="img" aria-label="${cats[index].name}, a ${options.mood || 'happy'} cat">${catArt(index, options)}</svg>`; }
function pawArt(colour) { return `<g fill="${colour}"><ellipse cx="9" cy="13" rx="4" ry="5.4" transform="rotate(-25 9 13)"/><ellipse cx="17" cy="7" rx="4" ry="5.4" transform="rotate(-10 17 7)"/><ellipse cx="26" cy="8" rx="4" ry="5.4" transform="rotate(12 26 8)"/><ellipse cx="33" cy="15" rx="4" ry="5.4" transform="rotate(26 33 15)"/><path d="M13 23q7-13 14 0c2 3 7 8 2 11-4 3-6-1-9-1s-5 3-9 0c-5-3-1-7 2-10Z"/></g>`; }
function pawSVG(c) { return `<svg xmlns="${NS}" viewBox="0 0 42 40" aria-hidden="true">${pawArt(c)}</svg>`; }
const expandIcon = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M7 3H3v4m10-4h4v4M3 13v4h4m10-4v4h-4m-7-3 8-8"/></svg>';
const editIcon = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m4 13-1 4 4-1L17 6l-3-3ZM12 5l3 3"/></svg>';

function grid(maxY = 10, maxX = 5, xLabel = '', yLabel = '', xNames) {
  let s = '';
  for (let i = 0; i <= 5; i++) {
    let y = 209 - i * 34;
    if (state.grid && i) s += `<path class="grid-line" d="M46 ${y}H352" fill="none"/>`;
    s += `<text x="36" y="${y + 4}" text-anchor="end">${Math.round(maxY * i / 5 * 10) / 10}</text>`;
  }
  if (xNames) xNames.forEach((name, i) => { s += `<text x="${(xNames.length === 4 ? 66 : 52) + i * ((xNames.length === 4 ? 270 : 295) / Math.max(1, xNames.length - 1))}" y="228" text-anchor="middle">${esc(name)}</text>`; });
  else for (let i = 0; i <= 5; i++) s += `<text x="${52 + i * 59}" y="228" text-anchor="middle">${maxX * i / 5}</text>`;
  return s + `<path class="axis-line" d="M46 28V210H359" fill="none"/><text class="axis-label" x="202" y="249" text-anchor="middle">${xLabel}</text><text class="axis-label" transform="translate(13 124) rotate(-90)" text-anchor="middle">${yLabel}</text>`;
}
function marker(x, y, index, type = state.marker, size) {
  const s = size || 24 + state.cuteness * .2;
  if (type === 'dots') return `<circle cx="${x}" cy="${y}" r="6" fill="${colours()[index % 5]}" stroke="#fffdf6" stroke-width="2.5"/>`;
  if (type === 'paws') return `<g transform="translate(${x - s / 2} ${y - s / 2}) scale(${s / 42}) rotate(${(index % 3 - 1) * 12} 21 20)">${pawArt(colours()[index % 5])}</g>`;
  return `<g class="cat-marker" transform="translate(${x - s / 2} ${y - s * .51}) scale(${s / 100})">${catArt(index % 4, { mood: index % 4 === 1 ? 'sleepy' : 'happy' })}</g>`;
}
function point(id, i, x, y, label, contents, draggable = true) {
  return `<g class="data-point" data-chart="${id}" data-index="${i}" data-draggable="${draggable}" data-tip="${esc(label)}" tabindex="0" role="${draggable ? 'slider' : 'img'}" aria-label="${esc(label)}" ${draggable ? `aria-valuemin="0" aria-valuemax="${id === 'bar' ? 20 : 10}" aria-valuenow="${id === 'scatter' ? state.scatter[i][1] : state[id][i]}"` : ''}>
    <circle class="focus-ring" cx="${x}" cy="${y}" r="23" fill="transparent" stroke="none"/>${contents}</g>`;
}
function lineChart() {
  const points = state.line.map((v, i) => [52 + i * 59, 209 - v * 17]);
  const path = points.map((p, i) => (i ? 'L' : 'M') + p.join(' ')).join(' ');
  return grid(10, 5, 'time (naps)', 'mood (purrs)') + `<path d="${path}L347 209H52Z" fill="${colours()[0]}" opacity=".09"/><path class="data-line" d="${path}" fill="none" stroke="${palettes[state.palette].ink}" stroke-width="2.8"/>` + points.map(([x, y], i) => point('line', i, x, y, `Nap ${i}: ${state.line[i].toFixed(1)} purrs`, marker(x, y, [0, 2, 3, 0, 3, 2][i]))).join('') + (state.cuteness > 40 ? `<path d="m302 122 3-9 3 9 8 3-8 3-3 9-3-9-8-3Z" fill="${colours()[0]}" opacity=".65"/><path d="m84 77 2-7 2 7 6 2-6 2-2 7-2-7-6-2Z" fill="${colours()[0]}" opacity=".4"/>` : '');
}
function barChart() {
  let s = grid(20, 3, 'cat squad', 'treats earned', cats.map(c => c.name));
  state.bar.forEach((value, i) => {
    const x = 66 + i * 90, y = 209 - value * 8.5;
    const rect = `<rect x="${x - 24}" y="${y}" width="48" height="${209 - y}" rx="3" fill="${colours()[i]}" fill-opacity=".82" stroke="${colours()[i]}" stroke-width="1.6"/><path d="M${x - 20} ${y + 4}V205" stroke="#fff" stroke-width="2" opacity=".25"/>`;
    const paws = state.marker === 'cats' ? `<g fill="${cats[i].coat}" stroke="#49423f" stroke-width="1"><ellipse cx="${x - 10}" cy="${y + 1}" rx="4.5" ry="3.3"/><ellipse cx="${x + 10}" cy="${y + 1}" rx="4.5" ry="3.3"/></g>` : '';
    s += point('bar', i, x, y - 13, `${cats[i].name}: ${value} treats`, rect + marker(x, y - 12, i) + paws);
  });
  return s;
}
function scatterChart() {
  return grid(10, 10, 'chaos level', 'zoomies') + state.scatter.map(([vx, vy], i) => {
    const x = 52 + vx * 29.5, y = 209 - vy * 17;
    return point('scatter', i, x, y, `Chaos ${vx.toFixed(1)} · zoomies ${vy.toFixed(1)}`, marker(x, y, i, state.marker === 'cats' ? 'paws' : state.marker, 21 + state.cuteness * .13));
  }).join('') + (state.cuteness > 35 ? `<g transform="translate(286 161) scale(.57) rotate(-13 50 50)">${catArt(0)}</g><path d="M288 210h64" stroke="#9c9284" stroke-width="1.5"/><g transform="translate(241 32)"><path d="M0 8Q0 0 12 0H84Q94 0 94 11v28q0 10-13 10H22l-9 9 1-10Q0 50 0 37Z" fill="#fcf2d8" stroke="#d4c39d" stroke-width="1.2"/><text x="47" y="20" text-anchor="middle" style="font-family:var(--hand);font-size:12px;fill:#8b7750">more chaos,</text><text x="47" y="37" text-anchor="middle" style="font-family:var(--hand);font-size:12px;fill:#8b7750">more zoomies!</text></g>` : '');
}
const pieLabels = ['sleep', 'eat', 'knock stuff over', 'zoom', 'cuddle'];
function pieChart() {
  let start = -Math.PI / 2, total = state.pie.reduce((a, b) => a + b, 0), s = '';
  const exact = state.pie.map(v => v / total * 100), percentages = exact.map(Math.floor);
  const remainders = exact.map((v, i) => ({ i, remainder: v - percentages[i] })).sort((a, b) => b.remainder - a.remainder);
  for (let i = 0, left = 100 - percentages.reduce((a, b) => a + b, 0); i < left; i++) percentages[remainders[i].i]++;
  const cx = 132, cy = 126, r = 87;
  state.pie.forEach((v, i) => {
    const end = start + v / total * Math.PI * 2, mid = (start + end) / 2;
    const x = a => cx + r * Math.cos(a), y = a => cy + r * Math.sin(a);
    const percent = percentages[i];
    const sector = `<path d="M${cx} ${cy}L${x(start)} ${y(start)}A${r} ${r} 0 ${end - start > Math.PI ? 1 : 0} 1 ${x(end)} ${y(end)}Z" fill="${colours()[[0, 4, 2, 1, 3][i]]}" stroke="#fffaf0" stroke-width="1.7"/>`;
    const mx = cx + r * .64 * Math.cos(mid), my = cy + r * .64 * Math.sin(mid);
    s += point('pie', i, mx, my, `${pieLabels[i]}: ${percent}%`, sector + marker(mx, my, [0, 2, 0, 1, 3][i], state.marker, 29 + state.cuteness * .06), false);
    s += `<text x="${cx + (r + 18) * Math.cos(mid)}" y="${cy + (r + 18) * Math.sin(mid) + 4}" text-anchor="middle" style="font-size:12px;fill:#686051">${percent}%</text>`;
    const name = pieLabels[i] === 'knock stuff over' ? '<tspan x="267" dy="0">knock stuff</tspan><tspan x="267" dy="14">over</tspan>' : pieLabels[i];
    s += `<rect x="246" y="${49 + i * 35}" width="11" height="11" rx="2" fill="${colours()[[0, 4, 2, 1, 3][i]]}" stroke="#7e706359"/><text x="267" y="${59 + i * 35}" style="font-size:12px">${name}</text>`;
    start = end;
  });
  return s + `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#88786a" stroke-width="1.4"/><text class="axis-label" x="196" y="249" text-anchor="middle">daily activities of a cat</text>`;
}
const boxData = Array.from({ length: 80 }, (_, i) => 4.15 + ((Math.sin(i * 2.1) + Math.sin(i * 5.7) + Math.cos(i * 1.37)) / 3 + 1) * 2.86);
function histogramCounts(bins) { const counts = Array(bins).fill(0); boxData.forEach(v => counts[clamp(Math.floor((v - 4) / 6 * bins), 0, bins - 1)]++); return counts; }
function histChart() {
  const counts = histogramCounts(state.bins), max = Math.ceil(Math.max(...counts) / 5) * 5;
  let s = grid(max, 6, 'box fits (inches)', 'frequency', ['4', '5', '6', '7', '8', '9', '10']);
  const w = 295 / state.bins;
  counts.forEach((v, i) => {
    const h = v / max * 170, x = 52 + i * w, y = 209 - h;
    const label = `${(4 + i * 6 / state.bins).toFixed(1)}–${(4 + (i + 1) * 6 / state.bins).toFixed(1)} inches: ${v} boxes`;
    s += point('hist', i, x + w / 2, y, label, `<rect x="${x}" y="${y}" width="${w - 1}" height="${h}" rx="1" fill="${colours()[0]}" fill-opacity=".83" stroke="${palettes[state.palette].ink}" stroke-width="1.4"/>`, false);
  });
  if (state.cuteness > 30) s += `<g transform="translate(51 24) scale(.62)"><g transform="translate(5 -2)">${catArt(0)}</g><g stroke="#87663e" stroke-width="2" stroke-linejoin="round"><path d="m8 73 47 11 50-10v45l-49 13-48-13Z" fill="#dca762"/><path d="m55 84 1 48M8 73l-10 15 45 13 12-17 12 17 48-15-10-12" fill="#efc787"/></g><ellipse cx="34" cy="77" rx="9" ry="6" fill="#a4a19d" stroke="#49423f" stroke-width="2"/><ellipse cx="79" cy="77" rx="9" ry="6" fill="#a4a19d" stroke="#49423f" stroke-width="2"/></g><text x="128" y="47" style="font-family:var(--hand);fill:#a88bb9;font-size:13px">if I fits,</text><text x="133" y="63" style="font-family:var(--hand);fill:#a88bb9;font-size:13px">I sits.</text>`;
  return s;
}
function heatValue(x, y) {
  const nx = (x - 11.5) / 10, ny = (y - 11) / 10;
  const head = nx * nx / .83 + (ny - .12) * (ny - .12) / .8 < 1;
  const ear = y > 1 && y < 9 && ((x >= 2 && x < 8 && y > Math.abs(x - 3) * 1.15) || (x >= 16 && x < 22 && y > Math.abs(x - 20) * 1.15));
  let value = .1 + .06 * Math.sin(x * .7 + y * 1.8);
  if (head || ear) value = .63 + .12 * Math.cos(x * .9) + .07 * Math.sin(y * 1.6);
  if (head && (x - 11.5) ** 2 / 47 + (y - 14) ** 2 / 30 < 1) value = .92;
  if (head && y < 9 && x % 4 === 0) value -= .18;
  if ((x === 6 || x === 9 || x === 15 || x === 18) && y === 12 || (x === 7 || x === 8 || x === 16 || x === 17) && y === 11) value = .07;
  if (y === 15 && (x === 11 || x === 12) || y === 16 && (x === 10 || x === 13) || y === 17 && (x === 11 || x === 12)) value = .09;
  if ((x === 3 || x === 4 || x === 19 || x === 20) && (y === 14 || y === 16)) value = .3;
  return clamp(value, 0, 1);
}
function heatColour(v) {
  const stops = [[174, 77, 48], [223, 116, 48], [246, 171, 68], [255, 209, 107], [255, 242, 182]];
  const f = clamp(v + (state.warmth - 50) / 300, 0, .999) * 4;
  const lo = Math.floor(f), t = f - lo;
  return `rgb(${stops[lo].map((a, i) => Math.round(a + (stops[Math.min(lo + 1, 4)][i] - a) * t)).join(',')})`;
}
function heatChart() {
  let s = '';
  const u = ++uid;
  for (let y = 0; y < 22; y++) for (let x = 0; x < 24; x++) {
    const v = heatValue(x, y), temp = (29 + (1 - v) * 8 + state.warmth * .05).toFixed(1);
    s += `<rect class="heat-cell" x="${65 + x * 9}" y="${18 + y * 9}" width="9.1" height="9.1" fill="${heatColour(v)}" data-tip="Pixel (${x}, ${y}) · ${temp} °C"/>`;
  }
  return s + `<rect x="65" y="18" width="216" height="198" fill="none" stroke="#926b4d" stroke-width="1.6"/><defs><linearGradient id="heat-${u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${heatColour(0)}"/><stop offset=".5" stop-color="${heatColour(.5)}"/><stop offset="1" stop-color="${heatColour(1)}"/></linearGradient></defs><rect x="307" y="51" width="16" height="135" fill="url(#heat-${u})" stroke="#a28766" stroke-width="1"/><text x="315" y="36" text-anchor="middle" style="font-family:var(--hand);font-size:13px">warm</text><text x="315" y="204" text-anchor="middle" style="font-family:var(--hand);font-size:13px">cozy</text><text class="axis-label" x="190" y="249" text-anchor="middle">temperature map of a happy cat</text>`;
}
const chartFns = { line: lineChart, bar: barChart, scatter: scatterChart, pie: pieChart, hist: histChart, heat: heatChart };
function chartSVG(id) {
  const spec = specs.find(s => s.id === id);
  return `<svg xmlns="${NS}" viewBox="0 0 380 263" class="plot-svg" data-plot="${id}" role="group" aria-label="${spec.label}"><title>${spec.label}</title><desc>${spec.title}. Use the Edit data button for accessible controls.</desc>${chartFns[id]()}</svg>`;
}
function renderCards() {
  $('#chart-grid').innerHTML = specs.map((s, i) => `<article class="chart-card" data-card="${s.id}" style="--chart-colour:${colours()[s.colour]}"><div class="card-top"><div class="card-title"><span class="card-number">0${i + 1}</span><h2>${s.method}</h2></div><div class="card-menu"><button class="icon-button" data-edit="${s.id}" aria-label="Edit ${s.label}" title="Edit chart data">${editIcon}</button><button class="icon-button" data-edit="${s.id}" aria-label="Expand ${s.label}" title="Expand chart">${expandIcon}</button></div></div><p class="chart-subtitle">${s.title}</p><div class="plot-wrap">${chartSVG(s.id)}</div><div class="chart-footer"><span class="card-hint">${s.hint}</span><button data-edit="${s.id}">Edit data ↗</button></div></article>`).join('');
}
function renderChart(id) {
  const plot = $(`[data-card="${id}"] .plot-wrap`);
  if (plot) plot.innerHTML = chartSVG(id);
  if (state.activeChart === id) $('#detail-plot').innerHTML = chartSVG(id);
}
function toast(msg) {
  clearTimeout(toastTimer); $('#toast').textContent = msg; $('#toast').classList.add('visible');
  toastTimer = setTimeout(() => $('#toast').classList.remove('visible'), 2600);
}
function hearts(x, y, count = 7) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  for (let i = 0; i < count; i++) {
    const heart = document.createElement('span'); heart.className = 'flying-heart'; heart.textContent = i % 3 === 0 ? '✦' : '♥';
    heart.style.cssText = `left:${x - 10 + (Math.random() - .5) * 35}px;top:${y}px;--dx:${(Math.random() - .5) * 170}px;--r:${(Math.random() - .5) * 70}deg;animation-delay:${i * .055}s;color:${colours()[i % 5]}`;
    $('#hearts').append(heart); setTimeout(() => heart.remove(), 1900);
  }
}
function makeDownload(content, filename, type = 'image/svg+xml') {
  const blob = new Blob([content], { type }); const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = filename; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
}
function showView(view, updateHash = true) {
  if (!['playground', 'gallery', 'components', 'code'].includes(view)) view = 'playground';
  state.view = view;
  $$('.view').forEach(el => el.hidden = el.id !== `view-${view}`);
  $$('.nav-button').forEach(el => { const selected = el.dataset.view === view; el.classList.toggle('active', selected); if (selected) el.setAttribute('aria-current', 'page'); else el.removeAttribute('aria-current'); });
  if (view === 'components') renderStudio();
  if (view === 'code') renderCode();
  document.dispatchEvent(new CustomEvent('catplotlib-view', { detail: view }));
  if (updateHash) history.replaceState(null, '', '#' + view);
}
function renderPalettes() {
  $('#palettes').innerHTML = palettes.map((p, i) => `<button class="palette-button ${state.palette === i ? 'selected' : ''}" data-palette="${i}" aria-label="${p.name} palette" title="${p.name}" aria-pressed="${state.palette === i}" style="background:conic-gradient(${p.colours[0]} 0deg 180deg,${p.colours[4]} 180deg 360deg)"></button>`).join('');
  $('#palette-name').textContent = palettes[state.palette].name;
}
function renderStudio() {
  $('#studio-cat').innerHTML = catSVG(state.cat, { full: true, mood: state.mood, blush: state.blush, scarf: state.scarf });
  $('#studio-name').textContent = cats[state.cat].name;
  $('#studio-description').textContent = cats[state.cat].description;
  $('#cat-picker').innerHTML = cats.map((c, i) => `<button class="cat-choice ${state.cat === i ? 'selected' : ''}" data-cat="${i}" aria-pressed="${state.cat === i}">${catSVG(i)}<span class="cat-choice-name">${c.name}</span></button>`).join('');
  $$('#mood-picker button').forEach(b => { b.classList.toggle('selected', b.dataset.mood === state.mood); b.setAttribute('aria-pressed', b.dataset.mood === state.mood); });
  $('#studio-speech').textContent = { happy: 'hello, human.', sleepy: 'five more minutes…', surprised: 'is that a treat?!' }[state.mood];
  $('#tip-cat').innerHTML = catSVG(2);
  $('#marker-samples').innerHTML = cats.map((c, i) => catSVG(i)).join('');
  $('#paw-samples').innerHTML = colours().map(c => pawSVG(c)).join('');
  $('#colour-samples').innerHTML = colours().map(c => `<span style="background:${c}" title="${c}" aria-label="${c}"></span>`).join('');
}
function petCat(event) {
  const r = $('#studio-cat').getBoundingClientRect();
  hearts(r.x + r.width / 2, r.y + r.height / 2);
  $('#studio-speech').textContent = ['purrrrrrrrr.', 'you may continue.', 'excellent human.', 'head scritches!'][Math.floor(Math.random() * 4)];
  const cat = $('#studio-cat'); cat.animate([{ transform: 'rotate(0)' }, { transform: 'rotate(-7deg) scale(1.06)' }, { transform: 'rotate(4deg)' }, { transform: 'rotate(0)' }], { duration: matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 450 });
}
const pythonCode = `# Install or update the downloaded source: python -m pip install --upgrade .
import matplotlib.pyplot as plt
import catplotlib as cp

with cp.context("milk_tea"):
    fig, (ax, bar_ax) = plt.subplots(1, 2, figsize=(11.5, 4.8))

    line, = ax.plot([0, 1, 2, 3, 4, 5], [2, 3.7, 6.4, 5.2, 8.8, 9.8])
    cp.dreamy_line(line)  # Gradient fill and little stars.
    cp.catify(line, companion="nugget", size=27)
    ax.set(xlabel="Time (naps)", ylabel="Mood (purrs)",
           title="A little data. A lot of cat.", ylim=(0, 12))

    bars = bar_ax.bar(["Mochi", "Beans", "Nugget", "Tofu"],
                      [16, 12, 13, 15], color=cp.palette()[:4], width=.6)
    cp.bubble_bars(bars)  # Rounded corners, outline, and white highlight.
    cp.perch(bars, size=25)
    bar_ax.set(ylabel="Treats earned", title="Treats for the whole squad",
               ylim=(0, 20))

    fig.tight_layout()
    fig.savefig("my-cat-plot.svg")
    fig.savefig("my-cat-plot.png")
    plt.show()`;
function sourceCode() { return state.code === 'python' ? pythonCode : catSVG(state.cat, { full: true, mood: state.mood, blush: state.blush, scarf: state.scarf }); }
function renderCode() {
  $('#code-content').textContent = sourceCode();
  $$('.code-tabs [data-code]').forEach(b => b.classList.toggle('selected', b.dataset.code === state.code));
  $('#code-disclaimer').textContent = state.code === 'python' ? 'The theme sets colours and fonts. bubble_bars() adds rounded highlights; dreamy_line() adds the gradient and stars.' : 'This is the actual SVG from the cat studio. Save it as a .svg file, or embed it in HTML.';
  $('#code-cat').innerHTML = catSVG(state.cat, { full: true, mood: 'sleepy', scarf: true });
}
function dataControls(id) {
  let rows = [];
  if (id === 'line') rows = state.line.map((v, i) => [`Nap ${i}`, v, 0, 10, .1, i]);
  if (id === 'bar') rows = state.bar.map((v, i) => [cats[i].name, v, 0, 20, 1, i]);
  if (id === 'pie') rows = state.pie.map((v, i) => [pieLabels[i] === 'knock stuff over' ? 'Knock over' : pieLabels[i], v, 1, 60, 1, i]);
  if (id === 'scatter') rows = state.scatter.map((v, i) => [`Paw ${i + 1} · Y`, v[1], 0, 10, .1, i]);
  if (id === 'hist') rows = [['Bins', state.bins, 4, 14, 1, 0]];
  if (id === 'heat') rows = [['Warmth', state.warmth, 0, 100, 1, 0]];
  $('#data-controls').innerHTML = rows.map(([name, v, min, max, step, i]) => `<label class="data-input-row"><span>${esc(name)}</span><input type="range" data-value-index="${i}" min="${min}" max="${max}" step="${step}" value="${v}" aria-label="${esc(name)}"><output>${Number.isInteger(v) ? v : v.toFixed(1)}</output></label>`).join('');
}
function openChart(id) {
  state.activeChart = id;
  const spec = specs.find(s => s.id === id);
  $('#dialog-method').textContent = spec.method; $('#dialog-title').textContent = spec.label;
  $('#detail-hint').textContent = { line: 'Move the sliders, or drag a cat directly on the plot.', bar: 'How many treats has each very good cat earned?', scatter: 'Drag paws to move both coordinates. Sliders adjust zoomies.', pie: 'Change the activity weights. Percentages always add up to 100%.', hist: 'The same 80 box measurements, grouped into different bin sizes.', heat: 'Warm up the colour map. Hover over a pixel to see its temperature.' }[id];
  $('#detail-plot').innerHTML = chartSVG(id); dataControls(id);
  $('#tooltip').hidden = true;
  if (!$('#chart-dialog').open) $('#chart-dialog').showModal();
}
function exportChart() {
  const id = state.activeChart;
  const svg = $('#detail-plot svg').cloneNode(true);
  svg.setAttribute('width', '1140'); svg.setAttribute('height', '789');
  const style = document.createElementNS(NS, 'style');
  style.textContent = 'text{font-family:Trebuchet MS,Arial,sans-serif;font-size:12px;fill:#80786e}.axis-label{font-family:Comic Sans MS,cursive;font-size:14px;fill:#6c6259}.grid-line{stroke:#e8e0d4;stroke-dasharray:3 5;stroke-width:1}.axis-line{stroke:#9c9284;stroke-width:1.4;fill:none}.data-line{stroke-linecap:round;stroke-linejoin:round}.cat-sleep-z{font-size:13px;fill:#8c6ab6}';
  const bg = document.createElementNS(NS, 'rect'); bg.setAttribute('width', '380'); bg.setAttribute('height', '263'); bg.setAttribute('fill', '#fffdf6');
  svg.prepend(bg); svg.prepend(style);
  svg.querySelectorAll('[tabindex]').forEach(el => { el.removeAttribute('tabindex'); el.removeAttribute('role'); });
  makeDownload(new XMLSerializer().serializeToString(svg), `catplotlib-${id}.svg`);
  toast('One fresh little plot, ready to go.');
}
function shuffle() {
  state.line = state.line.map(() => Math.round((1 + Math.random() * 8.8) * 10) / 10);
  state.bar = state.bar.map(() => 3 + Math.floor(Math.random() * 17));
  state.scatter = state.scatter.map(() => [Math.round((.5 + Math.random() * 8.5) * 10) / 10, Math.round((.6 + Math.random() * 8.8) * 10) / 10]);
  state.pie = state.pie.map(() => 5 + Math.floor(Math.random() * 35));
  state.bins = 5 + Math.floor(Math.random() * 8); state.warmth = 25 + Math.floor(Math.random() * 60);
  renderCards(); $('#chart-grid').classList.remove('shuffled'); void $('#chart-grid').offsetWidth; $('#chart-grid').classList.add('shuffled');
  toast('The cats have rearranged your data.');
}
function localPoint(svg, event) {
  const p = new DOMPoint(event.clientX, event.clientY); return p.matrixTransform(svg.getScreenCTM().inverse());
}
function setDraggedValue(event) {
  if (!drag) return;
  const p = localPoint(drag.svg, event), id = drag.id, i = drag.index;
  if (id === 'scatter') state.scatter[i] = [Math.round(clamp((p.x - 52) / 29.5, 0, 10) * 10) / 10, Math.round(clamp((209 - p.y) / 17, 0, 10) * 10) / 10];
  else if (id === 'line') state.line[i] = Math.round(clamp((209 - p.y) / 17, 0, 10) * 10) / 10;
  else if (id === 'bar') state.bar[i] = Math.round(clamp((209 - p.y - 12) / 8.5, 0, 20));
  const svg = drag.svg;
  svg.innerHTML = `<title>${specs.find(s => s.id === id).label}</title>` + chartFns[id]();
  if (state.activeChart === id) dataControls(id);
}

document.addEventListener('click', event => {
  const t = event.target.closest('button');
  if (!t) return;
  if (t.dataset.view) showView(t.dataset.view);
  if (t.dataset.edit) openChart(t.dataset.edit);
  if (t.dataset.palette !== undefined) { state.palette = Number(t.dataset.palette); renderPalettes(); renderCards(); }
  if (t.dataset.marker) { state.marker = t.dataset.marker; $$('#marker-controls button').forEach(b => { b.classList.toggle('selected', b === t); b.setAttribute('aria-pressed', b === t); }); renderCards(); }
  if (t.dataset.cat !== undefined) { state.cat = Number(t.dataset.cat); renderStudio(); }
  if (t.dataset.mood) { state.mood = t.dataset.mood; renderStudio(); }
  if (t.dataset.code) { state.code = t.dataset.code; renderCode(); }
});
$('#cuteness').addEventListener('input', e => { state.cuteness = Number(e.target.value); $('#cute-label').textContent = state.cuteness < 25 ? 'a lil’' : state.cuteness < 75 ? 'very' : 'illegal'; renderCards(); });
$('#grid-toggle').addEventListener('change', e => { state.grid = e.target.checked; renderCards(); });
$('#shuffle-all').addEventListener('click', shuffle);
$('#treat-button').addEventListener('click', e => {
  state.treats++; $('#treat-count').textContent = state.treats;
  const r = e.currentTarget.getBoundingClientRect(); hearts(r.x + r.width / 2, r.bottom);
  state.bar = state.bar.map(v => Math.min(20, v + 1)); renderChart('bar');
  toast(state.bar.every(v => v === 20) ? 'Treat jars are full. The squad is very pleased.' : state.treats === 1 ? 'A treat for every cat! +1 to the whole squad.' : ['Treats distributed. Purr levels rising.', 'Excellent human. The squad approves.', 'Another round of very well-earned snacks.'][state.treats % 3]);
});
$('#pet-cat').addEventListener('click', petCat); $('#studio-cat').addEventListener('click', petCat);
$('#blush-toggle').addEventListener('change', e => { state.blush = e.target.checked; renderStudio(); });
$('#scarf-toggle').addEventListener('change', e => { state.scarf = e.target.checked; renderStudio(); });
$('#download-cat').addEventListener('click', () => { makeDownload(catSVG(state.cat, { full: true, mood: state.mood, blush: state.blush, scarf: state.scarf }), `${cats[state.cat].name.toLowerCase()}-cat.svg`); toast('A tiny companion for your next project.'); });
$('#copy-code').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(sourceCode()); $('#copy-code').textContent = 'Copied!'; setTimeout(() => $('#copy-code').textContent = 'Copy', 1800); }
  catch { const range = document.createRange(); range.selectNodeContents($('#code-content')); const sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range); toast('Code selected. Press Ctrl+C or ⌘C to copy.'); }
});
$('#back-to-plots').addEventListener('click', () => showView('playground'));
$('#close-dialog').addEventListener('click', () => $('#chart-dialog').close());
$('#chart-dialog').addEventListener('close', () => { if (state.activeChart) renderChart(state.activeChart); state.activeChart = null; $('#tooltip').hidden = true; });
$('#chart-dialog').addEventListener('click', e => { if (e.target === e.currentTarget) { const r = e.currentTarget.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) e.currentTarget.close(); } });
$('#reset-chart').addEventListener('click', () => {
  const id = state.activeChart;
  if (id === 'hist') state.bins = defaults.bins; else if (id === 'heat') state.warmth = defaults.warmth; else state[id] = structuredClone(defaults[id]);
  renderChart(id); dataControls(id);
});
$('#data-controls').addEventListener('input', e => {
  if (!e.target.matches('input')) return;
  const value = Number(e.target.value), i = Number(e.target.dataset.valueIndex), id = state.activeChart;
  if (id === 'hist') state.bins = value; else if (id === 'heat') state.warmth = value; else if (id === 'scatter') state.scatter[i][1] = value; else state[id][i] = value;
  e.target.nextElementSibling.value = value;
  renderChart(id);
});
$('#export-chart').addEventListener('click', exportChart);
document.addEventListener('pointerdown', event => {
  const target = event.target.closest('[data-draggable="true"]');
  if (!target || event.button !== 0) return;
  const svg = target.closest('svg.plot-svg');
  drag = { id: target.dataset.chart, index: Number(target.dataset.index), svg, pointerId: event.pointerId };
  svg.setPointerCapture(event.pointerId); $('#tooltip').hidden = true; event.preventDefault();
});
document.addEventListener('pointermove', event => { if (drag && drag.pointerId === event.pointerId) { setDraggedValue(event); return; } const target = event.target.closest('[data-tip]'); if (target) showTooltip(target, event.clientX, event.clientY); else $('#tooltip').hidden = true; });
function endDrag() { if (!drag) return; const id = drag.id; drag = null; renderChart(id); }
document.addEventListener('pointerup', endDrag); document.addEventListener('pointercancel', endDrag);
document.addEventListener('keydown', event => {
  const target = event.target.closest('[data-draggable="true"]');
  if (!target || !['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) return;
  event.preventDefault();
  const id = target.dataset.chart, i = Number(target.dataset.index), d = ['ArrowUp', 'ArrowRight'].includes(event.key) ? 1 : -1;
  if (id === 'scatter') { const axis = ['ArrowLeft', 'ArrowRight'].includes(event.key) ? 0 : 1; state.scatter[i][axis] = Math.round(clamp(state.scatter[i][axis] + d * .2, 0, 10) * 10) / 10; }
  else state[id][i] = Math.round(clamp(state[id][i] + d * (id === 'bar' ? 1 : .2), 0, id === 'bar' ? 20 : 10) * 10) / 10;
  const inDialog = !!target.closest('dialog'); renderChart(id); if (state.activeChart === id) dataControls(id);
  $(`[data-chart="${id}"][data-index="${i}"]`, inDialog ? $('#detail-plot') : $('#chart-grid'))?.focus();
});
function showTooltip(target, x, y) {
  if (drag) return;
  const tip = $('#tooltip');
  const parent = $('#chart-dialog').open ? $('#chart-dialog') : document.body;
  if (tip.parentElement !== parent) parent.append(tip);
  tip.textContent = target.dataset.tip; tip.hidden = false;
  tip.style.left = `${Math.max(8, Math.min(x + 14, window.innerWidth - tip.offsetWidth - 12))}px`;
  tip.style.top = `${Math.max(8, Math.min(y - tip.offsetHeight - 12, window.innerHeight - tip.offsetHeight - 12))}px`;
}
document.addEventListener('focusin', event => { const t = event.target.closest('[data-tip]'); if (t) { const r = t.getBoundingClientRect(); showTooltip(t, r.x + r.width / 2, r.y); } });
document.addEventListener('focusout', () => $('#tooltip').hidden = true);
document.addEventListener('pointerleave', () => $('#tooltip').hidden = true);
window.addEventListener('hashchange', () => showView(location.hash.slice(1), false));
window.addEventListener('scroll', () => $('#tooltip').hidden = true, { passive: true });
$('#brand-cat').innerHTML = catSVG(0);
$('#intro-cat').innerHTML = catSVG(2, { full: true, scarf: true });
$('.tiny-paw').innerHTML = pawSVG('#bd8296');
$('.small-paw').innerHTML = pawSVG('#b5a1c8');
$('.note-paw').innerHTML = pawSVG('#c6a5c5');
renderPalettes(); renderCards(); showView(location.hash.slice(1) || 'playground', false);
