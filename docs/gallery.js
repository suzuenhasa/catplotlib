/* Real Matplotlib output, with local-only browsing and downloads. */
(() => {
  let catalog = null, loading = null, category = 'All', query = '', active = null;
  let palette = 'milk_tea', sample = 0, companions = true, request = 0, lastSvg = '';
  let duel = null, duelHeight = null, duelModelPromise = null, duelMode = 'swat_down';
  const byId = id => document.getElementById(id);
  const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  async function load() {
    if (catalog) return;
    if (loading) return loading;
    loading = (async () => {
      try {
        const response = await fetch('gallery/manifest.json');
        if (!response.ok) throw Error('The plot catalogue could not load.');
        catalog = await response.json();
        if (!Array.isArray(catalog.plots)) throw Error('The plot catalogue is incomplete.');
        byId('gallery-categories').innerHTML = ['All', 'Cat scenes', ...new Set(catalog.plots.map(p => p.category))].map(c => `<button data-category="${escape(c)}" class="${c === category ? 'selected' : ''}" aria-pressed="${c === category}">${escape(c)}</button>`).join('');
        render();
      } catch(e) {
        byId('recipe-grid').innerHTML = '<div class="gallery-empty">The cat-alogue could not load. <button id="retry-gallery" class="text-button">Try again</button></div>';
        byId('gallery-count').textContent = 'Could not load plots';
        byId('retry-gallery').onclick = load;
      } finally { byId('recipe-grid').setAttribute('aria-busy', 'false'); loading = null; }
    })();
    return loading;
  }
  function render() {
    const plots = catalog.plots.filter(p => (category === 'All' || p.category === category || category === 'Cat scenes' && ['wireframe','bar3d','bar'].includes(p.id)) && `${p.method} ${p.title} ${p.category} ${p.description}`.toLowerCase().includes(query));
    byId('gallery-count').textContent = `${plots.length} of ${catalog.count} plot recipes`;
    byId('recipe-grid').innerHTML = plots.length ? plots.map(p => `<button class="recipe-card" data-recipe="${p.id}" aria-label="Open ${escape(p.method)} recipe"><img src="gallery/${p.id}.png" alt="${escape(p.title)}" loading="lazy" width="468" height="312"><div class="recipe-card-info"><span>${escape(p.category)} · SVG + Python</span><h2>${escape(p.method)}</h2><p>${escape(p.title)}</p></div></button>`).join('') : '<div class="gallery-empty">No cats in this corner. Try a different plot name.</div>';
  }
  function python() {
    if (!active) return '';
    let result = active.code.replaceAll('default_rng(7)', `default_rng(${sample ? 19 : 7})`).replace(/^    seed = 7$/m, `    seed = ${sample ? 19 : 7}`).replaceAll("'milk_tea'", `'${palette}'`);
    if (active.id === 'bar' && duelHeight !== null) result = result.replace('    bars = ax.bar', `    y = y.astype(float)\n    y[1] = ${duelHeight.toFixed(1)}\n    bars = ax.bar`);
    if (active.id === 'bar' && duelMode === 'arched') result = result.replace('    upper.set_gid("catplotlib-cat-duel-upper")', '    upper.set_gid("catplotlib-cat-duel-upper")\n    upper.set_pose("arched")');
    if (!companions) result = result.replace('\nplt.show()', '\n# Hide cats and scenes; keep the paw markers.\nfor artist in list(ax.artists):\n    if (artist.get_gid() or "").startswith("catplotlib-cat-"):\n        artist.remove()\n\nplt.show()');
    return result;
  }
  async function preview() {
    if (!active) return;
    const current = ++request;
    if (duel) { duel.destroy(); duel = null; }
    byId('duel-height').disabled = true;
    byId('recipe-code').textContent = python();
    byId('recipe-preview').setAttribute('aria-busy', 'true');
    byId('recipe-save-svg').disabled = true;
    byId('recipe-preview').textContent = 'Warming up the plot…';
    try {
      const url = `gallery/${active.id}-${palette}-${sample}.svg`;
      const response = await fetch(url);
      if (!response.ok) throw Error('Unable to load plot');
      const source = await response.text();
      let duelModel = null;
      if (active.id === 'bar') {
        if (!duelModelPromise) duelModelPromise = fetch('gallery/duel-scene.json').then(r => { if (!r.ok) throw Error('Unable to load cat poses'); return r.json(); }).catch(e => { duelModelPromise = null; throw e; });
        duelModel = await duelModelPromise;
      }
      if (current !== request) return;
      const doc = new DOMParser().parseFromString(source, 'image/svg+xml');
      if (doc.querySelector('parsererror')) throw Error('Invalid plot');
      const svg = doc.documentElement;
      if (svg.localName !== 'svg') throw Error('Invalid plot');
      // The assets are bundled outputs of the local Matplotlib renderer.
      svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', active.title);
      byId('recipe-preview').replaceChildren(document.importNode(svg, true));
      lastSvg = source;
      if (duelModel) {
        const height = duelHeight === null ? duelModel.sampleHeights[sample] : duelHeight;
        duel = CatplotlibDuel.mount(byId('recipe-preview').querySelector('svg'), duelModel, height, {
          cats: companions, motion: byId('duel-motion').checked, initialMode: duelMode,
          onChange: ({height, mode, cats}) => {
            duelHeight = height; duelMode = mode;
            byId('duel-height').value = height;
            byId('duel-height-value').textContent = height.toFixed(1);
            const reaction = !cats ? 'Cats hidden' : mode === 'arched' ? 'Personal space! >:C' : 'Room to swat';
            if (byId('duel-reaction').textContent !== reaction) byId('duel-reaction').textContent = reaction;
            byId('duel-reaction').dataset.mood = mode;
          }
        });
        byId('duel-height').disabled = false;
        byId('recipe-code').textContent = python();
      }
      byId('recipe-save-svg').disabled = false;
      byId('recipe-preview').classList.toggle('no-companions', !companions);
    } catch(e) {
      if (current !== request) return;
      lastSvg = '';
      byId('recipe-preview').innerHTML = '<div class="recipe-error">This plot could not load.<button id="retry-recipe">Try again</button></div>';
      byId('retry-recipe').onclick = preview;
    } finally { if (current === request) byId('recipe-preview').setAttribute('aria-busy', 'false'); }
  }
  function open(id) {
    active = catalog.plots.find(p => p.id === id);
    if (!active) return;
    duelHeight = null; duelMode = 'swat_down';
    byId('recipe-preview').setAttribute('aria-live', active.id === 'bar' ? 'off' : 'polite');
    byId('duel-controls').hidden = active.id !== 'bar';
    byId('recipe-category').textContent = `${active.category} / ${active.method}`;
    byId('recipe-title').textContent = active.title;
    byId('recipe-description').textContent = active.description + (active.projection === '3d' ? ' This is an SVG snapshot; run the Python for interactive rotation.' : '');
    byId('recipe-versions').textContent = `Rendered with Matplotlib ${catalog.matplotlib} · Catplotlib ${catalog.package} · two example datasets`;
    byId('recipe-dialog').showModal();
    preview();
  }
  document.addEventListener('catplotlib-view', e => { if (e.detail === 'gallery') load(); });
  if (location.hash === '#gallery') load();
  byId('gallery-categories').addEventListener('click', e => {
    const b = e.target.closest('[data-category]'); if (!b) return;
    category = b.dataset.category;
    byId('gallery-categories').querySelectorAll('button').forEach(el => { el.classList.toggle('selected', el === b); el.setAttribute('aria-pressed', el === b); });
    render();
  });
  byId('gallery-search').addEventListener('input', e => { query = e.target.value.trim().toLowerCase(); if (catalog) render(); });
  byId('recipe-grid').addEventListener('click', e => { const card = e.target.closest('[data-recipe]'); if (card) open(card.dataset.recipe); });
  byId('recipe-palette').addEventListener('change', e => { palette = e.target.value; preview(); });
  byId('recipe-sample').addEventListener('change', e => { sample = Number(e.target.value); duelHeight = null; duelMode = 'swat_down'; preview(); });
  byId('recipe-cats').addEventListener('change', e => {
    companions = e.target.checked;
    if (duel) duel.setCats(companions);
    byId('recipe-preview').classList.toggle('no-companions', !companions);
    byId('recipe-code').textContent = python();
  });
  byId('duel-motion').checked = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  byId('duel-height').addEventListener('input', e => {
    if (!duel) return;
    duel.setHeight(Number(e.target.value));
    byId('recipe-code').textContent = python();
  });
  byId('duel-motion').addEventListener('change', e => { if (duel) duel.setMotion(e.target.checked); });
  byId('close-recipe').onclick = () => byId('recipe-dialog').close();
  byId('recipe-dialog').addEventListener('close', () => { request++; if (duel) { duel.destroy(); duel = null; } });
  byId('recipe-dialog').addEventListener('click', e => {
    if (e.target !== e.currentTarget) return;
    const r = e.currentTarget.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) e.currentTarget.close();
  });
  byId('recipe-save-code').onclick = () => makeDownload(python(), `catplotlib-${active.id}.py`, 'text/x-python');
  byId('recipe-save-svg').onclick = () => {
    if (duel) { makeDownload(duel.serialize(), `catplotlib-${active.id}-${palette}.svg`); return; }
    if (!lastSvg) return;
    const doc = new DOMParser().parseFromString(lastSvg, 'image/svg+xml');
    if (!companions) doc.querySelectorAll('[id^="catplotlib-cat-"]').forEach(el => el.remove());
    makeDownload(new XMLSerializer().serializeToString(doc.documentElement), `catplotlib-${active.id}-${palette}.svg`);
  };
  byId('recipe-copy-code').onclick = async () => {
    try { await navigator.clipboard.writeText(python()); byId('recipe-copy-code').textContent = 'Copied!'; setTimeout(() => byId('recipe-copy-code').textContent = 'Copy', 1600); }
    catch { const r = document.createRange(); r.selectNodeContents(byId('recipe-code')); const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(r); byId('recipe-copy-code').textContent = 'Press Ctrl/⌘+C'; }
  };
})();
