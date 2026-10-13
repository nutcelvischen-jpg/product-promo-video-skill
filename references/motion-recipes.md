# Motion recipes & sync formulas (promo-wide template)

Built on motion-video-skill's `wide` runtime, so `c.rise`, `c.out`, `c.count`, `c.tilt`, `c.sheen`, `c.wipe` all work (see `<MV>/references/animation-cookbook.md`). Below is what this skill adds.

## 1. Footage layers `.clip`
```html
<div id="c_power" class="clip"><img data-clip="power" data-n="255" src="assets/clips/power/0000.jpg"></div>
```
- `data-clip` = shot folder, `data-n` = frame count.
- **Later in the DOM = on top**: order clips by appearance.
- Add `.shade` gradients inside a clip to make text readable.

```js
clip("#c_power", t0, t1, skip = 0)
```
Shows frame `skip` at t0, advances 30 fps, holds the last frame; auto-hides at t1 + 0.6 s (so the next cut-in has something underneath). For a thumbnail use `clip("#twin img", ...)`.

`tick()` swaps frames; the final `__seek` override waits for each new frame to decode — **keep both**.

## 2. Sync formula (most important)
Action at frame F should land at time T:
```js
clip(sel, T - F / 30, t1);
```
Cloud scenario clicked at frame 30, to land right after the question (≈22% into the line):
```js
clip("#c_cloud", Math.min(LM(4, 0, .22) - 1.0, S(4).start - .3), L(4, 1) + .3);
```

## 3. Transitions
| Move | Code | Use |
|---|---|---|
| Wipe | `cutIn(sel, t, .8)` | between shots, 0.35 s before the next line |
| Circle reveal | `clipPath circle(0%→120%)` | first product appearance |
| Fade | `fadeIn` / `fadeOut` | open, close, dims |
| Flash | `#flash` 0.2 s in, 1 s out | title/logo hits (with boom SFX) |
| Dim | `#dimAll` | before big words |

## 4. Camera moves
| Move | Code | Notes |
|---|---|---|
| Push-in | `zoomTo(sel, x, y, 1.85, t, 1.6)` | (x, y) on the 1920×1080 frame; start 0.5 s after the click |
| Drift | `drift(sel, t, d, 1.05, 1.18)` | slow Ken Burns on cine shots |
| Reframe | `fromTo(sel+" img",{x:330},{x:0})` | push the 3D subject right while text sits left |
| Browser frame | `c.tilt("#win", t)` with `<img data-clip="ui">` | first full-UI reveal feels more "product" |

## 5. Text
| Element | HTML | Animation |
|---|---|---|
| Pain card + counter | `.card.glass .big` | `c.rise` + `c.count` |
| Question pills | `.tag` (`.amber/.blue/.coral`) | `pop` at `LM(i,j,.02/.36/.68)` |
| Big words | `.kin > .w × 2` | `words(sel, t, .45)` |
| Scene tag | `.tag` at `left:72px;top:170px` | `pop`, `c.out` before next line |
| Callouts | `.callout .lb small` | slide in after push-in, with `#coShade` |
| Formula card | `.card.glass .eb/.eq/.foot` | `c.rise` + `c.sheen`; footnote example factors |
| KPI cards | `.tc.glass × 3` | `c.rise(".tc")` + bars + sheen |
| Architecture | SVG paths + dots moved in `tick()` | see `examples/cnc-twin` `#iot` |
| Logo end card | `#logo` | blur-in → line → tagline → disclaimer |

## 6. Layout rules
- Top 140 px brand bar, bottom 160 px subtitles.
- ≤ 3 focal elements; remove the previous line's tag before the next line.
- Text over footage always needs a backing (`.shade`, `#coShade`, dark `.card` — not translucent glass over a bright floor).
- `.glass` sets `position:relative` → absolutely-positioned cards need `position:absolute!important` (`.card` handles it).
- Containers without `.abs` (`#title`, `#logo`) need `position:absolute` in CSS.
- Don't put big words over the 3D subject.

## 7. Color
Reuse the product's semantic colors so meaning matches between film and product. `--gold` is the runtime accent → set to the product primary; `--glow-rgb` tints the bokeh.
