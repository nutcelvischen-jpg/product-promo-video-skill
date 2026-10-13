# 05 Timing and sync: narration is the clock

## 1. Time model
```
script.json ──tts.py──▶ audio_<lang>/sNN.wav ──align_timeline.py──▶ timeline_<lang>.json ──render.py --preview──▶ _tl.js
                                                                              │
                                     index.html reads it via S(i) / L(i,j) / LM(i,j,k)
```
- `align_timeline.py` speeds the voice to a target length (`atempo`, pitch preserved) and snaps sentence boundaries to real pauses. 0.95–1.08 is inaudible; above 1.12, cut lines.
- After redoing a scene: `tts.py --only s03` → `align_timeline.py ... --refresh s03`.

## 2. Time functions
| Function | Meaning |
|---|---|
| `S(i).start` | scene i start (0-based) |
| `L(i, j)` / `LE(i, j)` | line j of scene i start / end |
| `LM(i, j, k)` | k fraction through that line |
| `c.TL.total` | total length |

**Never hard-code seconds.**

## 3. Skeleton helpers
```js
clip(sel, t0, t1, skip = 0)    // footage: frame `skip` at t0, then 30 fps; holds last frame; auto-hides at t1+0.6
cutIn(sel, t, d)               // wipe transition
zoomTo(sel, x, y, scale, t, d) // push-in around (x,y) in original 1920×1080 coordinates
drift(sel, t, d, s0, s1)       // slow Ken Burns
fadeIn / fadeOut / pop / words // basics; words = two-line kinetic type
```
Plus the `wide` runtime's `c.rise`, `c.out`, `c.count`, `c.tilt`, `c.sheen`, `c.wipe`, `c.type`. Anything else: write `c.m.fromTo(...)` directly (third argument is time).

Footage element:
```html
<div id="c_xxx" class="clip"><img data-clip="xxx" data-n="255" src="assets/clips/xxx/0000.jpg"></div>
```
`data-n` = frame count. Later in DOM = on top; order by appearance. Keep `tick()` and the final `__seek` override (waits for each new frame to decode).

## 4. The sync formula
Action at frame F should land at time T:
```js
clip(sel, T - F / 30, t1);
```
If t0 would be later than when the shot appears, use `Math.min(T - F/30, appearTime)`.

Choosing T:
- Answer to a question must be *seen*: T right after the question ends (~20–30% into the line).
- Action lines ("one click shows…"): T on the verb.
- Number changes: 0.2–0.4 s before the number is spoken — eyes arrive first.

## 5. Pacing
- Elements appear on their line, or 0.1–0.3 s early.
- Transitions start 0.3–0.4 s before the next line so picture and words arrive together.
- Clear a beat's elements 0.3–0.5 s before the next beat.
- Pauses between lines are breathing room — big moves (push-ins, reveals) work best there.
- Hold the end logo ≥ 2 s (motion-video leaves 2.6 s of tail).

## 6. Preview
```bash
python <MV>/scripts/render.py videos/<name> --sheet
python <MV>/scripts/render.py videos/<name> --stills 12.5,40
```
Browser: `index.html?play` (loop), `?t=12.5` (freeze).
