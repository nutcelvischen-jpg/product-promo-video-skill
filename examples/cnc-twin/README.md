# Example: CNC factory digital twin promo (enterprise, 90 s)

Product: a Three.js CNC factory digital twin (simulated production, power, solar, carbon). Audience: enterprise clients. Sign-off: ICMA Lab. Narration is Traditional Chinese (Taiwan); the structure is language-independent.

| File | Content |
|---|---|
| `script.json` | 8-scene marketing script (pain → reveal → feature → layers → scenarios → carbon → scale → sign-off) |
| `shots.json` | 10 shots: 5 cine (full-screen 3D) + 5 UI |
| `index.html` | Full animation (tilted browser frame, push-ins + callouts, formula card, KPI cards, IoT diagram, logo) |
| `music.json` | Apple Loops "Forward Progress" Synth/Bass/Guitar + "Matchbox Beat 01", 100 BPM |
| `sfx.json` | 11 whooshes, 3 booms, 3 ticks |

Reproduce (needs the factory-twin app at http://localhost:8766):
```bash
python <P>/scripts/new_promo.py videos/cnc-twin --mv <MV>
cp <P>/examples/cnc-twin/*.json <P>/examples/cnc-twin/index.html videos/cnc-twin/
python <P>/scripts/capture.py videos/cnc-twin/shots.json --out videos/cnc-twin/assets/clips --jobs 2
python <MV>/scripts/tts.py videos/cnc-twin --lang zh
python <P>/scripts/align_timeline.py videos/cnc-twin --mv <MV> --target 90
python <MV>/scripts/render.py videos/cnc-twin --preview && python <MV>/scripts/render.py videos/cnc-twin --sheet
python <P>/scripts/music.py videos/cnc-twin/music.json --timeline videos/cnc-twin/timeline_zh.json --out videos/cnc-twin/bgm.wav
python <P>/scripts/sfx.py videos/cnc-twin/sfx.json --timeline videos/cnc-twin/timeline_zh.json --out videos/cnc-twin/sfx.wav
python <MV>/scripts/render.py videos/cnc-twin --lang zh --crf 18
python <P>/scripts/mix.py videos/cnc-twin --lang zh --max-mb 30
```

Lessons baked into the skill:
- Layer changes were invisible at small size → the product was updated with stronger 3D colors and particles before filming.
- "場外太陽能" was both a list item and a camera button → exact text match first.
- `.glass` `position:relative` pushed the formula card off-screen → `.card` forces absolute.
- TTS ran 6% long → `align_timeline.py --target 90`.
