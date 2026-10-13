# 01 Understand the product: be the user first

A video can only sell what the product really does and what a camera can show. This step builds those two lists.

## 1. Read the docs and answer four questions
1. **Who uses it, and what pain does it solve?** (If unstated, ask — don't invent.)
2. **What is the core mechanism?** (where data comes from, what is computed, what comes out)
3. **Is the data real or simulated?** Any example parameters? → how the video must label it
4. **Visual system**: palette, fonts, semantic colors (what means OK, warning, energy…) → reused in the film

## 2. Run it and operate everything
```bash
npm install && npm run build && cd dist && python -m http.server 8766   # or the project's own way
```
List every interactive element with Playwright:
```python
btns = await pg.eval_on_selector_all("button,[role=button],a", "els=>els.map(e=>(e.innerText||e.getAttribute('aria-label')||'').trim()).filter(Boolean)")
```
Operate **every feature once and screenshot it** (before and after is better), stitch a contact sheet, and look.

## 3. Build the feature list

| Feature | How to trigger | What changes on screen | Readable on video? | Value to the audience |
|---|---|---|---|---|
| e.g. scenario switch | click "Cloud cover" | solar 27→8 kW, grid up, trend bends | small numbers → push-in | simulate before deciding (high) |

Readability test: shrink the screenshot to 960×540 (the effective resolution on phones and projectors). Can you still see the change?

## 4. Find the money shot
Usually one of:
- one action triggers many linked changes (3D, numbers, chart move together)
- something invisible becomes visible (energy flow, data flow, hidden relationships)
- continuity from macro to micro (whole factory → one machine → one number)
- a scenario with a dramatic before/after

Place it at the story's peak and film it with the best shot (cine, push-in, enough time).

## 5. Visibility problems and code suggestions

| Problem | Example | Suggestion |
|---|---|---|
| Change is too subtle | a layer only tints slightly | stronger colors, thicker/brighter particles or lines |
| Camera presets barely differ | "interior view" only zooms a bit | really move inside, or orbit by dragging in the video |
| UI elements are tiny | 9 px labels | no change — push in on video |
| State differs per launch | localStorage remembers settings | clear before capture, or add a `?demo` flag |
| Hint text, cursor tips | "drag to rotate" | hide with CSS during capture |

Report in three buckets — **recommended** (post can't fix), **optional** (post can fix), **not needed** — with reasons and rough effort. Film after the user rebuilds.

## 6. Output
- Feature list with readability and value
- 1–2 money-shot candidates
- Palette, fonts, semantic colors
- Honesty requirements (simulated data, example parameters, unbuilt features)
- 3D canvas container selector (for cine shots):
  ```js
  let e=document.querySelector('canvas'),out=[];while(e){out.push(e.tagName+'#'+e.id+'.'+[...e.classList].join('.'));e=e.parentElement}out
  ```
