# Sound: voice, music, SFX, mix

## 1. Voice (motion-video-skill tts.py)
1. Audition scene 1 only (`--only s01`) and let the user approve accent and pace.
2. Generate all, then `align_timeline.py --target 90`:
   - computes an `atempo` speed-up (pitch preserved). 0.95–1.08 is inaudible; > 1.12 → cut lines.
   - snaps sentence starts to real pauses (tts.py only estimates by length).
3. Fixes: wrong accent → state it in `style`; mispronunciations → `["spoken", "displayed"]`; flat delivery → concrete `dir` per scene.

## 2. Music: Apple Loops (macOS)
GarageBand ships ~1,700 Apple Loops (`/Library/Audio/Apple Loops/Apple/`), royalty-free for use in your own productions (the loop files themselves may not be redistributed).

1. `apple_loops.py list --genre Chillwave` → pick one **family** (e.g. Forward Progress Bass / Synth / Guitar): same tempo and key.
2. Tempo from length: 9.6 s = 4 bars @ 100 BPM; 8.0 s = 4 bars @ 120 BPM.
3. `apple_loops.py beats --bars-of 9.6` → drum loops of 4.8 / 9.6 s.
4. `apple_loops.py convert ... --out videos/x/loops`.

| Tone | Folder | Note |
|---|---|---|
| Enterprise / tech / industrial | 07 Chillwave | steady, modern; avoid Vox |
| Startup / upbeat | 02 Electro House, 08 Indie Disco | simpler drum loops |
| Warm / education | Apple Loops for GarageBand (acoustic, piano) | |

Can't audition? Compare RMS and spectral centroid with numpy (higher centroid = harsher); pick calmer drums for enterprise — and **have the user listen**.

## 3. Arrangement (music.json)
| Section | Move |
|---|---|
| Pain hook | melody only, low-pass 500→2600 Hz (muffled tension) |
| Reveal | `anchor` = reveal time → downbeat lands there; filter opens; bass + drums enter (with boom) |
| Features | melody + bass + drums; add a third layer after "how it works" |
| Key line | drop drums for two bars (`L(i,j)` → `L(i,j)+2*BAR`) |
| Outro | drums out, melody + bass, 3 s fade |

`gain` / `lowpass` are `[time, value]` polylines; times accept `S(1)+0.1`, `L(4,2)+2*BAR`, `END-3`.

## 4. SFX (sfx.json)
| Type | Use | Gain |
|---|---|---|
| whoosh 0.6–0.8 s | every wipe; `offset: -0.25`; `alt_pan` | 0.14–0.2 |
| boom | reveal, title flash, logo | 0.35–0.5 |
| tick | pills/tags popping | 0.2 |
| riser 2 s | before a big turn (optional) | 0.15 |

All synthesized — no licensing. Main cuts + three hits is enough.

## 5. Mix (mix.py)
```
voice → HPF 80 Hz → comp 3:1 ─┬──────────────────────┐
                              └→ sidechain key ─┐      ├→ amix → loudnorm(-15 LUFS, TP -1.5) → AAC 192k
music × 0.30 ──────────→ sidechaincompress ─────┘      │
sfx ───────────────────────────────────────────────────┘
```
`--music` 0.25 (wordy) – 0.35 (sparse). `--lufs` −14…−16 web, −16…−18 meeting rooms.
