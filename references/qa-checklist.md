# QA checklist

## A. Script (before user approval)
- [ ] Pain or contrast within 3 s
- [ ] One idea per line; acronyms have pronunciation fixes
- [ ] Every line has a shot that can be captured from the real product
- [ ] Simulated data, example factors and future features honestly labeled
- [ ] Opening and ending echo; sign-off and CTA present
- [ ] Word count fits length (90 s ≈ 210–230 words)

## B. Shots (`contact_sheet.py clips`)
- [ ] Every key action happened (no "button not found" in the log)
- [ ] Orbits start and end well, no back side or clipping
- [ ] Enough frames (line length + 2 s)
- [ ] No dev tools, errors or private data

## C. Animation (`render.py --sheet`, look at every frame)
- [ ] Footage matches each subtitle
- [ ] Previous clips hidden; nothing covers big words or the logo
- [ ] Cards/tags where intended (no `.glass` relative push)
- [ ] Text inside boxes, readable, not over the 3D subject or bright floors
- [ ] Subtitle zone clear
- [ ] Push-ins don't crop the key panel
- [ ] "Demo · simulated data" visible during product footage
- [ ] Logo fully visible ≥ 2 s

## D. Sound
- [ ] Length on target (±1 s)
- [ ] Downbeat on reveal; drums drop under the key line
- [ ] Integrated loudness −14…−16 LUFS
- [ ] **User listened**: accent, pronunciation, music balance

## E. Final file (`contact_sheet.py video --every 4`)
- [ ] No black frames, flicker or stale frames
- [ ] 1920×1080, 30 fps, H.264 + AAC
- [ ] Size fits the delivery channel (`--max-mb`)
