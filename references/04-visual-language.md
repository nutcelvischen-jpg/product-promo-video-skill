# 04 Visual language: grown from the product

## 1. Where the look comes from
Don't pick colors from a template. The answer is in the product:

| From the product | In the film |
|---|---|
| background color | film background (a bit darker so footage pops) |
| primary color | emphasis, accents, glow |
| semantic colors (OK / warning / energy / money…) | tags, legends, numbers — **same meaning as in the product** |
| fonts | titles and numbers (`@font-face` from `assets/fonts/`) |
| radius, line weight, shadow style | cards, pills, outlines |

No design system? Sample colors from screenshots and confirm with the user. Set `:root` in the skeleton: `--bg1/2/3`, `--cream`, `--muted`, `--gold` (the runtime's accent variable → product primary), `--glow-rgb`, plus your semantic colors.

## 2. Layout
- 1920×1080; top 140 px brand bar (runtime shows brand/event), bottom 160 px subtitles.
- ≤ 3 focal elements; clear the previous beat's elements before the next.
- Text over footage **always needs a backing**: gradient, dark card, local dimming. Never translucent glass over a bright 3D floor.
- Keep text off the product subject: use empty space or push the subject aside (`x` offset).
- Type sizes: big words 120–170 px, titles 60–90, tags 26–34, footnotes 18–22. Under 20 px only for unimportant notes.

## 3. Technique toolbox
Every technique answers a viewer question. **Problem first, then technique**; don't repeat one move everywhere.

| Viewer question | Technique | Hints |
|---|---|---|
| "Where do I look?" | push-in to a point | scale around the target; start 0.3–0.6 s after the action, finish in 1.2–1.8 s |
| | local dim / spotlight | darken or blur everything else |
| | callout | line or color bar to the target + 2–6 word label, after the push-in |
| "What is this?" | scene tag | small pill: category (small) + name |
| | legend | dots in the product's semantic colors |
| "How does it work?" | formula card, flow, architecture | only the layer viewers need; reveal piece by piece with the narration |
| | dots flowing along paths | direction of data or energy (computed from `t` in `tick()`) |
| "Why does it matter?" | count-up number | from 0 or from the "before" value |
| | kinetic type | one sentence in two lines, each emerging from blur; for key lines and turns |
| | dim-out | darken and blur so the words are the only focus |
| "Is this real?" | browser frame | first full-UI reveal in a tilted window |
| | real footage | never replace filmable footage with an illustration |
| Emotional turn | circle reveal, flash | once-only moments: reveal, title, logo |
| Topic change | wipe, fade | start 0.3–0.4 s before the next line |

Need something not on the list? Design it: direction and easing (`expo.out` in, `power2.in` out), semantic sense (drop goes down, expand spreads out), timing tied to narration.

## 4. Motion principles
- Fast in, faster out: in 0.6–1.2 s, out 0.4–0.6 s.
- Move one group at a time; stagger multiples by 0.1–0.4 s.
- Any frame static for > 3 s needs micro-motion (drift, particles, sheen) or it looks frozen.
- When the footage itself moves, add little on top.
- Keep transition vocabulary consistent: one main transition, one special-moment transition.

## 5. Technical traps
- motion-video's `.glass` sets `position:relative` — absolutely positioned cards need `position:absolute!important`.
- Containers without `.abs` need `position:absolute`.
- The render environment may not reach Google Fonts — ship fonts locally.
- No CSS animation/transition, `setTimeout`, `<video>`, `Math.random()` — everything on the GSAP timeline or in `tick(t)`; random via `c.rng(seed)`.
