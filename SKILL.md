---
name: product-promo-video
description: 把一個可以在瀏覽器打開的產品（網站、儀表板、3D 數位孿生、SaaS 系統）實際操作錄下來，剪成「行銷公司等級」的橫式產品介紹影片：行銷腳本、真實操作畫面、推鏡與標註、台灣口音配音、配樂與音效，一次輸出 MP4。當使用者說「幫我的系統／網站／專題做介紹影片」「做產品宣傳片」「給企業客戶看的 demo 影片」「錄操作畫面做成影片」時使用。需要搭配 motion-video-skill。
---

# Product Promo Video Skill — 把網頁產品做成專業介紹影片

這個 skill 是 [motion-video-skill](https://github.com/nutcelvischen-jpg/motion-video-skill) 的延伸：
motion-video 負責「動畫＋配音＋渲染」的引擎，這個 skill 加上**產品實拍**與**行銷包裝**：

| 加了什麼 | 用什麼做 |
|---|---|
| 真實操作畫面（含 3D / WebGL）逐格擷取，30fps 平順 | `scripts/capture.py` + `scripts/vt.js`（虛擬時鐘） |
| 行銷公司的腳本結構（痛點→登場→功能→情境→價值→署名） | `references/storyboard-marketing.md` |
| 畫面放大推鏡、標註、轉場、Logo 片尾 | `templates/promo-wide/index.html` |
| 配音加速＋句子精準對齊停頓 | `scripts/align_timeline.py` |
| 配樂（Apple Loops 編排）、轉場音效（程式合成）、專業混音 | `scripts/music.py`、`sfx.py`、`mix.py` |
| 檢查用總覽圖 | `scripts/contact_sheet.py` |

完整範例：`examples/cnc-twin/`（CNC 工廠數位孿生，90 秒，企業客戶，片尾 ICMA Lab）。

`<P>` = 本 skill 資料夾，`<MV>` = motion-video skill 資料夾。所有指令在**工作區根目錄**執行，影片放 `videos/<名稱>/`。

---

## 總流程（照順序做，每一步都有檢查點）

```
0 環境 → 1 試用產品 → 2 腳本（給使用者確認）→ 3 建資料夾 → 4 鏡頭清單 + 試拍 → 5 正式擷取
→ 6 配音 + 對齊 → 7 動畫 → 8 總覽圖檢查 → 9 配樂音效 → 10 渲染 + 混音 → 11 成片檢查 → 12 交付
```

時間預估（90 秒影片）：腳本 15 分、擷取 20～60 分（看電腦，可背景跑）、動畫 30～60 分、渲染 10～15 分。

---

## 步驟 0：環境

```bash
git clone https://github.com/nutcelvischen-jpg/motion-video-skill .agents/skills/motion-video   # 若還沒裝
pip install playwright numpy pillow imageio-ffmpeg && python -m playwright install chromium
python <MV>/scripts/check_env.py
ffmpeg -version     # mix.py / align_timeline.py 需要系統 ffmpeg
```
- TTS 金鑰用環境變數 `OPENROUTER_API_KEY`（或 `GEMINI_API_KEY`），**絕不寫進檔案或對話**。
  使用者沒設定時，請他存在家目錄的隱藏檔（例：`~/.openrouter.env`，`chmod 600`），執行時 `set -a; source ~/.openrouter.env; set +a`。
- Mac 的 Homebrew Python 若出現 `CERTIFICATE_VERIFY_FAILED`：`export SSL_CERT_FILE=/etc/ssl/cert.pem`。
- 雲端／沙盒環境常常連不到 TTS API 或 Google Fonts：TTS 改在使用者電腦上跑，字型改用本機字型（範本已內建 Manrope + Noto Sans CJK TC 備援）。

## 步驟 1：先當使用者，把產品玩一遍（不可省略）

目的：知道有哪些「值得拍」的畫面、哪些功能在影片裡會看不清楚。

1. 讀產品的 `README.md` / `PRODUCT.md` / `DESIGN.md`：功能、色票、字型、資料是真是假。
2. 啟動產品：靜態網站 `cd dist && python -m http.server 8766`；Vite 專案 `npm run build` 後同上（或 `npm run dev`）。
3. 用 Playwright 開起來，**列出所有按鈕文字**（之後鏡頭清單要用）：
   ```python
   btns = await pg.eval_on_selector_all("button", "els=>els.map(e=>(e.innerText||e.getAttribute('aria-label')||'').trim())")
   ```
4. 每個主要功能點一次、截一張圖，拼成總覽圖親自看。特別注意：
   - **在小畫面看不出差異的功能**（例如圖層只變一點點顏色）→ 影片要推鏡放大，或建議使用者先改程式加強對比。
   - **鏡頭預設差異太小** → 改用滑鼠拖曳做環繞運鏡（capture.py 的 `drag`）。
   - **3D 畫布的父容器選擇器**（例如 `.scene-area` / `#scene`）→ 之後做全螢幕「電影鏡頭」用。
   - 有沒有 toast、彈窗、需要登入、localStorage 會記住上次狀態。
5. 回報使用者：哪些能直接拍、哪些建議先改程式（列成「建議改／可改可不改／不用改」三類，附理由與改法）。**使用者改完再拍**，不然要重拍。

## 步驟 2：寫行銷腳本（先給使用者確認台詞再往下）

先讀 `references/storyboard-marketing.md`。問清楚（沒說就用預設）：

| 項目 | 預設 |
|---|---|
| 長度 | 90 秒（約 330～360 個中文字）|
| 觀眾 | 企業客戶（決策者）|
| 語言 | 台灣華語（`zh`）|
| 聲音 | `Leda`＋「科技發表會旁白：沉穩、專業、有自信」|
| 片尾署名 | 使用者的實驗室／公司 |

標準 8 場結構：**痛點鉤子 → 產品登場 → 核心功能 → 原理／圖層 → 情境模擬 → 量化價值 → 擴充與未來 → 記憶點＋署名**。

規則：
- 每句 8～24 字；數字與英文縮寫用 `["念法", "顯示"]`（例：`["C N C", "CNC"]`、`["3 D", "3D"]`、`["I o T", "IoT"]`）。
- 中文一律台灣用語（影片、資料、軟體、品質；不用視頻、數據、軟件、質量、家人們）。
- **誠實**：模擬資料要標「展示畫面・模擬資料」；示範係數要註明；未來功能用「下一步」，不能講成已上線；不捏造客戶、成效數字。開場若用戲劇化數字（帳單金額），交付時要提醒使用者。
- 每句台詞旁邊寫好「這句配什麼畫面」，畫面要能從產品實際拍到。

## 步驟 3：建資料夾

```bash
python <P>/scripts/new_promo.py videos/<名稱> --mv <MV>
```
然後：把確認過的台詞寫進 `script.json`；`index.html` 的 `:root` 換成產品色票（看產品 CSS 變數或 DESIGN.md）、`assets/fonts/` 換成產品字型。

## 步驟 4：鏡頭清單 + 試拍

先讀 `references/capture-guide.md`。編輯 `shots.json`，每個鏡頭一個條目：

- `mode: "cine"`：只留 3D 畫布、全螢幕（產品登場、圖層、電影感環繞）。
- `mode: "ui"`：整個介面（點按鈕、看數字跳動、表單操作），之後在動畫裡推鏡到重點區域。
- 動作在第幾格發生（30 格 = 1 秒）：`click`（按鈕文字）、`drag`（環繞）、`type`（逐字輸入）、`fill`、`select`、`eval`。
- 每個鏡頭 240～270 格（8～9 秒），比該句台詞長一點；**關鍵動作放在第 20～30 格**，方便動畫對時。

試拍（每 45 格存一張，快速檢查動作有沒有發生）：
```bash
python <P>/scripts/capture.py videos/<名稱>/shots.json --out /tmp/test_clips --test
python <P>/scripts/contact_sheet.py clips /tmp/test_clips      # 打開 sheet_clips.jpg 看
```
確認：按鈕真的按到（log 出現「找不到按鈕文字」就是沒按到）、環繞角度不會轉到產品背面、彈窗/toast 正常。

## 步驟 5：正式擷取（可背景執行）

```bash
nohup python <P>/scripts/capture.py videos/<名稱>/shots.json --out videos/<名稱>/assets/clips --jobs 2 > capture.log 2>&1 &
```
- 沒有 GPU 的雲端：3D 全螢幕約 1～2.5 秒／格、UI 約 1 秒／格。10 個鏡頭約 30～60 分鐘。**趁擷取時做步驟 6、7。**
- Mac 有 GPU：在 shots.json 加 `"channel": "chrome", "gpu": true`，快 5～10 倍。
- 完成後一定跑 `contact_sheet.py clips` 看每個鏡頭的頭、中、尾。

## 步驟 6：配音 + 對齊

```bash
python <MV>/scripts/tts.py videos/<名稱> --lang zh --only s01   # 先試一段聽口音
python <MV>/scripts/tts.py videos/<名稱> --lang zh               # 全部
python <P>/scripts/align_timeline.py videos/<名稱> --mv <MV> --target 90   # 壓到目標長度並對齊句子
python <MV>/scripts/render.py videos/<名稱> --preview            # 更新 _tl.js
```
- TTS 通常比估計長 5～10%。`--target` 會自動算加速倍率（建議 0.95～1.08；超過 1.12 就該刪台詞）。
- align 會把句子邊界吸附到真正的停頓，畫面切換才會精準。log 出現「找不到停頓」的句子，檢查台詞是否太長或標點太少。
- 改了某一場台詞：`tts.py --only s03` 重做 → `align_timeline.py ... --refresh s03`（把新檔收進 raw 再重新對齊）。

## 步驟 7：做動畫（改 index.html）

先讀 `references/motion-recipes.md`，再看 `examples/cnc-twin/index.html`。核心概念：

- 每個鏡頭是一個 `.clip`，`clip(sel, t0, t1, skip)` 宣告「t0 秒開始播第 skip 格」；`tick()` 每格換圖。
- **所有時間綁台詞**：`S(i).start`、`L(i,j)`、`LM(i,j,k)`，不要寫死秒數。
- 動作對時：鏡頭在第 30 格按下按鈕 → `clip(sel, LM(i,j,.22) - 1.0, ...)` 讓「按下」落在問句講完的瞬間。
- 轉場：`cutIn`（擦入）；推鏡：`zoomTo(sel, x, y, scale, t)`（x,y 用截圖量面板位置）；慢推：`drift`。
- 文字：痛點卡＋數字跳動、問題膠囊 `.tag`、大字 `.kin .w`（逐行模糊浮現）、標註 `.callout`、公式卡 `.card`、Logo。
- 畫面上同時最多 3 個重點；字幕區（下方 160px）不放東西；長時間顯示產品畫面時保持「展示畫面・模擬資料」標籤。

## 步驟 8：總覽圖檢查（每次改完都做，直到沒問題）

```bash
python <MV>/scripts/render.py videos/<名稱> --sheet          # 每句結尾一張
python <MV>/scripts/render.py videos/<名稱> --stills 41.5,68  # 指定秒數
```
**一定要打開圖親自看**，對照 `references/qa-checklist.md`。最常見的錯：上一個鏡頭沒隱藏蓋住後面、卡片跑出畫面（`.glass` 的 position 衝突）、文字壓到 3D 主體、字幕被擋。

## 步驟 9：配樂與音效

先讀 `references/audio-guide.md`。
```bash
# Mac：從 GarageBand 內建 Apple Loops 選同一家族（同 BPM 同調）
python <P>/scripts/apple_loops.py list --genre Chillwave
python <P>/scripts/apple_loops.py beats --bars-of 9.6
python <P>/scripts/apple_loops.py convert "07 Chillwave/Forward Progress Synth" "07 Chillwave/Forward Progress Bass" "07 Chillwave/Matchbox Beat 01" --out videos/<名稱>/loops
# 編排（段落綁旁白）與音效
python <P>/scripts/music.py videos/<名稱>/music.json --timeline videos/<名稱>/timeline_zh.json --out videos/<名稱>/bgm.wav
python <P>/scripts/sfx.py   videos/<名稱>/sfx.json   --timeline videos/<名稱>/timeline_zh.json --out videos/<名稱>/sfx.wav
```
- 音樂的關鍵：`anchor` 讓強拍落在產品登場那一刻；開場用低通濾波「悶住」、登場瞬間打開；重點句（例「先模擬，再決策」）抽掉鼓兩小節；片尾只留旋律淡出。
- 沒有 Mac：使用者提供自己有授權的 `bgm.wav`，music.json 只放一軌。

## 步驟 10：渲染 + 混音

```bash
python <MV>/scripts/render.py videos/<名稱> --lang zh --crf 18 --workers 2
python <P>/scripts/mix.py videos/<名稱> --lang zh --max-mb 30
```
- `--crf 18`：產品畫面細節多，預設 26 會糊。90 秒約 30 MB。
- mix.py：旁白壓縮、音樂側鏈閃避人聲、音效疊上、整體 loudnorm -15 LUFS，輸出 `out/<名稱>_zh_final.mp4`；超過 `--max-mb` 另存 `_small.mp4`。

## 步驟 11：成片檢查

```bash
python <P>/scripts/contact_sheet.py video videos/<名稱>/out/<名稱>_zh_final.mp4 --every 4
```
看：每張的字幕與畫面是否對應、轉場時沒有黑畫面、片尾 Logo 有出現、總長符合目標。
聲音無法自動檢查：**請使用者親自聽**口音、念錯字、音樂音量。

## 步驟 12：交付

- 成片：`out/<名稱>_zh_final.mp4`（傳檔有大小限制就給 `_small.mp4`）。
- 原始檔：`index.html`、`script.json`、`shots.json`、`music.json`、`sfx.json`、`timeline_zh.json`（`assets/clips/` 很大，可不附，能用 shots.json 重拍）。
- 回報：長度、大小、響度、哪些是戲劇化／示範內容需要使用者確認、建議下一步（英文版、15 秒短版、直式版）。

---

## 常見問題

見 `references/troubleshooting.md`。最常見的五個：
1. **截圖卡住不動**：用了 Playwright 的 `page.clock` → 改用本 skill 的 `vt.js`（capture.py 已處理）。
2. **成片某段畫面是上一格**：`index.html` 最後那段 `__seek` 覆寫（等圖片 decode）被刪了。
3. **卡片位置跑掉**：`.glass` 帶 `position:relative`，卡片要加 `position:absolute!important`（範本的 `.card` 已處理）。
4. **按鈕沒按到**：文字比對是「完全相同」優先、其次「開頭相同」；同名按鈕（清單項目 vs 鏡頭按鈕）會按錯 → 改用 `click_sel`。
5. **動作跟台詞對不上**：clip 的 t0 沒有扣掉「動作發生在第幾格 ÷ 30」。

## 檔案地圖

```
<P>/
├── SKILL.md                         ← 本檔
├── scripts/
│   ├── new_promo.py                 ← 建影片資料夾（套 promo-wide 範本）
│   ├── capture.py + vt.js           ← 逐格擷取產品畫面
│   ├── align_timeline.py            ← 配音加速＋句子對齊
│   ├── music.py / apple_loops.py    ← 配樂編排 / 找 Apple Loops
│   ├── sfx.py                       ← 程式合成音效
│   ├── mix.py                       ← 混音＋合成成片
│   ├── contact_sheet.py             ← 鏡頭／成片總覽圖
│   └── ppvslib.py                   ← 共用（時間運算式、wav）
├── templates/promo-wide/            ← index.html、script.json、shots/music/sfx.json、字型
├── examples/cnc-twin/               ← 完整案例（90 秒企業版）
└── references/
    ├── storyboard-marketing.md      ← 行銷腳本結構、台詞公式、誠實原則
    ├── capture-guide.md             ← shots.json 完整說明、鏡頭設計
    ├── motion-recipes.md            ← 動畫招式與對時公式
    ├── audio-guide.md               ← 配音、選曲、編排、音效、混音
    ├── qa-checklist.md              ← 檢查清單
    └── troubleshooting.md           ← 錯誤排除
```
