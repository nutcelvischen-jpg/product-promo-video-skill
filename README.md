# Product Promo Video Skill：讓 AI Agent 把你的系統做成專業介紹影片

[English](https://github.com/nutcelvischen-jpg/product-promo-video-skill/tree/en) | **繁體中文**

把一個能在瀏覽器打開的產品（網站、儀表板、3D 數位孿生、SaaS 系統）交給 AI，它會：

1. **先試用產品**，找出值得拍的功能、建議哪裡要先改
2. **用行銷公司的結構寫腳本**（痛點 → 產品登場 → 功能 → 情境模擬 → 價值 → 署名）
3. **逐格錄下真實操作畫面**（連 3D / WebGL 都是平順 30fps）
4. **做動態設計**：推鏡、標註、轉場、大字、Logo 片尾
5. **台灣口音 AI 配音**、Apple Loops 配樂、程式合成音效、專業混音
6. 輸出 **1080p MP4**

![preview](docs/preview.jpg)

> 範例：CNC 工廠數位孿生介紹影片（90 秒、企業客戶、片尾 ICMA Lab）— 見 `examples/cnc-twin/`

這是一個 **Agent Skill**（`SKILL.md` 格式），可以在 Google Antigravity、Claude Code 等支援 skills 的 AI 工具中使用。它建立在 [motion-video-skill](https://github.com/nutcelvischen-jpg/motion-video-skill) 之上，**兩個都要裝**。

---

## 一、準備（約 15 分鐘）

需要：**Python 3.9 以上**、**Git**、**ffmpeg**、網路。做配樂需要 **Mac**（使用內建 Apple Loops），沒有 Mac 可以用自己有授權的音樂。

### 1. 安裝兩個 skill

在 Antigravity 開啟你的工作資料夾，打開終端機：
```bash
git clone https://github.com/nutcelvischen-jpg/motion-video-skill .agents/skills/motion-video
git clone https://github.com/nutcelvischen-jpg/product-promo-video-skill .agents/skills/product-promo-video
```
> 英文版：`git clone` 後面加 `-b en`。

### 2. 安裝套件

Mac：
```bash
brew install ffmpeg
pip3 install -r .agents/skills/product-promo-video/requirements.txt
python3 -m playwright install chromium
```
Windows：
```bash
winget install ffmpeg
pip install -r .agents/skills/product-promo-video/requirements.txt
python -m playwright install chromium
```

### 3. 設定配音金鑰（OpenRouter）

到 [openrouter.ai](https://openrouter.ai) → Keys 建立金鑰，**存在自己的電腦，不要貼給 AI、不要放進專案**：
```bash
echo 'OPENROUTER_API_KEY=sk-or-你的金鑰' > ~/.openrouter.env && chmod 600 ~/.openrouter.env
```

---

## 二、使用方式

把產品跑起來（例如 `npm run build && cd dist && python3 -m http.server 8766`），然後對 AI 說：

> 「用 product-promo-video skill，幫我把 http://localhost:8766 這個系統做成 90 秒介紹影片，給企業客戶看，華語，片尾署名 ○○實驗室。」

AI 會依序：試用 → 給你改程式的建議 → 給你看台詞 → 擷取畫面 → 配音 → 動畫 → 配樂 → 輸出。
**台詞確認、改程式建議、成片試聽**這三個地方會停下來問你。

成品在 `videos/<名稱>/out/<名稱>_zh_final.mp4`。

---

## 三、自己動手（想了解每一步）

```bash
P=.agents/skills/product-promo-video; MV=.agents/skills/motion-video
python $P/scripts/new_promo.py videos/demo --mv $MV                       # 建資料夾
# 改 videos/demo/script.json（台詞）、shots.json（鏡頭）
python $P/scripts/capture.py videos/demo/shots.json --out videos/demo/assets/clips --test   # 試拍
python $P/scripts/capture.py videos/demo/shots.json --out videos/demo/assets/clips          # 正式拍
set -a; source ~/.openrouter.env; set +a
python $MV/scripts/tts.py videos/demo --lang zh                             # 配音
python $P/scripts/align_timeline.py videos/demo --mv $MV --target 90       # 對齊＋壓長度
python $MV/scripts/render.py videos/demo --preview                          # 更新時間軸
# 改 videos/demo/index.html（動畫）
python $MV/scripts/render.py videos/demo --sheet                            # 總覽圖檢查
python $P/scripts/music.py videos/demo/music.json --timeline videos/demo/timeline_zh.json --out videos/demo/bgm.wav
python $P/scripts/sfx.py videos/demo/sfx.json --timeline videos/demo/timeline_zh.json --out videos/demo/sfx.wav
python $MV/scripts/render.py videos/demo --lang zh --crf 18                 # 渲染
python $P/scripts/mix.py videos/demo --lang zh                              # 混音＋成片
```

完整說明見 [SKILL.md](SKILL.md)，各主題細節在 `references/`。

---

## 四、這個 skill 的關鍵技術

| 問題 | 解法 |
|---|---|
| 3D 網頁在沒 GPU 的電腦上錄影會卡 | **虛擬時鐘**（`scripts/vt.js`）：接管頁面的時間，一格一格推進再截圖 |
| 操作要跟配音對齊 | 動作固定在第 N 格發生；動畫用 `clip(sel, 台詞時間 - N/30)` 對時 |
| TTS 句子時間不準 | `align_timeline.py` 用靜音偵測對齊真正的停頓 |
| 配樂要跟畫面起落 | `music.py`：強拍對齊產品登場、金句抽鼓、片尾淡出，全部綁旁白時間 |
| 旁白被音樂蓋過 | `mix.py`：側鏈壓縮自動閃避人聲、loudnorm -15 LUFS |

## 授權

MIT。Apple Loops 依 Apple 授權可用於自己的影片作品，但 loop 檔案本身不可再散布（所以本 repo 不附音檔）。
