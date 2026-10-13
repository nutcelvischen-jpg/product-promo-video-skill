---
name: product-promo-video
description: Guides an AI agent to make a professional promo video, in code, for any product that runs in a browser (website, dashboard, 3D digital twin, SaaS) — use the product first, design the story for a specific audience, derive shots from the narration, capture real footage frame by frame, design motion graphics in HTML/GSAP, add voice-over, music and a mix, and render MP4. Use when the user asks for a product video, demo video, promo for clients, or "turn my system into a video". Requires motion-video-skill (render engine).
---

# Product Promo Video — making product videos with code

## What this skill teaches

Not a template — a **method**: how to understand a product, find the story for a particular audience, turn every line of narration into something filmable, and use code to lock picture, type and sound together.

`examples/cnc-twin/` is a complete case study. **Read it to understand decisions, not to reuse them.** Every product has a different audience, selling point, interface and palette. If your video would still work after swapping in the CNC product's name, you copied instead of designing.

## Core principles

1. **User first, director second.** Don't write a line before you've operated the product yourself. A video can only sell what the product really does *and* what a camera can show.
2. **The audience decides everything.** The same product pitches risk and cost to executives, innovation to judges, fun and learnability to students. Structure, tone, length and which features to show all follow from that.
3. **Narration is the clock.** Every cut, animation and music change is tied to line times (`L(i,j)`), never hard-coded seconds. Change a line and the whole film realigns.
4. **Every line must be acted out on screen.** Say "click" — show the click. Say "drops" — show the number drop. Unshown claims are unbelievable claims.
5. **Real footage beats illustration.** Real product footage persuades; motion graphics guide the eye and explain the invisible. They don't replace the product.
6. **One thing at a time.** At most 3 focal elements on screen; use push-ins, dimming and callouts to lead the eye.
7. **Honesty.** Label simulated data, footnote example parameters, put unbuilt features under "next", never invent customers or results. One exaggeration ruins an enterprise video's credibility.
8. **Look at everything.** Open every capture, contact sheet and final frame sample. Never assume the code "should" have worked.

## Tools and responsibilities

| Layer | Tool | What *you* decide |
|---|---|---|
| Render engine (TTS, subtitles, timeline, frame output) | motion-video-skill: `tts.py`, `render.py`, `wide` runtime | voice, tone, format |
| Real footage capture | `scripts/capture.py` + `vt.js` (virtual clock — smooth 30 fps even for 3D) | which shots, which frame each action happens on, camera moves |
| Animation skeleton | `templates/promo-wide/index.html` (footage layer + timing helpers only, **no scenes**) | every scene, layout, text, transition |
| Voice alignment | `scripts/align_timeline.py` | target length, whether to cut lines |
| Sound | `scripts/music.py`, `sfx.py`, `mix.py`, `apple_loops.py` | style, arrangement, where the hits go |
| Review | `scripts/contact_sheet.py`, `render.py --sheet` | your eyes |

`<P>` = this skill folder, `<MV>` = motion-video skill folder. Videos live in `videos/<name>/`.

---

## Workflow

Each step lists what to think through, what it produces, and a checkpoint. Each output feeds the next step.

### 1. Understand the product → `references/01-product-discovery.md`
**Think:** whose problem does it solve? What is its most impressive moment (the money shot)? Which features will be unreadable on video?
Read the docs → run it → operate every feature with Playwright and screenshot → stitch a contact sheet and look.
**Output:** feature list (filmable / needs push-in / unreadable — suggest code change), money-shot candidates, palette and fonts.
**Checkpoint:** report suggested code changes as *recommended / optional / not needed*. Film after the user changes the code.

### 2. Design the story → `references/02-story-design.md`
**Think:** who watches, what should they do afterwards, what is the one-line value proposition, which narrative structure fits (problem→solution, result-first, before/after, day-in-the-life, feature tour, architecture explainer…)?
Don't apply a fixed scene list. Write the message hierarchy first, then pick a structure, then a beat sheet, then lines.
**Output:** `script.json`, with the shot that will act out each line noted beside it.
**Checkpoint:** user approves the lines.

### 3. Design shots → `references/03-shot-design.md`
**Think:** what picture makes each beat believable? Full-screen 3D (cine) or the whole UI (ui)? Which frame must the key action land on?
**Output:** `shots.json`. `--test` capture, review, then full capture (background; do steps 4–5 meanwhile).
**Checkpoint:** every key action happened; every camera move starts and ends well.

