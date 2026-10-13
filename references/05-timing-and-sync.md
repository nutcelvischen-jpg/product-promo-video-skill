# 05 時間與對時：旁白是時鐘

## 1. 時間模型

```
script.json ──tts.py──▶ audio_<lang>/sNN.wav ──align_timeline.py──▶ timeline_<lang>.json ──render.py --preview──▶ _tl.js
                                                                                │
                                         index.html 用 S(i) / L(i,j) / LM(i,j,k) 讀取它
```
- `align_timeline.py`：把配音整體加速（`atempo`，音高不變）到目標長度，並用靜音偵測把句子邊界吸附到真正的停頓。加速 0.95～1.08 聽不出來；超過 1.12 就該刪台詞。
- 重做某場配音後：`tts.py --only s03` → `align_timeline.py ... --refresh s03`。

## 2. 時間函式（index.html 裡）

| 函式 | 意思 |
|---|---|
| `S(i).start` | 第 i 場開始（0 起算） |
| `L(i, j)` / `LE(i, j)` | 第 i 場第 j 句開始／結束 |
| `LM(i, j, k)` | 第 i 場第 j 句講到 k 比例（0.5 = 一半） |
| `c.TL.total` | 總長 |

**不要寫死秒數。** 改台詞或重做配音，整支片會自動重新對齊。

## 3. 骨架提供的工具

```js
clip(sel, t0, t1, skip = 0)   // 素材：t0 秒顯示第 skip 格，之後每秒 30 格；超過總格數停在最後一格；t1+0.6 秒自動隱藏
cutIn(sel, t, d)              // 擦入轉場
zoomTo(sel, x, y, scale, t, d)// 以 (x,y) 為中心推鏡（座標是原始 1920×1080 畫面）
drift(sel, t, d, s0, s1)      // 整段緩慢推近
fadeIn / fadeOut / pop / words // 淡入、淡出、彈出、大字逐行浮現
```
加上 motion-video `wide` runtime 的 `c.rise`、`c.out`、`c.count`、`c.tilt`、`c.sheen`、`c.wipe`、`c.type`。要什麼效果不夠，就直接寫 `c.m.fromTo(...)`（GSAP 時間軸，第三個參數是時間）。

素材元素：
```html
<div id="c_xxx" class="clip"><img data-clip="xxx" data-n="255" src="assets/clips/xxx/0000.jpg"></div>
```
`data-n` 是該鏡頭的總格數。DOM 越後面越上層，照出現順序排。`tick()` 與最後的 `__seek` 覆寫（等新的一格解碼完才截圖）不要刪。

## 4. 對時公式（最重要）

鏡頭在第 F 格發生動作，想讓動作落在時間 T：
```js
clip(sel, T - F / 30, t1);
```
如果算出來的 t0 比鏡頭出現的時間晚，用 `Math.min(T - F/30, 出現時間)`，避免一開始空白。

T 怎麼選：
- 問句的答案要「被看見」：T 落在問句講完、答句開始的瞬間（約該句的 20～30%）。
- 描述動作的句子（「點一下，就能…」）：T 落在講到動詞的時候。
- 數字變化：數字開始變的時間，比講到數字早 0.2～0.4 秒，觀眾的眼睛會先到。

## 5. 節奏規則

- 元素在「講到它的那句」開始時出現，或早 0.1～0.3 秒。
- 轉場在下一句開始前 0.3～0.4 秒啟動，讓新畫面跟新句子同時到位。
- 收掉上一個 beat 的元素：下一個 beat 開始前 0.3～0.5 秒。
- 句子之間的停頓是給畫面「呼吸」的地方，大動作（推鏡、圓形展開）放在停頓裡效果最好。
- 結尾 Logo 要留 2 秒以上（motion-video 的時間軸結尾預設留 2.6 秒）。

## 6. 預覽與檢查

```bash
python <MV>/scripts/render.py videos/<名稱> --sheet           # 每句結尾一張
python <MV>/scripts/render.py videos/<名稱> --stills 12.5,40  # 指定秒數（檢查轉場中間、動作瞬間）
```
瀏覽器預覽：`index.html?play`（循環）、`?t=12.5`（停格）。
