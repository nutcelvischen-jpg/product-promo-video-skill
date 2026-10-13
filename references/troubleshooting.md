# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `page.screenshot()` hangs | Playwright `page.clock.install()` | use `vt.js` (built into capture.py) |
| `ERR_CONNECTION_REFUSED` | product server not running | start it; `curl localhost:<port>` |
| "找不到按鈕文字" (button not found) | label differs, element not rendered | list labels first; use `click_sel`; act a few frames later |
| Wrong button clicked | two labels share a prefix | exact match wins; if both exact, `click_sel` |
| Blank / stretched cine view | wrong container / canvas_host, no resize | re-find selectors (see 01); capture.py dispatches resize |
| Orbit swings too far | ~1080 px ≈ 360° | ~200 px for 70° |
| Something doesn't animate | Web Worker or `<video>` | use a ui shot, or move logic to the main thread |
| Capture is slow | no GPU | background + `--jobs 2`; on Mac `"channel":"chrome","gpu":true` |
| A shot vanishes in the sheet | covered by a later `.clip`, or t1 too early | check `clip()` times; DOM order = appearance order |
| Card off-screen | `.glass{position:relative}` | `position:absolute!important` |
| Custom container misplaced | no `.abs` class | `position:absolute` in CSS |
| Stale frame in render | `__seek` override removed | restore the skeleton's last script |
| Fonts wrong | no Google Fonts access | fonts in `assets/fonts/` |
| TTS `CERTIFICATE_VERIFY_FAILED` (macOS) | Homebrew Python certs | `export SSL_CERT_FILE=/etc/ssl/cert.pem` |
| TTS connection refused | sandbox blocks the API | run tts.py on the user's machine, bring `audio_<lang>/` back |
| Cuts feel off | estimated sentence times | `align_timeline.py`; add punctuation where it finds no pause |
| Too long | slow TTS | `--target`; above 1.12× cut lines |
| Beat doesn't fit | mismatched loop lengths, no anchor | same family; matching drum length; anchor on the reveal |
| File too big | crf 18 ≈ 0.33 MB/s | `mix.py --max-mb` |
| Render slow | one JPG decode per frame | normal (10–15 min / 90 s); `--workers 2` |
