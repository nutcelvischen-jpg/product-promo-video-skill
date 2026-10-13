# 錯誤排除

| 症狀 | 原因 | 解法 |
|---|---|---|
| `page.screenshot()` 永遠卡住 | 用了 Playwright `page.clock.install()` | 用 `vt.js`（capture.py 已內建） |
| `ERR_CONNECTION_REFUSED` | 產品 server 沒啟動 | 啟動並用 `curl localhost:<port>` 確認 |
| `! 找不到按鈕文字` | 文字不同、元素還沒出現 | 先列出所有按鈕文字；改用 `click_sel`；或延後幾格 |
| 按到錯的按鈕 | 兩個元素文字開頭相同 | 完全相同優先；兩個都相同時用 `click_sel` |
| cine 畫面空白／變形 | container／canvas_host 選錯，或 3D 沒收到 resize | 重新找選擇器（見 01）；capture.py 會送 resize |
| 環繞轉太多 | OrbitControls 約 1080px ≈ 360° | 70° 以內約 200px |
| 某些東西不會動 | 用了 Web Worker 或 `<video>` | 改用 ui 鏡頭；或請產品端改到主執行緒 |
| 擷取很慢 | 沒有 GPU | 背景執行、`--jobs 2`；Mac 加 `"channel":"chrome","gpu":true` |
| 總覽圖某鏡頭不見 | 被後面的 `.clip` 蓋住，或 t1 太早 | 檢查 `clip()` 時間；DOM 順序＝出現順序 |
| 卡片跑到畫面外 | `.glass{position:relative}` 蓋掉絕對定位 | 加 `position:absolute!important` |
| 自訂容器位置不對 | 沒有 `.abs` class | CSS 寫 `position:absolute` |
| 成片有一格是上一張 | `__seek` 覆寫被刪 | 恢復骨架最後那段 script |
| 字型跑掉 | 連不到 Google Fonts | 字型放 `assets/fonts/` |
| TTS `CERTIFICATE_VERIFY_FAILED`（Mac） | Homebrew Python 憑證 | `export SSL_CERT_FILE=/etc/ssl/cert.pem` |
| TTS 連線被拒 | 沙盒擋外部 API | 在使用者電腦執行 tts.py，再把 `audio_<lang>/` 帶回來 |
| 句子切換時間不準 | tts 的句子時間是估計 | `align_timeline.py`；「找不到停頓」就加標點或拆句 |
| 影片太長 | TTS 語速慢 | `--target`；超過 1.12 倍就刪台詞 |
| 音樂節拍跟畫面不合 | loop 長度與 BPM 不符、沒設 anchor | 同家族 loop；鼓組長度相符；anchor 對準登場 |
| 成品太大 | crf 18 約 0.33 MB／秒 | `mix.py --max-mb` |
| 渲染很慢 | 每格要解碼 JPG | 正常（90 秒約 10～15 分）；`--workers 2` |
