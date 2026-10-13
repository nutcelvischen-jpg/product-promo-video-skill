# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `page.screenshot()` hangs | Playwright `page.clock.install()` | use `vt.js` (built into capture.py) |
| `ERR_CONNECTION_REFUSED` | product server not running | `cd dist && python -m http.server 8766`; `curl localhost:8766` |
| "找不到按鈕文字" (button not found) | label differs, element not rendered yet | list labels with Playwright; use `click_sel`; act a few frames later |
| Wrong button clicked | two labels share a prefix | exact match wins; if both exact, use `click_sel` |
| Blank / stretched cine view | wrong container/canvas_host; no resize | re-find selectors; capture.py dispatches resize |
| Orbit swings too far | 1080 px ≈ 360° | ≤ 200 px for ~70° |
| Something doesn't animate | Web Worker or `<video>` not under the virtual clock | film in UI mode or move logic to main thread |
| Capture is slow | no GPU (SwiftShader) | background + `--jobs 2`; on Mac `"channel":"chrome","gpu":true` |
| A shot disappears in the sheet | covered by a later `.clip` or t1 too early | check `clip()` t1; DOM order = appearance order |
| Old shots visible at the end | old template without auto-hide | use current `clip()` (auto-hide at t1 + 0.6) |
| Card at bottom of frame | `.glass{position:relative}` overrides `.abs` | `position:absolute!important` |
| `#logo` / `#title` misplaced | no `.abs`, top/left ignored | add `position:absolute` |
| Stale frame in render | `__seek` override removed | restore the last script block |
| Fonts wrong | no Google Fonts access | ship fonts in `assets/fonts/` via `@font-face` |
| TTS `CERTIFICATE_VERIFY_FAILED` (macOS) | Homebrew Python certs | `export SSL_CERT_FILE=/etc/ssl/cert.pem` |
| TTS connection refused | sandbox blocks the API | run tts.py on the user's machine, copy `audio_<lang>/` back |
| Cuts feel off | estimated sentence times | run `align_timeline.py`; add punctuation where it reports no pause |
| Too long | slow TTS | `--target 90`; above 1.12× cut lines |
| Beat doesn't fit | mismatched loop lengths, no anchor | same family; drums ½× or 1× melody length; anchor on reveal |
| File too big to send | crf 18 ≈ 30 MB / 90 s | `mix.py --max-mb 25` |
| `render.py` slow | one JPG decode per frame | normal (10–15 min / 90 s); `--workers 2` |
