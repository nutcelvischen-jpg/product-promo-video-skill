# Case study: CNC factory digital twin promo

> This document records *why* each decision was made. Learn the reasoning, not the scenes, lines or colors.
> For a different product almost every answer changes — each section ends with "for another product".

**Product**: Three.js CNC factory digital twin (6–12 CNC machines, outdoor solar, production / power / carbon layers, scenario simulation, add devices), simulated data.
**Brief**: 90 s, Taiwanese Mandarin, enterprise clients, signed ICMA Lab.
**Result**: 90.6 s, 8 scenes, 10 shots.

---

## 1. What discovery revealed

| Observation | Judgment | Action |
|---|---|---|
| Power / carbon layers only tinted the 3D machines slightly — invisible when shrunk | post can't fix it | asked the user to change code: strong blue / coral layers, thicker brighter energy particles |
| "Interior" camera only zoomed a little | post could fix it, but a code change is stronger | user changed it to an aisle-level view |
| Scenario switch: solar 27→8 kW, grid 24→43 kW, trend line bends | "one action, many linked changes" | chosen as a money shot |
| KPI numbers small on screen | push-in solves it | film the full UI, zoom in animation |
| "Simulated data" badge, example carbon factor | honesty | persistent "demo · simulated data" tag; formula card footnotes the example factor |

**For another product**: find which feature disappears when shrunk and which action triggers the most linked change.

## 2. Story reasoning
- **Audience** = enterprise decision makers → cost, risk, visibility; not Three.js.
- **Value proposition**: "See it, then manage it" — make invisible power and carbon visible.
- **Structure**: plant managers already feel "the bill only shows a total" → problem→solution as the spine, with a scenario-simulation middle to amplify decision value (the digital twin's real differentiator).
- **Echo**: opening big word "Invisible," → closing "See it, then manage it."
- **Cuts**: CSV export, pause and sim speed were considered but aren't value to executives; "add machines" stayed because it answers the adoption question "what if we expand?".
- **Roadmap**: IoT integration isn't built → only under "next", shown as an architecture diagram.
- **Hook bill amount** is dramatized — flagged to the user at delivery.

**For another product**: a learning tool for students would have a different pain, structure (maybe result-first or day-in-the-life) and tone — no bills, no KPIs.

## 3. Shot reasoning

| Line conveys | Why this shot |
|---|---|
| Reveal grandeur | full-screen 3D orbit (cine): only 3D gives "an entire factory" scale |
| "status, progress, output in sync" | whole UI in a tilted browser frame: this is a complete system |
| "the 3D floor updates live" | aisle-level interior: jump from dashboard to being there |
| "one click: spindle speed, power, energy" | UI shot, click CNC-03 at frame 20, push into the detail panel |
| "where power comes from and goes" | power-layer cine + legend: only 3D particles show flow |
| scenarios (cloud, fault) | UI shot, scenario clicked at frame 30, push into the changing numbers |
| "add a machine, auto-placed" | UI shot: type the name, add, 3D gains a machine |

Actions at frames 20–30; animation uses `clip(sel, T - F/30, ...)` to land them right after each question.

**For another product**: no 3D means no cine shots; "grandeur" might come from the UI unfolding or a data visualization in motion.

## 4. Visual reasoning
- All colors from the product: deep teal background, mint primary, amber = solar, blue = power, coral = fault/carbon. Tag colors match the product's layer meanings.
- Font: the product's Manrope.
- Techniques chosen by problem:
  - "where to look" → push-in + left dimming + callouts (detail panel)
  - "how it works" → formula cards (solar balance, carbon), architecture diagram (IoT)
  - "this matters" → dim-out big words ("Simulate first, then decide")
  - "this is real" → browser frame
- Traps hit: the formula card escaped the frame because of `.glass`'s `position:relative`; text over the bright 3D floor was unreadable → dark cards.

**For another product**: different palette and semantic colors → different tags, cards and accents; techniques chosen by what's hard to understand in *your* product.

## 5. Sound reasoning
- Voice: Leda, calm keynote narrator (enterprise audience).
- TTS ran 6% long → `align_timeline.py --target 90` (×1.06).
- Music: Apple Loops Chillwave "Forward Progress" family (steady, modern, unobtrusive) + same-tempo drums.
  - Intro: filtered melody only → filter opens with bass and drums at the reveal (anchor) → drums drop two bars under "Simulate first" → melody-only fade at the end.
- SFX: 11 transition whooshes, 3 booms (reveal, title, logo), 3 ticks (question pills).

**For another product**: a student-facing video might use a lighter style and livelier voice; draw the curve from *your* story.

## 6. Files
`script.json`, `shots.json`, `index.html`, `music.json`, `sfx.json` are the real files — for seeing how decisions became code. Don't start from them and change the words; start from the `new_promo.py` skeleton and design.
