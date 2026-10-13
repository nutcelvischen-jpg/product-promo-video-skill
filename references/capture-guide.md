# Capturing product footage (capture.py)

## 1. Why not screen recording
- WebGL on a machine without a GPU runs at single-digit fps → stuttering recordings.
- You can't control *when* a click happens, so syncing to narration is guesswork.
- This skill uses a **virtual clock**: `vt.js` replaces `performance.now`, `Date.now`, `requestAnimationFrame`, `setTimeout`, `setInterval` before the page loads. Page time only advances on `__step(33.33)`; screenshot, then step again → smooth, deterministic 30 fps on any hardware.

> ⚠ Don't use Playwright's `page.clock.install()` — it freezes the browser's own frame scheduling and `page.screenshot()` hangs forever.

Limits: CSS transitions/animations still use real time (they appear instant when capture is slow — usually fine); `<video>` elements and Web Worker timers are not controlled.

## 2. shots.json

```jsonc
{
  "url": "http://localhost:8766/",
  "viewport": [1920, 1080], "fps": 30, "quality": 80,
  "warmup": 45,                          // frames run before recording
  "load_wait_ms": 1200,
  "clear_storage": true,                 // clear localStorage before each shot
  "local_storage": {"key": "value"},     // preset state (token, setting)
  "channel": "chrome", "gpu": true,      // optional: local Chrome + GPU on a Mac
  "cine": {                              // full-screen 3D mode
    "container": ".scene-area",          //   3D panel wrapper
    "canvas_host": "#scene",             //   element holding <canvas> (siblings get hidden)
    "background": "#18242a", "extra_css": ""
  },
  "ui_css": "#toast{transition:none!important}",
  "setup": [ ... ],                      // actions before every shot
  "shots": {
    "<name>": {
      "mode": "cine" | "ui",
      "frames": 255,                     // 30 = 1 s; use 240–270
      "setup": [ ... ],                  // before warm-up, not recorded
      "actions": [ ... ],                // during recording
      "css": "", "url": "", "warmup": 45, "quality": 80
    }
  }
}
```
Find the container:
```js
let e=document.querySelector('canvas'),out=[];while(e){out.push(e.tagName+'#'+e.id+'.'+[...e.classList].join('.'));e=e.parentElement}out
```
Usually the panel two levels above the canvas is `container`, the canvas's parent is `canvas_host`.

## 3. Actions

| Action | JSON | Notes |
|---|---|---|
| Click by text | `{"at": 20, "click": "Cloud cover"}` | exact match first, then prefix; also aria-label/title; `"scope"` to change selector set |
| Click by selector | `{"at": 20, "click_sel": "#export"}` | for duplicate labels |
| Orbit drag | `{"drag": 220, "dy": 0, "from": 0, "to": 254, "x0": 860, "y": 540}` | OrbitControls: 1080 px ≈ 360°, so 220 px ≈ 70°. smoothstep by default; `"ease": false` for linear |
| Wheel zoom | `{"zoom": -300, "from": 0, "to": 60}` | negative = zoom in |
| Typing | `{"type": {"selector": "#name", "value": "CNC-07"}, "at": 42, "cps": 10}` | clear with fill first |
| Fill | `{"at": 40, "fill": {"selector": "#name", "value": ""}}` | fires input/change (React/Vue safe) |
| Select | `{"select": {"selector": "select", "index": -1, "label": "3×"}}` | index -1 = last |
| JS | `{"at": 10, "eval": "..."}` | |
| Key | `{"at": 10, "key": "Escape"}` | |

## 4. Shot design
1. One shot = one idea = one line.
2. **Key action at frame 20–30**: ~1 s of "before" so the "after" reads.
3. Length = line length + 2 s (otherwise the last frame freezes).
4. Cine orbits: ≤ 70°; good start *and* end frames (check frames 0/135/254 with `--test`). For camera presets, click at frame 4–6 so the fly-in is recorded; start dragging at 80–90.
5. Film the whole UI; **do push-ins in the animation** (`zoomTo`).
6. Simulation speed: 1× for cine (natural machine motion), 3× for UI where numbers should move.
7. For before/after, one shot with the action in the middle beats two shots.

## 5. Speed
| Environment | Full-screen 3D | UI |
|---|---|---|
| Cloud / no GPU (SwiftShader) | 1–2.5 s/frame | 0.8–1 s/frame |
| Mac + `"channel":"chrome","gpu":true` | 0.1–0.2 s/frame | 0.1 s/frame |

`--jobs 2` parallel browsers; `--only a,b` re-shoot; `nohup ... &` + `tail capture.log`.

## 6. Review
`python contact_sheet.py clips videos/<name>/assets/clips` → 4 frames per shot. Action happened, no error screens, good orbit ending, toasts not covering the point.
