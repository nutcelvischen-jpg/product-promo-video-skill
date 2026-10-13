# 錯誤排除

| 症狀 | 原因 | 解法 |
|---|---|---|
| `page.screenshot()` 永遠卡住 | 用了 Playwright `page.clock.install()` | 改用 `vt.js`（capture.py 已內建） |
| 擷取時出現 `ERR_CONNECTION_REFUSED` | 產品 server 沒啟動或被關掉 | `cd dist && python -m http.server 8766`，用 `curl localhost:8766` 確認 |
| `! 找不到按鈕文字` | 文字不同（含空白、icon）、按鈕還沒出現 | 先在 Playwright 列出所有按鈕文字；或改用 `click_sel`；或延後幾格 |
| 按到錯的按鈕 | 有兩個開頭相同的按鈕（清單項目「場外太陽能 裝置容量…」vs 鏡頭按鈕「場外太陽能」） | 完全相同優先，但兩個都完全相同時用 `click_sel` |
| 3D 全螢幕模式畫面空白／變形 | container / canvas_host 選錯；3D 沒收到 resize | 重新找選擇器；capture.py 會送 resize 事件，若產品用 ResizeObserver 通常也會自動更新 |
| 環繞轉太多 | OrbitControls 1080px ≈ 360° | 70° 以內 ≈ 200px |
| 數字或動畫沒在動 | 產品用 Web Worker 或 `<video>`，不受虛擬時鐘控制 | 改拍 UI 模式、或把該功能改成主執行緒 |
| 擷取很慢 | 沒有 GPU（SwiftShader 軟體繪圖） | 背景跑、`--jobs 2`；Mac 上加 `"channel":"chrome","gpu":true` |
| 總覽圖某鏡頭整段消失 | 被後面 DOM 的 `.clip` 蓋住（還沒隱藏）或 clip 的 t1 太早 | 檢查 `clip()` 的 t1；DOM 順序＝出現順序 |
| 最後幾張還看到前面的鏡頭 | 舊版範本沒有自動隱藏 | 用新版 `clip()`（t1 + 0.6 秒自動 opacity 0） |
| 卡片跑到畫面底部 | `.glass{position:relative}` 蓋掉 `.abs` | 卡片加 `position:absolute!important` |
| `#logo`、`#title` 位置不對 | 沒有 `.abs` class，`top/left` 無效 | 在 CSS 寫 `position:absolute` |
| 成片有一格是上一張畫面 | `__seek` 覆寫被刪，截圖時新圖還沒解碼 | 恢復 index.html 最後那段 script |
| 字型跑掉 | 渲染環境連不到 Google Fonts | 字型放 `assets/fonts/` 用 `@font-face`；中文用本機 Noto Sans CJK TC |
| TTS `CERTIFICATE_VERIFY_FAILED`（Mac） | Homebrew Python 找不到憑證 | `export SSL_CERT_FILE=/etc/ssl/cert.pem` |
| TTS 連線被拒 | 雲端沙盒擋外部 API | 在使用者電腦上執行 tts.py，再把 audio_zh/ 複製回來 |
| 句子切換時間怪怪的 | tts 的句子時間是估計值 | 跑 `align_timeline.py`；log 有「找不到停頓」就加標點或拆句 |
| 影片比目標長 | TTS 語速慢 | `align_timeline.py --target 90`；超過 1.12 倍就刪台詞 |
| 音樂節拍跟畫面不合 | loop 長度跟 BPM 對不上、anchor 沒設 | 同家族 loop；鼓組長度是旋律的 1/2 或相同；anchor 設在登場 |
| 成品太大傳不出去 | crf 18 的 90 秒約 30MB | `mix.py --max-mb 25` 自動產生縮小版 |
| `render.py` 很慢 | 每格要解碼一張 JPG | 正常（90 秒約 10～15 分鐘）；`--workers 2` |
