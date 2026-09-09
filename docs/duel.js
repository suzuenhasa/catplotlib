/* The same vector poses and point-based spacing used by the Python artists. */
(function(root) {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  function gapForHeight(model, height) {
    return height * model.pointsPerTreat - model.reach;
  }
  function modeForGap(gap, previous = 'swat_down', closeGap = 18, hysteresis = 3) {
    return gap <= closeGap + (previous === 'arched' ? hysteresis : 0) ? 'arched' : 'swat_down';
  }
  function bubbleBarPaths(model, height) {
    const x0 = model.barLeft, x1 = model.barRight;
    const bottom = model.floorY, top = bottom - height * model.pointsPerTreat;
    const r = Math.min(2.5, (x1-x0)/2, (bottom-top)/2);
    const inset = Math.min(3.2, (x1-x0)*.22, (bottom-top)*.22);
    return {
      body: `M ${x0+r} ${bottom} L ${x1-r} ${bottom} Q ${x1} ${bottom} ${x1} ${bottom-r} L ${x1} ${top+r} Q ${x1} ${top} ${x1-r} ${top} L ${x0+r} ${top} Q ${x0} ${top} ${x0} ${top+r} L ${x0} ${bottom-r} Q ${x0} ${bottom} ${x0+r} ${bottom} Z`,
      shine: `M ${x0+inset} ${bottom-inset} L ${x0+inset} ${top+inset}`
    };
  }
  function mount(svg, model, initialHeight, {cats = true, motion = true, initialMode = 'swat_down', onChange = () => {}} = {}) {
    const bar = svg.querySelector('#catplotlib-duel-bar path');
    const shine = svg.querySelector('#catplotlib-duel-bar [id^="catplotlib-bubble-shine-"] path');
    if (!bar) throw Error('The interactive bar is missing.');
    svg.querySelectorAll('#catplotlib-cat-duel-lower, #catplotlib-cat-duel-upper').forEach(n => n.remove());
    let height, mode = initialMode === 'arched' ? 'arched' : 'swat_down', animation = null;
    function catGroup(name, id) {
      const group = document.createElementNS(NS, 'g');
      group.setAttribute('id', id);
      const source = new DOMParser().parseFromString(model.poses[name].svg, 'image/svg+xml');
      if (source.querySelector('parsererror')) throw Error('The cat pose could not load.');
      Array.from(source.documentElement.children).forEach(n => group.appendChild(document.importNode(n, true)));
      svg.appendChild(group);
      return group;
    }
    const lower = catGroup('stretch', 'catplotlib-cat-duel-lower');
    const swat = catGroup('swat_down', 'catplotlib-cat-duel-swat');
    const arched = catGroup('arched', 'catplotlib-cat-duel-arched');
    const arm = swat.querySelector('[data-part="swatting-paw"]');
    function place(group, name, x, y, mirror = false) {
      const pose = model.poses[name], scale = pose.size / pose.width;
      group.setAttribute('transform', `translate(${x + (mirror ? 1 : -1) * pose.anchor[0] * scale} ${y - pose.anchor[1] * scale}) scale(${mirror ? -scale : scale} ${scale})`);
    }
    place(lower, 'stretch', model.centerX + model.groundOffset, model.floorY, true);
    function syncMotion() {
      const enabled = cats && motion && mode === 'swat_down';
      if (enabled && !animation && arm) {
        animation = document.createElementNS(NS, 'animateTransform');
        for (const [key, value] of Object.entries({attributeName:'transform',type:'rotate',values:'0 157 91;0 157 91;-15 157 91;7 157 91;-10 157 91;0 157 91;0 157 91',keyTimes:'0;0.36;0.48;0.56;0.65;0.75;1',dur:'2.8s',repeatCount:'indefinite'})) animation.setAttribute(key, value);
        arm.appendChild(animation);
        if (typeof animation.beginElement === 'function') animation.beginElement();
      } else if (!enabled && animation) { animation.remove(); animation = null; }
    }
    function refresh() {
      const y = model.floorY - height * model.pointsPerTreat;
      mode = modeForGap(gapForHeight(model, height), mode, model.closeGap, model.hysteresis);
      const paths = bubbleBarPaths(model, height);
      bar.setAttribute('d', paths.body);
      if (shine) shine.setAttribute('d', paths.shine);
      place(swat, 'swat_down', model.centerX, y);
      place(arched, 'arched', model.centerX, y);
      lower.style.display = cats ? '' : 'none';
      swat.style.display = cats && mode === 'swat_down' ? '' : 'none';
      arched.style.display = cats && mode === 'arched' ? '' : 'none';
      syncMotion();
      onChange({height, mode, cats});
    }
    const controller = {
      setHeight(value) {
        if (!Number.isFinite(Number(value))) throw Error('Height must be a number.');
        height = Math.max(model.minHeight, Math.min(model.maxHeight, Number(value)));
        refresh();
      },
      setCats(value) { cats = Boolean(value); refresh(); },
      setMotion(value) { motion = Boolean(value); syncMotion(); },
      destroy() { if (animation) { animation.remove(); animation = null; } },
      serialize() {
        const clone = svg.cloneNode(true);
        clone.querySelectorAll('animateTransform').forEach(n => n.remove());
        clone.querySelectorAll('[id^="catplotlib-cat-"]').forEach(n => { if (!cats || n.style.display === 'none') n.remove(); });
        return new XMLSerializer().serializeToString(clone);
      }
    };
    controller.setHeight(initialHeight);
    return controller;
  }
  const api = {gapForHeight, modeForGap, bubbleBarPaths, mount};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.CatplotlibDuel = api;
})(typeof window !== 'undefined' ? window : globalThis);
