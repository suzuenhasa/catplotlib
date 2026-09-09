const test = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');

test('the website starter is the exact runnable example shipped with the package', () => {
  const script=readFileSync(join(__dirname,'../docs/app.js'),'utf8');
  const match=script.match(/const pythonCode = `([\s\S]*?)`;/);
  assert.ok(match);
  const example=readFileSync(join(__dirname,'../python/examples/quickstart.py'),'utf8').trim();
  assert.equal(match[1],example);
});

test('every relevant gallery download includes its finish helper', () => {
  const manifest=JSON.parse(readFileSync(join(__dirname,'../docs/gallery/manifest.json'),'utf8'));
  for (const [ids,helper] of [
    [['bar','barh','grouped_bar','stacked_bar','waterfall','hist','broken_barh'],'cp.bubble_bars('],
    [['plot','step','errorbar','ecdf','loglog','psd'],'cp.dreamy_line(']
  ]) {
    for (const id of ids) assert.ok(manifest.plots.find(p=>p.id===id).code.includes(helper),`${id} must include ${helper}`);
  }
});
