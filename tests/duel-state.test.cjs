const test = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {gapForHeight,modeForGap,bubbleBarPaths} = require('../docs/duel.js');
const model = JSON.parse(readFileSync(new URL('../docs/gallery/duel-scene.json', `file://${__filename}`)));
test('actual bar heights produce the two requested reactions', () => {
  assert.equal(modeForGap(gapForHeight(model,12)), 'swat_down');
  assert.equal(modeForGap(gapForHeight(model,8)), 'arched');
  assert.equal(modeForGap(gapForHeight(model,18)), 'swat_down');
});
test('the reaction does not flicker as height crosses the boundary', () => {
  assert.equal(modeForGap(18,'swat_down'), 'arched');
  assert.equal(modeForGap(19,'arched'), 'arched');
  assert.equal(modeForGap(19,'swat_down'), 'swat_down');
  assert.equal(modeForGap(22,'arched'), 'swat_down');
});
test('browser reach derives from the same SVG-sized raised paws', () => {
  const pose=model.poses.stretch;
  assert.equal(model.reach, pose.size/pose.width*(pose.anchor[1]-16));
  assert.ok(model.poses.swat_down.svg.includes('data-part="swatting-paw"'));
  assert.ok(model.poses.arched.svg.includes('aria-label="nugget arched'));
});
test('resizing preserves the exact rounded bar and shine geometry exported by Python', () => {
  const tokens = path => path.match(/[a-zA-Z]|[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?/g).map(v => /^[a-z]$/i.test(v) ? v.toUpperCase() : Number(v));
  for (const palette of ['milk_tea','strawberry','blueberry','matcha']) {
    for (const sample of [0,1]) {
      const svg = readFileSync(new URL(`../docs/gallery/bar-${palette}-${sample}.svg`, `file://${__filename}`),'utf8');
      const group = svg.slice(svg.indexOf('<g id="catplotlib-duel-bar">'));
      const expected = bubbleBarPaths(model,model.sampleHeights[sample]);
      for (const [part,marker] of [['body','body'],['shine','shine']]) {
        const match = group.match(new RegExp(`<g id="catplotlib-bubble-${marker}-[^"]+">\\s*<path d="([^"]+)"`));
        assert.ok(match, `${palette} sample ${sample} includes ${part}`);
        const actual=tokens(match[1]), wanted=tokens(expected[part]);
        assert.equal(actual.length,wanted.length);
        actual.forEach((v,i) => typeof v === 'string' ? assert.equal(v,wanted[i]) : assert.ok(Math.abs(v-wanted[i])<1e-5, `${part}: ${v} differs from ${wanted[i]}`));
      }
    }
  }
});
