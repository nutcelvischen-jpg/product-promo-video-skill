/* 虛擬時鐘（Virtual Time）— 由 capture.py 在頁面載入前注入。
 * 取代 performance.now / Date.now / requestAnimationFrame / setTimeout / setInterval，
 * 頁面上的動畫只會在呼叫 window.__step(ms) 時前進，所以每一格畫面都可以慢慢截圖、又保持平順。
 * 注意：CSS transition/animation 仍用真實時間（截圖慢時會「瞬間完成」），通常沒關係。
 */
(() => {
  let vt = 0, q = [], id = 0, timers = [], tid = 1e6;
  const D0 = Date.now();
  performance.now = () => vt;
  Date.now = () => D0 + vt;
  window.requestAnimationFrame = cb => { q.push([++id, cb]); return id; };
  window.cancelAnimationFrame = i => { q = q.filter(e => e[0] !== i); };
  window.setTimeout = (fn, ms = 0, ...a) => { const i = ++tid; timers.push({ i, at: vt + (+ms || 0), fn, a }); return i; };
  window.clearTimeout = i => { timers = timers.filter(t => t.i !== i); };
  window.setInterval = (fn, ms = 0, ...a) => { const i = ++tid; const every = Math.max(1, +ms || 0); timers.push({ i, at: vt + every, fn, a, every }); return i; };
  window.clearInterval = window.clearTimeout;
  window.__step = (ms) => {
    vt += ms;
    let guard = 0;
    while (guard++ < 1000) {
      const due = timers.filter(t => t.at <= vt).sort((a, b) => a.at - b.at)[0];
      if (!due) break;
      if (due.every) due.at += due.every; else timers = timers.filter(t => t !== due);
      try { typeof due.fn === "function" ? due.fn(...due.a) : (0, eval)(due.fn); } catch (e) { console.error(e); }
    }
    const cur = q; q = [];
    for (const [, cb] of cur) { try { cb(vt); } catch (e) { console.error(e); } }
    return vt;
  };
})();
