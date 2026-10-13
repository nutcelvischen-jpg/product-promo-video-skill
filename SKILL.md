---
name: product-promo-video
description: 引導 AI 用程式為「能在瀏覽器打開的產品」（網站、儀表板、3D 數位孿生、SaaS）製作專業產品介紹影片：自己試用產品、依觀眾設計故事、從台詞設計鏡頭、逐格擷取真實操作畫面、用 HTML/GSAP 做動態設計、配音配樂混音，輸出 MP4。當使用者要「幫我的系統／網站／專題做介紹影片」「產品宣傳片」「給客戶看的 demo 影片」時使用。需搭配 motion-video-skill（渲染引擎）。
---

# Product Promo Video — 用程式做產品介紹影片

## 這個 skill 在教什麼

不是一套固定範本，而是一套**做片的方法**：怎麼看懂一個產品、怎麼替特定觀眾找到故事、怎麼把每句話變成可以拍的畫面、怎麼用程式把畫面、文字、聲音精準對在一起。

`examples/cnc-twin/` 是一個完整案例，**用來理解決策，不是用來套用**。每個產品的觀眾、賣點、介面、顏色都不同；如果你做出來的影片換個產品名稱就能套到 CNC 那支，代表你在抄，不是在設計。

## 核心原則

1. **先當使用者，再當導演。** 沒親手操作過產品之前，不寫任何台詞。影片能賣的只有產品真正做得到、而且鏡頭拍得出來的東西。
2. **觀眾決定一切。** 同一個產品，給老闆看講風險與成本，給評審看講創新與技術，給學生看講好玩與好學。結構、語氣、長度、要秀的功能都從這裡推導。
3. **旁白是時鐘。** 所有畫面、轉場、音樂起落都綁在台詞時間上（`L(i,j)`），不寫死秒數。改台詞，整支片自動重新對齊。
4. **每句話都要被畫面「演出來」。** 講「點一下」就要看到點；講「下降」就要看到數字掉。講了畫面卻沒有對應，觀眾就不會相信。
5. **真實素材 > 示意動畫。** 產品實際操作畫面最有說服力；動態設計是用來「引導視線」和「解釋看不見的東西」，不是取代產品。
6. **一次一個重點。** 畫面同時最多 3 個焦點；觀眾看不懂的地方，用推鏡、壓暗、標註把視線帶過去。
7. **誠實。** 模擬資料要標示、示範參數要註明、未完成功能只能說「下一步」、不捏造客戶與成效。給企業看的影片，一句誇大就毀掉整支片的可信度。
8. **每一步都要親眼檢查。** 截圖、總覽圖、成片抽格都要打開來看，不要假設程式「應該」做對了。

## 工具與分工

| 層 | 工具 | 你要自己決定的事 |
|---|---|---|
| 渲染引擎（配音、字幕、時間軸、逐格輸出） | motion-video-skill：`tts.py`、`render.py`、`wide` runtime | 聲音、語氣、版型 |
| 真實畫面擷取 | `scripts/capture.py` + `vt.js`（虛擬時鐘，3D 也能平順 30fps） | 拍哪些鏡頭、動作在第幾格、怎麼運鏡 |
| 動畫骨架 | `templates/promo-wide/index.html`（只有素材層與時間工具，**沒有任何場景**） | 所有場景、版面、文字、轉場 |
| 配音對齊 | `scripts/align_timeline.py` | 目標長度、是否要刪台詞 |
| 聲音設計 | `scripts/music.py`、`sfx.py`、`mix.py`、`apple_loops.py` | 曲風、段落起落、哪裡要重擊 |
| 檢查 | `scripts/contact_sheet.py`、`render.py --sheet` | 你的眼睛 |

`<P>` = 本 skill 資料夾，`<MV>` = motion-video skill 資料夾。影片放 `videos/<名稱>/`。

---

## 工作流程

每一步都有「要想清楚的事」「產出」「檢查點」。前一步的產出是下一步的輸入。

### 1. 理解產品 → 讀 `references/01-product-discovery.md`

**要想清楚：** 這個產品解決誰的什麼問題？它最厲害的那一刻是什麼（the money shot）？哪些功能在影片裡會看不清楚？

做法：讀專案文件 → 把產品跑起來 → 用 Playwright 逐一操作每個功能並截圖 → 拼總覽圖親眼看。

**產出：** 功能清單（每項標註「可直接拍／需推鏡放大／看不清楚建議改程式」）、候選的 money shot、產品的色票與字型。
**檢查點：** 把「建議先改的程式」分成「建議改／可改可不改／不用改」回報使用者。使用者改完再拍，不然要重拍。

### 2. 設計故事 → 讀 `references/02-story-design.md`

**要想清楚：** 觀眾是誰？看完要做什麼？一句話價值主張是什麼？哪一種敘事結構最適合（問題—解法、成果先行、前後對比、一天的工作、功能巡禮、架構解說……）？

不要直接套固定的幾場結構。先寫出「訊息階層」（觀眾最該記住的 1 件事、支撐它的 2～4 件事），再選結構、排節奏（beat sheet），最後才寫台詞。

**產出：** `script.json`，每句台詞旁邊寫好「這句由哪個鏡頭／什麼畫面演出」。
**檢查點：** 台詞給使用者確認後才往下。

### 3. 設計鏡頭 → 讀 `references/03-shot-design.md`

**要想清楚：** 每個 beat 用什麼畫面最有說服力？是 3D 全螢幕的電影感（cine），還是整個介面看數字變化（ui）？關鍵動作要發生在第幾格，才能對上台詞？

