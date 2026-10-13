# 02 Design the story: derive it from the audience

## 1. Three premises (ask if unknown)

| Question | Affects |
|---|---|
| **Who watches, and what do they care about?** | which benefits, vocabulary, technical depth |
| **What should they do afterwards?** | call to action, sign-off |
| **Where will it play?** | length, subtitle size, whether it must work muted |

Audience → cares about (examples, not rules):

| Audience | Cares about | Doesn't care about |
|---|---|---|
| Executives | cost, risk, adoption effort, visibility | frameworks, implementation details |
| Front-line users | ease of use, time saved | architecture, business model |
| Competition judges | novelty, completeness, impact | long operating instructions |
| Students / beginners | fun, clarity, "can I build this?" | business KPIs |

## 2. Message hierarchy
Write it before choosing a structure:
```
The one thing viewers remember: ________ (value proposition, one sentence)
Supporting evidence (2–4, each with a shot):
  1. ________  ← shot: ________
  2. ________  ← shot: ________
  3. ________  ← shot: ________
```
Evidence without a shot gets cut.

## 3. Choose a narrative structure

| Structure | Flow | Fits |
|---|---|---|
| Problem → solution | pain → reveal → how it solves it → value | audience already feels the pain (B2B) |
| Result first | money shot first → how it works → value | highly visual products, short-attention platforms |
| Before / after | a day without vs. with the product | efficiency tools |
| Day in the life | follow one user through a task | workflow systems, user as hero |
| Feature tour | 3–5 features, one segment each | audiences who already know the product, tutorials |
| Architecture explainer | where data comes from → what happens → what comes out | technical judges, engineers |
| Scenario simulation | "what if…?" several times | simulation, decision support, digital twins |

Mix if needed, but keep one spine.

## 4. Beat sheet
For each beat: purpose, length, emotion, picture, line direction.
```
beat  purpose                 sec    emotion     picture              line
1     make them feel the pain  0-10   tension     (your design)        (your words)
```
Pacing:
- **First 3 seconds** must stop the scroll: pain, contrast, a striking image or number.
- An emotional curve: tension → release → build → peak → resolve. Not one flat intensity.
- Money shot around two-thirds, with set-up before it.
- A memorable last line, ideally echoing the opening.
- Length: English ≈ 2.4 words/s, Chinese ≈ 4 characters/s including pauses. 90 s ≈ 210–230 words.

When time is short, cut *how many* proof points, not the depth of each. Three clear points beat six rushed ones.

## 5. Writing lines
- One idea per line; 2–3 lines per beat.
- Talk to "you", not "we will now introduce".
- **Use verbs the footage can perform**: click, switch, add, drop, light up. For every line ask "what's the picture?" — no answer, rewrite.
- Question + answer is the strongest rhythm for scenarios.
- Give TTS pronunciations: `["spoken", "displayed"]`, e.g. `["C N C", "CNC"]`.
- Use the audience's language and spelling.

## 6. Voice direction
`style`: who speaks, to whom, accent, pace, emotion. Per-scene `dir`: only what differs (suspense, brighter, emphasis, slower). Match the audience: credible and calm for executives, livelier for students.

## 7. Honesty

| Situation | Do |
|---|---|
| Simulated data on screen | persistent small label while product is shown; repeat at the end |
| Example coefficients | footnote where they appear |
| Unbuilt features | only under "next / roadmap" |
| Dramatized numbers (a hook's bill amount) | allowed — tell the user at delivery |
| Customers, results, testimonials | never without a real source |
| Third-party logos | don't |

## 8. Output
`script.json` (motion-video format). When asking for approval, include the picture for each line so the user can judge "can we actually film that?".
