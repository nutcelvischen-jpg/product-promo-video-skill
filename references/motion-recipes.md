# 動畫招式與對時公式（promo-wide 範本）

範本建立在 motion-video-skill 的 `wide` runtime 上：`c.rise`、`c.out`、`c.count`、`c.tilt`、`c.sheen`、`c.wipe` 這些都能用（見 `<MV>/references/animation-cookbook.md`）。以下是本 skill 加的部分。

## 1. 素材層 `.clip`

```html
<div id="c_power" class="clip"><img data-clip="power" data-n="255" src="assets/clips/power/0000.jpg"></div>
```
- `data-clip` = 鏡頭資料夾名稱，`data-n` = 總格數（`ls assets/clips/power | wc -l`）。
- **DOM 越後面越上層**：照影片出現順序排，後面的鏡頭自然蓋住前面的。
- 可以在 `.clip` 裡加 `.shade`（漸層遮罩）讓左側文字好讀。

```js
clip("#c_power", t0, t1, skip = 0)
```
- t0 秒顯示第 `skip` 格，之後每秒前進 30 格，播完停在最後一格。
- t1 + 0.6 秒自動隱藏（讓下一個鏡頭的擦入轉場有東西墊底）。
- 同一組畫面要在兩個地方用（例如縮圖），寫 `clip("#twin img", ...)` 直接對 img。

`tick()` 負責換圖；最後的 `__seek` 覆寫負責「等新圖解碼完才截圖」——**兩段都不要刪**。

## 2. 對時公式（最重要）

鏡頭在第 F 格發生動作，想讓動作落在時間 T：
```js
clip(sel, T - F / 30, t1);
```
例：雲層遮蔽在第 30 格按下，想讓它落在「天氣轉陰？」問句講完（大約該句 22% 處）：
```js
clip("#c_cloud", LM(4, 0, .22) - 1.0, L(4, 1) + .3);
```
若算出的 t0 比畫面出現時間還晚，用 `Math.min(..., 出現時間)`，避免一開始顯示空白。

## 3. 轉場

| 招式 | 程式 | 用在 |
|---|---|---|
| 擦入 | `cutIn(sel, t, .8)` | 鏡頭與鏡頭之間（主要轉場），在下一句開始前 0.35 秒 |
| 圓形展開 | `m.fromTo(sel,{clipPath:"circle(0% at 66% 50%)"},{clipPath:"circle(120% at 66% 50%)",duration:1.6,ease:"expo.inOut"},t)` | 產品第一次登場 |
| 淡入淡出 | `fadeIn` / `fadeOut` | 片頭片尾、暗場 |
| 閃光 | `fadeIn("#flash", t, .2); fadeOut("#flash", t+.2, 1)` | 片名、Logo 出現瞬間（搭配 boom 音效） |
| 暗場 | `fadeIn("#dimAll", t)` | 要打大字之前，壓暗並模糊後面的畫面 |

## 4. 鏡頭運動

| 招式 | 程式 | 說明 |
|---|---|---|
| 推鏡到面板 | `zoomTo(sel, x, y, 1.85, t, 1.6)` | (x, y) 是原始 1920×1080 截圖上的點；縮放以該點為中心。點選後 0.5 秒開始推 |
| 慢推 | `drift(sel, t, d, 1.05, 1.18)` | 電影鏡頭整段緩慢放大，靜止畫面也有呼吸感 |
| 再構圖 | `m.fromTo(sel+" img",{x:330},{x:0,...})` | 左邊要放文字時把 3D 主體推到右邊，文字收掉再回中間 |
| 瀏覽器框 | `c.tilt("#win", t)` + 內放 `<img data-clip="ui">` | 第一次秀完整介面時，用 3D 傾斜浮入，比全螢幕更有「產品感」 |

量面板座標：用 `--test` 拍出的 JPG，在看圖軟體看游標座標；或用 Python `Image.open(...).crop(...)` 試。

## 5. 文字

| 元件 | HTML | 動畫 |
|---|---|---|
| 痛點卡＋數字跳動 | `.card.glass` 內 `.big` | `c.rise` + `c.count(sel,0,1284600,t,2.2,fmt)` |
| 問題膠囊 | `.tag`（`.amber/.blue/.coral` 換點點顏色） | `pop(sel, LM(i,j,.02/.36/.68))` 跟著問句逐一出現 |
| 大字（兩行） | `.kin > .w × 2` | `words(sel, t, .45)`：逐行從模糊浮現 |
| 場景標籤 | `.tag` 左上 `left:72px;top:170px` | `pop`，下一句前 `c.out` |
| 標註 | `.callout > .lb > small` | 推鏡後從左滑入，搭配 `#coShade` 左側壓暗 |
| 公式卡 | `.card.glass > .eb + .eq + .foot` | `c.rise` + `c.sheen`；示範係數要寫在 `.foot` |
| KPI 三卡 | `.tc.glass × 3`（含 `.bar2 i` 進度條） | `c.rise(".tc")` + 長條 + sheen |
| 架構圖 | SVG path + `tick()` 光點沿 path 流動 | 見 `examples/cnc-twin/index.html` 的 `#iot` |
| Logo 片尾 | `#logo`（name / cn / line / tl / ft） | 模糊放大浮現 → 線條展開 → 標語 → 免責小字 |

## 6. 版面規則

- 上方 140px 是品牌列（runtime 自動放 brand / event），下方 160px 是字幕，重要東西放中間。
- 同時最多 3 個重點元素；換句就收掉上一句的標籤（`c.out(sel, L(i,j+1) - .35)`）。
- 文字壓在畫面上時，一定要有底：`.shade` 漸層、`#coShade`、`.card` 深色底（不要用半透明玻璃壓在亮色 3D 地板上）。
- `.glass` 自帶 `position:relative`，**絕對定位的卡片一定要 `position:absolute!important`**（範本 `.card` 已處理）。
- `#title`、`#logo` 這類沒有 `.abs` class 的容器要自己寫 `position:absolute`。
- 3D 主體跟大字不要重疊：用 `x` 位移或把字放另一側。

## 7. 顏色

- 直接沿用產品 UI 的語意色（例：綠＝運轉／主要、琥珀＝太陽能、藍＝電力、珊瑚紅＝故障／碳排），觀眾在影片跟產品裡看到的意義一致。
- `--gold` 是 runtime 的重點色變數，設成產品主色；`--glow-rgb` 決定背景光點顏色。
