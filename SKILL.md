---
name: product-promo-video
description: Turn any product that runs in a browser (website, dashboard, 3D digital twin, SaaS) into an agency-grade landscape promo video — marketing script, real product footage captured frame by frame, push-ins and callouts, AI voice-over, music and sound design — rendered to MP4. Use when the user asks for a product video, demo video, promo for clients, or "record my system and make it a video". Requires motion-video-skill.
---

# Product Promo Video Skill — turn a web product into a professional promo

This skill extends [motion-video-skill](https://github.com/nutcelvischen-jpg/motion-video-skill/tree/en):
motion-video is the engine (animation + TTS + rendering); this skill adds **real product footage** and **marketing craft**.

| Adds | With |
|---|---|
| Real UI / 3D / WebGL footage, captured frame by frame at a smooth 30 fps | `scripts/capture.py` + `scripts/vt.js` (virtual clock) |
| Agency script structure (pain → reveal → features → scenarios → value → sign-off) | `references/storyboard-marketing.md` |
| Push-ins, callouts, transitions, logo end card | `templates/promo-wide/index.html` |
| Voice-over speed-up + sentence alignment to real pauses | `scripts/align_timeline.py` |
| Music from loops, synthesized SFX, broadcast-style mix | `scripts/music.py`, `sfx.py`, `mix.py` |
| Contact sheets for review | `scripts/contact_sheet.py` |

Full example: `examples/cnc-twin/` (CNC factory digital twin, 90 s, enterprise audience, signed ICMA Lab).

`<P>` = this skill folder, `<MV>` = motion-video skill folder. Run everything from the **workspace root**; videos live in `videos/<name>/`.

---

## Pipeline (in order — each step has a checkpoint)

```
0 setup → 1 use the product → 2 script (user approves) → 3 scaffold → 4 shot list + test capture → 5 capture
→ 6 voice + align → 7 animate → 8 contact-sheet review → 9 music + SFX → 10 render + mix → 11 final review → 12 deliver
```

Rough time for 90 s: script 15 min, capture 20–60 min (background), animation 30–60 min, render 10–15 min.

---

## Step 0: Setup

```bash
git clone -b en https://github.com/nutcelvischen-jpg/motion-video-skill .agents/skills/motion-video
pip install playwright numpy pillow imageio-ffmpeg && python -m playwright install chromium
python <MV>/scripts/check_env.py
ffmpeg -version     # mix.py / align_timeline.py need system ffmpeg
```
- TTS key via env var `OPENROUTER_API_KEY` (or `GEMINI_API_KEY`). **Never write it into files or the chat.** Ask the user to store it in a hidden file (`~/.openrouter.env`, `chmod 600`) and load with `set -a; source ~/.openrouter.env; set +a`.
- Homebrew Python on macOS showing `CERTIFICATE_VERIFY_FAILED`: `export SSL_CERT_FILE=/etc/ssl/cert.pem`.
- Cloud sandboxes often cannot reach the TTS API or Google Fonts: run TTS on the user's machine; use local fonts (the template ships Manrope + Noto Sans CJK fallback).

## Step 1: Use the product first (never skip)

Goal: know what is worth filming and what will be unreadable on video.

1. Read the product's `README.md` / `PRODUCT.md` / `DESIGN.md`: features, palette, fonts, real vs. simulated data.
2. Serve it: static `cd dist && python -m http.server 8766`; Vite: `npm run build` then the same (or `npm run dev`).
3. Open it with Playwright and **list every button label** (you'll need them for the shot list).
4. Click through each main feature, screenshot, stitch a contact sheet and look at it. Watch for:
   - **Features whose change is barely visible** (e.g. a layer that only tints slightly) → push in on video, or suggest a code change for more contrast.
   - **Camera presets that barely differ** → use mouse-drag orbits (`drag` in capture.py).
   - **The selector of the 3D canvas container** (e.g. `.scene-area` / `#scene`) → needed for full-screen "cine" shots.
   - Toasts, modals, logins, state persisted in localStorage.
5. Report to the user in three buckets — *recommended changes / optional / no change needed* — with reasons. **Film after they change the code**, or you'll re-shoot.

## Step 2: Marketing script (user approves lines before moving on)

Read `references/storyboard-marketing.md`. Defaults if not specified:

| Item | Default |
|---|---|
| Length | 90 s (≈ 210–230 English words / 330–360 Chinese characters) |
| Audience | Enterprise decision makers |
| Voice | `Charon`/`Aoede` (en) or `Leda` (Taiwanese Mandarin) + "keynote narrator: calm, professional, confident" |
| Sign-off | The user's lab / company |

Standard 8-scene structure: **pain hook → product reveal → core feature → how it works / layers → scenario simulation → quantified value → scale & roadmap → tagline + sign-off**.

Rules:
- One idea per line; for TTS pronunciation use `["spoken", "displayed"]` (e.g. `["C N C", "CNC"]`, `["three D", "3D"]`).
- **Honesty**: label simulated data on screen; footnote example coefficients; future features only as "next"; never invent customers or results. If the hook uses a dramatized number, tell the user at delivery.
- Next to each line, note which shot covers it — and the shot must be capturable from the real product.

## Step 3: Scaffold

```bash
python <P>/scripts/new_promo.py videos/<name> --mv <MV>
```
Put the approved lines in `script.json`; set `:root` colors in `index.html` to the product palette; put the product font in `assets/fonts/`.

## Step 4: Shot list + test capture

Read `references/capture-guide.md`. Edit `shots.json`:

- `mode: "cine"` — 3D canvas only, full screen (reveal, layers, cinematic orbits).
- `mode: "ui"` — the whole interface (clicks, numbers changing, forms); push in later in the animation.
- Actions at frame N (30 frames = 1 s): `click` (button text), `drag` (orbit), `type` (typing), `fill`, `select`, `eval`.
- 240–270 frames per shot; **put the key action at frame 20–30** so it is easy to sync.

```bash
python <P>/scripts/capture.py videos/<name>/shots.json --out /tmp/test_clips --test
python <P>/scripts/contact_sheet.py clips /tmp/test_clips      # open sheet_clips.jpg
```
Check the clicks happened (log prints "找不到按鈕文字" = button not found), orbits don't swing behind the model, toasts/modals behave.

## Step 5: Capture (background)

```bash
nohup python <P>/scripts/capture.py videos/<name>/shots.json --out videos/<name>/assets/clips --jobs 2 > capture.log 2>&1 &
```
- No GPU: 1–2.5 s/frame for full-screen 3D, ~1 s/frame for UI → 30–60 min. **Do steps 6–7 meanwhile.**
- Mac with GPU: add `"channel": "chrome", "gpu": true` → 5–10× faster.
- Always review with `contact_sheet.py clips`.

## Step 6: Voice-over + alignment

```bash
python <MV>/scripts/tts.py videos/<name> --lang en --only s01   # audition one scene
python <MV>/scripts/tts.py videos/<name> --lang en
python <P>/scripts/align_timeline.py videos/<name> --mv <MV> --lang en --target 90
python <MV>/scripts/render.py videos/<name> --preview
```
- TTS usually runs 5–10% long; `--target` computes the speed-up (0.95–1.08 is inaudible; above 1.12 cut lines instead).
- Sentence boundaries snap to real pauses so cuts land precisely.
- After re-doing one scene: `tts.py --only s03` then `align_timeline.py ... --refresh s03`.

## Step 7: Animate (index.html)

Read `references/motion-recipes.md`, then `examples/cnc-twin/index.html`.

- Each shot is a `.clip`; `clip(sel, t0, t1, skip)` = "show frame `skip` at t0"; `tick()` swaps frames.
- **Tie every time to the narration**: `S(i).start`, `L(i,j)`, `LM(i,j,k)` — never hard-code seconds.
- Sync rule: action at frame F, should land at time T → `clip(sel, T - F/30, ...)`.
- Transitions `cutIn`; push-ins `zoomTo(sel, x, y, scale, t)`; slow drift `drift`.
- Max 3 focal elements at once; keep the bottom 160 px for subtitles; keep the "demo · simulated data" tag while product footage is on screen.

## Step 8: Contact-sheet review (repeat until clean)

```bash
python <MV>/scripts/render.py videos/<name> --sheet
python <MV>/scripts/render.py videos/<name> --stills 41.5,68
```
**Open and look.** Use `references/qa-checklist.md`. Usual bugs: a previous clip not hidden, cards pushed off-screen (`.glass` position conflict), text over the 3D subject, subtitles covered.

## Step 9: Music + SFX

Read `references/audio-guide.md`.
```bash
python <P>/scripts/apple_loops.py list --genre Chillwave          # macOS only
python <P>/scripts/apple_loops.py beats --bars-of 9.6
python <P>/scripts/apple_loops.py convert "07 Chillwave/Forward Progress Synth" "07 Chillwave/Forward Progress Bass" "07 Chillwave/Matchbox Beat 01" --out videos/<name>/loops
python <P>/scripts/music.py videos/<name>/music.json --timeline videos/<name>/timeline_en.json --out videos/<name>/bgm.wav
python <P>/scripts/sfx.py   videos/<name>/sfx.json   --timeline videos/<name>/timeline_en.json --out videos/<name>/sfx.wav
```
Key moves: `anchor` puts a downbeat on the reveal; low-pass the intro and open it at the reveal; drop the drums for two bars under the key line; strip down for the outro.

## Step 10: Render + mix

```bash
python <MV>/scripts/render.py videos/<name> --lang en --crf 18 --workers 2
python <P>/scripts/mix.py videos/<name> --lang en --max-mb 30
```
`--crf 18` keeps UI detail sharp (~30 MB for 90 s). mix.py: compressed voice, side-chain-ducked music, SFX, loudnorm −15 LUFS → `out/<name>_en_final.mp4` (+ `_small.mp4` if over `--max-mb`).

## Step 11: Final review

```bash
python <P>/scripts/contact_sheet.py video videos/<name>/out/<name>_en_final.mp4 --every 4
```
Every frame matches its subtitle, no black frames at cuts, logo appears, length on target. **Ask the user to listen** — accent, mispronunciations, music level.

## Step 12: Deliver

Final MP4 (or `_small.mp4`), the project sources (`index.html`, `script.json`, `shots.json`, `music.json`, `sfx.json`, timeline). `assets/clips/` is large and can be re-captured. Report length, size, loudness, anything dramatized/illustrative the user must confirm, and next options (other language, 15 s cut, vertical).

---

## Top 5 problems (more in `references/troubleshooting.md`)
1. **Screenshot hangs** — Playwright `page.clock` was used; use `vt.js` (capture.py does).
2. **A frame shows the previous image** — the `__seek` override at the end of index.html was removed.
3. **Card in the wrong place** — `.glass` sets `position:relative`; cards need `position:absolute!important`.
4. **Wrong button clicked** — exact text match wins, then prefix; for duplicates use `click_sel`.
5. **Action out of sync** — clip `t0` didn't subtract `frame / 30`.

## File map
```
<P>/
├── SKILL.md
├── scripts/  new_promo.py · capture.py + vt.js · align_timeline.py · music.py · apple_loops.py · sfx.py · mix.py · contact_sheet.py · ppvslib.py
├── templates/promo-wide/   index.html · script.json · shots/music/sfx.json · fonts
├── examples/cnc-twin/      full 90 s enterprise example (Traditional Chinese narration)
└── references/  storyboard-marketing · capture-guide · motion-recipes · audio-guide · qa-checklist · troubleshooting
```
