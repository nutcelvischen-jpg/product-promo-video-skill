# 03 Design shots: from lines to pictures

## 1. Why frame-by-frame capture, not screen recording
- WebGL on a GPU-less machine runs at a few fps — recordings stutter.
- You can't control *when* a click happens, so syncing to narration is guesswork.
- `capture.py` injects `vt.js` (a virtual clock): the page's `performance.now`, `requestAnimationFrame`, `setTimeout` etc. only advance on `__step()`. Screenshot, advance 1/30 s, repeat → smooth, deterministic 30 fps on any machine.

> Don't use Playwright's `page.clock.install()` — it freezes the browser's own painting and screenshots hang.
> Limits: CSS transitions use real time (look instant when capture is slow); `<video>` and Web Workers aren't controlled.

## 2. Deriving a shot from a beat
For each line ask:
1. **What must viewers see to believe it?** (a state, a change, a relationship)
2. **Where is that in the product?** (3D scene / a panel / a number)
3. **How much context does it need?** (whole UI, or just a region)

| Needed picture | Mode | Later in animation |
|---|---|---|
| scale, wholeness, 3D beauty | `cine` (3D canvas only, full screen) | slow drift, text in empty space |
| a change caused by an action | `ui` (whole interface) | push into where it changes |
| "this is a real system" | `ui` | tilted browser frame or full screen |
| invisible mechanisms (data flow, calculation) | don't film — draw it | diagram, formula, architecture |

One shot, one idea. Film the whole UI; **push in during animation** — no reshoot needed.

## 3. Action timing
- Key action at **frame 20–30**: 0.7–1 s of "before" makes the "after" read.
- Shot length ≥ line length + 2 s (otherwise the last frame freezes). Usually 240–270 frames.
- Note each action's frame — you need it for sync (see 05).
- Before/after: one shot with the action in the middle beats two shots.

## 4. Camera (cine shots)
- Orbit with a mouse drag (OrbitControls: ~1080 px ≈ 360°). ≤ 70° (~200 px) avoids swinging behind the model.
- Start *and* end frames must be good compositions — check first/middle/last with `--test`.
- When switching camera presets, click at frame 4–6 so the fly-in is recorded; start dragging after it lands.
- Speed: machines/characters at the product's 1× look natural; UI shots where numbers must move can run faster.

## 5. shots.json spec
```jsonc
{
  "url": "http://localhost:8766/",
  "viewport": [1920, 1080], "fps": 30, "quality": 80,
  "warmup": 45, "load_wait_ms": 1200,
  "clear_storage": true, "local_storage": {"k": "v"},
  "channel": "chrome", "gpu": true,          // optional: local Chrome + GPU on a Mac (5–10× faster)
  "cine": { "container": ".scene-panel", "canvas_host": "#canvas-wrap", "background": "#101820", "extra_css": "" },
  "ui_css": "", "setup": [],
  "shots": {
    "<name>": { "mode": "cine" | "ui", "frames": 255, "setup": [], "actions": [], "css": "", "url": "", "warmup": 45 }
  }
}
```

### Actions
| Action | JSON | Notes |
|---|---|---|
| Click by text | `{"at": 20, "click": "Label"}` | exact match first, then prefix; also aria-label/title; `"scope"` changes the selector set |
| Click by selector | `{"at": 20, "click_sel": "#id"}` | for duplicate labels |
| Orbit | `{"drag": 200, "dy": 0, "from": 0, "to": 254, "x0": 960, "y": 540}` | smoothstep; `"ease": false` linear |
| Wheel zoom | `{"zoom": -300, "from": 0, "to": 60}` | negative = in |
| Typing | `{"type": {"selector": "#name", "value": "text"}, "at": 40, "cps": 10}` | clear with fill first |
| Fill | `{"at": 40, "fill": {"selector": "#name", "value": ""}}` | fires input/change |
| Select | `{"select": {"selector": "select", "index": -1, "label": "3×"}}` | |
| JS | `{"at": 10, "eval": "..."}` | |
| Key | `{"at": 10, "key": "Escape"}` | |

## 6. Workflow
```bash
python <P>/scripts/capture.py shots.json --out /tmp/test --test
python <P>/scripts/contact_sheet.py clips /tmp/test
python <P>/scripts/capture.py shots.json --out videos/<name>/assets/clips --jobs 2
```
"找不到按鈕文字" in the log = button not found. Without a GPU: 1–2.5 s/frame for full-screen 3D, ~1 s/frame for UI — run in background. Re-shoot some: `--only a,b`.
