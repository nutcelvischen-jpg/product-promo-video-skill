# 06 Sound design

Sound makes viewers *feel* the story's shape without competing with the narration.

## 1. Voice
- Generate scene 1 only (`tts.py --only s01`) and let the user approve accent, pace, emotion.
- Accent: state it explicitly in `style`.
- Mispronunciations: `["spoken", "displayed"]`; spell acronyms with spaces.
- Flat delivery: concrete per-scene `dir` (suspense, brighter, emphasis, slower).
- Length: `align_timeline.py --target` (see 05).

## 2. Music follows the emotional curve
| Story phase | Music |
|---|---|
| tension, questions | one layer of melody or pad, low-passed ("muffled") |
| turn, reveal | filter opens, bass and drums enter; downbeat on the key visual moment |
| build, demo | steady groove; add a layer mid-way for momentum |
| key line | drop drums or level for 1–2 bars so the line is heard |
| outro | rhythm out first, melody stays, fade |

`music.py` arranges loops: each track's `gain` and `lowpass` are `[time, value]` polylines with narration-bound expressions (`S(1)+0.1`, `L(4,2)+2*BAR`, `END-3`); `anchor` puts a downbeat on a chosen time.
```jsonc
{ "bpm": 100, "anchor": "<reveal time>", "peak": 0.89,
  "tracks": [ { "file": "loops/xxx.wav", "gain": [[0,0],["S(1)",0.7],["END",0]], "lowpass": [[0,500],["S(1)",18000]] } ] }
```

## 3. Sources
- **Apple Loops (GarageBand on macOS)**: ~1,700 loops, royalty-free in your own productions (loop files may not be redistributed). `apple_loops.py list / beats / convert`.
  - A "family" (same name prefix: `XXX Bass`, `XXX Synth`) shares tempo and key — stack freely.
  - Tempo from length: 9.6 s = 4 bars @ 100 BPM, 8.0 s = 4 bars @ 120 BPM; drums ½× or 1× the melody length.
- User's own licensed track: one track in music.json, shaped with gain.
- Match the audience: enterprise/tech calm and low-intensity; startups upbeat; education warm/acoustic. Avoid vocal loops.
- Can't audition? Compare RMS and spectral centroid with numpy (higher = harsher) — then **have the user listen**.

## 4. SFX (`sfx.py`, synthesized, no licensing)
| Type | Use |
|---|---|
| whoosh | main transitions; peak on the cut (`offset` ≈ −0.25) |
| boom | 2–4 hits per film: reveal, title, logo |
| tick | small elements appearing |
| riser | before a big turn (optional) |

Less is more — only real turning points.

## 5. Mix (`mix.py`)
Voice (HPF + compression), music (side-chain ducked under the voice), SFX → loudnorm.
`--music` 0.25 wordy – 0.35 sparse; `--lufs` −14…−16 web, −16…−18 meeting rooms. Check loudness, no clipping; **user listens**.