### 4. Voice and timing → `references/05-timing-and-sync.md`
`tts.py` (audition one scene first), then `align_timeline.py --target <seconds>`. From then on, that timeline is the clock.

### 5. Visual language and animation → `references/04-visual-language.md`, `05-timing-and-sync.md`
**Think:** what should this film look like? The answer is in the product: reuse its palette, fonts and semantic colors so meaning matches between film and product. What "I don't get it" problem does each scene solve, and which technique leads the eye?
Start from the `new_promo.py` skeleton and **design every scene yourself**. Techniques are a toolbox, chosen by purpose — invent new ones when needed.
**Checkpoint:** `render.py --sheet`, one frame per line, every frame inspected (`references/07-review.md`).

### 6. Sound → `references/06-sound-design.md`
**Think:** music follows the story's emotional curve — restrained pain, opening up at the reveal, space under the key line, a resolved ending. SFX only at real turning points.

### 7. Render, mix, review, deliver
```bash
python <MV>/scripts/render.py videos/<name> --lang en --crf 18
python <P>/scripts/mix.py videos/<name> --lang en --max-mb 30
python <P>/scripts/contact_sheet.py video videos/<name>/out/<name>_en_final.mp4 --every 4
```
At delivery, state length, size, anything dramatized or illustrative the user must confirm, and that they need to listen to it.

---

## Command reference

```bash
pip install playwright numpy pillow imageio-ffmpeg && python -m playwright install chromium   # plus system ffmpeg
python <P>/scripts/new_promo.py videos/<name> --mv <MV>
python <P>/scripts/capture.py videos/<name>/shots.json --out /tmp/test --test
python <P>/scripts/contact_sheet.py clips /tmp/test
python <P>/scripts/capture.py videos/<name>/shots.json --out videos/<name>/assets/clips --jobs 2
set -a; source ~/.openrouter.env; set +a        # key lives in a hidden file on the user's machine — never in the project or chat
python <MV>/scripts/tts.py videos/<name> --lang en [--only s01]
python <P>/scripts/align_timeline.py videos/<name> --mv <MV> --lang en --target 90 [--refresh s03]
python <MV>/scripts/render.py videos/<name> --preview
python <MV>/scripts/render.py videos/<name> --sheet          # or --stills 12.5,40
python <P>/scripts/apple_loops.py list|beats|convert ...      # macOS
python <P>/scripts/music.py videos/<name>/music.json --timeline videos/<name>/timeline_en.json --out videos/<name>/bgm.wav
python <P>/scripts/sfx.py   videos/<name>/sfx.json   --timeline videos/<name>/timeline_en.json --out videos/<name>/sfx.wav
python <MV>/scripts/render.py videos/<name> --lang en --crf 18
python <P>/scripts/mix.py videos/<name> --lang en --max-mb 30
```

## Anti-patterns (stop and rethink)

- Porting the CNC example's scenes, lines, colors or layout and changing the words.
- Writing the script before operating the product.
- Lines describing features the footage doesn't show (or the product can't do).
- The same technique in every scene ("wipe + top-left tag" ×8) — techniques serve content.
- Five tags, two paragraphs and a formula in one frame.
- Hard-coded seconds.
- Text on bright footage without a backing, or on top of the product subject.
- Rendering the final without reviewing the contact sheet.
- Presenting simulated data as real results, or the roadmap as shipped.

## References

| File | Content |
|---|---|
| `references/01-product-discovery.md` | Using the product, money shots, visibility audit, code-change suggestions |
| `references/02-story-design.md` | Audience → message hierarchy → structure → beats → lines; honesty |
| `references/03-shot-design.md` | From lines to shots; cine / ui; actions and camera; `shots.json` spec |
| `references/04-visual-language.md` | Deriving visuals from the product; layout, type, color; technique toolbox |
| `references/05-timing-and-sync.md` | Time model, sync formula, pacing, skeleton API |
| `references/06-sound-design.md` | Voice, music arrangement, SFX, mix |
| `references/07-review.md` | Self-review method and checklist |
| `references/troubleshooting.md` | Common errors |
| `examples/cnc-twin/CASE-STUDY.md` | Why each decision was made — and how it would change for another product |