**產出：** `shots.json`（鏡頭清單與動作）。先 `--test` 試拍、看總覽圖，再正式擷取（可背景執行，同時做步驟 4、5）。
**檢查點：** 每個鏡頭的關鍵動作都真的發生了、運鏡的起點與終點都好看。

### 4. 配音與時間 → 讀 `references/05-timing-and-sync.md`

用 motion-video 的 `tts.py` 配音（先試一段請使用者聽口音），再用 `align_timeline.py --target <秒數>` 壓長度並把句子對齊真正的停頓。之後所有時間都以這份時間軸為準。

### 5. 建立視覺語言並做動畫 → 讀 `references/04-visual-language.md`、`05-timing-and-sync.md`

**要想清楚：** 這支片的視覺應該長什麼樣子？——答案在產品裡：沿用產品的色票、字型、語意色（例如綠＝正常、紅＝警示），讓觀眾在影片與產品之間看到一致的意義。每個場景要解決什麼「看不懂」的問題？用什麼技巧引導視線？

從 `new_promo.py` 建的骨架開始，**自己設計每個場景**。技巧（推鏡、標註、壓暗、大字、架構圖、數字跳動……）是工具箱，依目的挑選，必要時自己發明新的。

**檢查點：** `render.py --sheet` 每句一張，逐張親眼看（`references/07-review.md`）。

### 6. 聲音設計 → 讀 `references/06-sound-design.md`

**要想清楚：** 音樂的情緒曲線要跟故事一樣——痛點壓抑、產品登場打開、金句時讓出空間、結尾收束。音效只放在真正的轉折點。

### 7. 渲染、混音、成片檢查、交付

```bash
python <MV>/scripts/render.py videos/<名稱> --lang zh --crf 18
python <P>/scripts/mix.py videos/<名稱> --lang zh --max-mb 30
python <P>/scripts/contact_sheet.py video videos/<名稱>/out/<名稱>_zh_final.mp4 --every 4
```
交付時說清楚：長度、大小、哪些是戲劇化／示範內容需要使用者確認、聲音需要使用者親自聽。

---

## 指令速查

```bash
# 環境（第一次）
pip install playwright numpy pillow imageio-ffmpeg && python -m playwright install chromium   # 另需系統 ffmpeg
# 建立影片資料夾（骨架）
python <P>/scripts/new_promo.py videos/<名稱> --mv <MV>
# 擷取
python <P>/scripts/capture.py videos/<名稱>/shots.json --out /tmp/test --test
python <P>/scripts/contact_sheet.py clips /tmp/test
python <P>/scripts/capture.py videos/<名稱>/shots.json --out videos/<名稱>/assets/clips --jobs 2
# 配音與時間
set -a; source ~/.openrouter.env; set +a        # 金鑰只放使用者電腦的隱藏檔，不進專案、不貼對話
python <MV>/scripts/tts.py videos/<名稱> --lang zh [--only s01]
python <P>/scripts/align_timeline.py videos/<名稱> --mv <MV> --target 90 [--refresh s03]
python <MV>/scripts/render.py videos/<名稱> --preview
# 檢查動畫
python <MV>/scripts/render.py videos/<名稱> --sheet          # 或 --stills 12.5,40
# 聲音
python <P>/scripts/apple_loops.py list|beats|convert ...      # Mac
python <P>/scripts/music.py videos/<名稱>/music.json --timeline videos/<名稱>/timeline_zh.json --out videos/<名稱>/bgm.wav
python <P>/scripts/sfx.py   videos/<名稱>/sfx.json   --timeline videos/<名稱>/timeline_zh.json --out videos/<名稱>/sfx.wav
# 輸出
python <MV>/scripts/render.py videos/<名稱> --lang zh --crf 18
python <P>/scripts/mix.py videos/<名稱> --lang zh --max-mb 30
```

## 反模式（看到就停下來重想）

- 把 `examples/cnc-twin` 的場景、台詞、顏色、版面搬過來改字。
- 沒操作過產品就開始寫腳本。
- 台詞講的功能，畫面沒有拍到（或產品根本做不到）。
- 每個場景都用同一招（全部都是「擦入＋左上標籤」）——技巧要服務內容，不同的訊息用不同的表現。
- 一個畫面塞 5 個標籤、兩段字、一個公式。
- 時間寫死秒數；改一次台詞整支片就亂掉。
- 文字壓在亮色畫面上沒有底、壓在產品主體上。
- 沒看總覽圖就渲染成片。
- 把模擬資料講成真實成效、把路線圖講成已上線。

## 參考文件

| 檔案 | 內容 |
|---|---|
| `references/01-product-discovery.md` | 怎麼試用產品、找 money shot、可視性檢查、給改程式建議 |
| `references/02-story-design.md` | 觀眾 → 訊息階層 → 敘事結構 → 節奏 → 台詞；誠實原則 |
| `references/03-shot-design.md` | 從台詞到鏡頭；cine / ui；動作與運鏡；`shots.json` 規格 |
| `references/04-visual-language.md` | 從產品推導視覺；版面、字級、色彩；技巧工具箱與何時用 |
| `references/05-timing-and-sync.md` | 時間模型、對時公式、節奏、骨架 API |
| `references/06-sound-design.md` | 配音、配樂編排、音效、混音 |
| `references/07-review.md` | 自我審查方法與檢查清單 |
| `references/troubleshooting.md` | 常見錯誤與解法 |
| `examples/cnc-twin/CASE-STUDY.md` | 案例：每個決策為什麼這樣做、換成別的產品會怎麼改 |
