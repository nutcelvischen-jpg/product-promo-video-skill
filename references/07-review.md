# 07 Review: watch with the audience's eyes

## 1. Method
1. **Inspect every contact-sheet frame** (`render.py --sheet`). Cover the subtitle and look only at the picture — can you guess the line? If not, the picture isn't acting it out.
2. **Spot-check transitions** (`--stills` at mid-transition times): black frames, blanks, leftover shots.
3. **Shrink it**: at phone size, is the point still readable?
4. **Final file every 4 s** (`contact_sheet.py video --every 4`).
5. **Ask**: Do viewers know what this is within 3 s? Do they remember the value proposition? Would an expert find any line exaggerated?

## 2. Checklist
### Story
- [ ] Something in the first 3 s stops the scroll
- [ ] One spine; every beat supports the value proposition
- [ ] Emotional curve; money shot at the peak
- [ ] Honest labeling (simulated data, example parameters, roadmap)

### Shots
- [ ] Every key action happened and matches its line
- [ ] Camera moves start and end on good compositions
- [ ] No errors, dev tools or private data

### Picture
- [ ] Every line is acted out
- [ ] ≤ 3 focal elements
- [ ] Text has a backing, avoids the subject, stays in bounds, clears subtitles
- [ ] Push-ins don't crop the target
- [ ] Visuals match the product (palette, semantic colors, fonts)
- [ ] Not the same technique everywhere
- [ ] Previous clips hidden; logo fully visible and held

### Sound
- [ ] Length on target
- [ ] Music follows the story; space under the key line
- [ ] −14…−16 LUFS, no clipping
- [ ] User has listened

### File
- [ ] 1920×1080, 30 fps, H.264 + AAC
- [ ] Size fits delivery (`mix.py --max-mb`)
